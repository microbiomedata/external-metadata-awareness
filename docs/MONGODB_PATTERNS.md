# MongoDB Patterns

Comprehensive guide to MongoDB patterns in this repository. Covers Python connections, JavaScript aggregations, Makefile integration, and when to use which approach.

For JS execution methods and script header conventions, see [DEVELOPMENT.md](DEVELOPMENT.md#mongodb-javascript-patterns).

Related issues: [#176](https://github.com/microbiomedata/external-metadata-awareness/issues/176) (connection unification), [#237](https://github.com/microbiomedata/external-metadata-awareness/issues/237) (atomic counting), [#240](https://github.com/microbiomedata/external-metadata-awareness/issues/240) (atomic transformations), [#282](https://github.com/microbiomedata/external-metadata-awareness/issues/282) (naming conventions).

---

## Python Connection Patterns

### `get_mongo_client()` — the standard connection factory

All Python scripts that connect to MongoDB should use the utility in `external_metadata_awareness/mongodb_connection.py`:

```python
from external_metadata_awareness.mongodb_connection import get_mongo_client

client = get_mongo_client(
    mongo_uri="mongodb://localhost:27017/ncbi_metadata",
    env_file="local/.env",   # optional — loads MONGO_USER/MONGO_PASSWORD
    debug=True
)
db = client.get_default_database()
```

The function validates the URI (must include a database name), optionally loads credentials from `.env`, and injects them into the URI.

### Standard Click options

Python CLI tools use two patterns:

**Minimal** (`mongo_js_executor.py` and similar):
```python
@click.option('--mongo-uri', required=True, help='MongoDB URI')
@click.option('--env-file', help='Path to .env file')
@click.option('--verbose', is_flag=True)
```

**Full** (`insert_all_flat_gold_biosamples.py` and similar — includes auth and collection params):
```python
@click.option('--mongo-uri', default=None, help='MongoDB URI (overrides host/port/db)')
@click.option('--mongo-host', default=None, help='MongoDB host')
@click.option('--mongo-port', default=None, type=int, help='MongoDB port')
@click.option('--mongo-username', default=None, help='MongoDB username')
@click.option('--mongo-password', default=None, help='MongoDB password')
@click.option('--mongo-auth-source', default=None, help='MongoDB auth source')
@click.option('--db-name', default=None, help='MongoDB database name')
@click.option('--dotenv-path', default='local/.env', help='Path to .env file')
```

The full pattern also includes collection name options (`--source-collection`, `--target-collection`, etc.) specific to each script.

### Environment variables

Credentials are loaded from `.env` files (never hardcoded), but different scripts use different variable names:

- **`get_mongo_client()`-based scripts**: Read `MONGO_USER` / `MONGO_PASSWORD` from `.env` and inject them into the provided `mongo_uri`. Does **not** read `MONGO_HOST` / `MONGO_PORT` / `MONGO_DB` — it requires a full URI with database name.
- **Full-option CLIs** (e.g., `insert_all_flat_gold_biosamples.py`): Read `MONGO_USERNAME` / `MONGO_PASSWORD` for auth, and `MONGO_HOST` / `MONGO_PORT` / `MONGO_DB` to construct a URI when `--mongo-uri` is not provided.

---

## Makefile Patterns

### `mongo-js-executor` for all JS aggregation scripts

Every Makefile target that runs a `mongo-js/` script uses this pattern:

```makefile
flatten_bioprojects: mongo-js/flatten_bioprojects_minimal.js
	date && time $(RUN) mongo-js-executor \
		--mongo-uri "$(MONGO_URI)" \
		$(ENV_FILE_OPTION) \
		--js-file mongo-js/flatten_bioprojects_minimal.js \
		--verbose && date
```

- `$(RUN)` = `poetry run`
- `$(MONGO_URI)` = `mongodb://$(MONGO_HOST):$(MONGO_PORT)/$(MONGO_DB)` (defaults to `localhost:27017/ncbi_metadata`)
- `$(ENV_FILE_OPTION)` = `--env-file $(ENV_FILE)` when `ENV_FILE` is set, empty otherwise
- `date && time ... && date` wraps every target for timing

### Inline `mongosh` — only for one-liners

Use inline `mongosh --eval` only for simple operations that don't warrant a script file:

```makefile
drop-temp-collections:
	mongosh "$(MONGO_URI)" --eval "db.getCollection('__tmp_hn_accessions').drop()"
```

For anything with an aggregation pipeline, use a `.js` file + `mongo-js-executor`.

### Standard Makefile variables

```makefile
MONGO_HOST ?= localhost
MONGO_PORT ?= 27017
MONGO_DB ?= ncbi_metadata
MONGO_URI ?= mongodb://$(MONGO_HOST):$(MONGO_PORT)/$(MONGO_DB)
```

---

## Python vs JavaScript — When to Use Which

| Use JavaScript (`mongo-js/`) | Use Python (`external_metadata_awareness/`) |
|---|---|
| MongoDB aggregation pipelines | External API calls (GOLD, NCBI, BioPortal) |
| Collection-to-collection transforms (`$out`) | Complex data manipulation (pandas, numpy) |
| Index creation | Ontology lookups (OAK) |
| Simple counting / reporting | CLI tools with Click |
| Temp collection management | Anything needing quantulum3, dateparser, geopy |

**Rule of thumb**: If the operation is purely MongoDB → MongoDB, use JavaScript. If it needs Python libraries or external data, use Python.

---

## Atomic Transformation Principles

From [#240](https://github.com/microbiomedata/external-metadata-awareness/issues/240): MongoDB transformations should be atomic, resumable, and small.

### Requirements

1. **Single responsibility**: One script creates one output collection from one or two input collections.
2. **Idempotent**: Running a script twice produces the same result. Aggregation pipelines use `$out` to atomically replace their target; loader/report scripts that use `drop()` + `insertMany()` must also be written so a rerun leaves the collection in the same final state.
3. **Skip if complete**: Scripts should check if the output collection already has the expected document count before running. (Not yet implemented in all scripts — tracked in [#254](https://github.com/microbiomedata/external-metadata-awareness/issues/254).)
4. **Progress reporting**: Log timestamps at start, finish, and at intermediate milestones for long operations.
5. **Small file size**: Keep scripts under 5K when possible. If a script exceeds that, document why in a comment.

### Temp collection conventions

- Prefix with `__tmp_` (double underscore) or `temp_`
- **Important**: `mongosh` interprets `db.__tmp_foo` as a private property. Use `db.getCollection('__tmp_foo')` instead:

```javascript
// ✅ Correct
db.getCollection('__tmp_hn_accessions').aggregate([...]);

// ❌ Fails silently in mongosh
db.__tmp_hn_accessions.aggregate([...]);
```

- Always drop temp collections in a dedicated cleanup step
- Name cleanup scripts with a `_cleanup` or step-number suffix (e.g., `step2d`)

---

## Aggregation Pipeline Conventions

All aggregation scripts live in `mongo-js/` and follow a common structure:

```javascript
db.source_collection.aggregate([
    { $project: { /* extract/compute fields */ } },
    { $group:   { _id: "$key", /* accumulate */ } },
    { $project: { /* reshape, compute $size of sets */ } },
    { $addFields: { /* derived metrics (percentages, ratios) */ } },
    { $project: { /* remove temporary fields */ } },
    { $sort:    { key: 1 } },
    { $out:     "target_collection" }
], { allowDiskUse: true });
```

### Key rules

- **Always use `allowDiskUse: true`** for any aggregation over >1M documents.
- **`$out` replaces the entire target collection atomically on success.** There is no upsert/merge mode — MongoDB writes results to a temporary collection and swaps it into place only if the pipeline completes successfully. If the pipeline fails, the previous collection remains unchanged and you must re-run to produce new output.
- **`$addToSet` has a 100MB memory limit per group.** For high-cardinality grouping (e.g., counting unique biosamples per harmonized_name across 756M attributes), use multi-step workflows instead.

---

## Multi-Step Workflows

When a single aggregation would exceed memory limits, break it into steps with intermediate temp collections.

### Pattern: deduplicate → aggregate → join → cleanup

Example: counting unique bioprojects per harmonized_name (`count_bioprojects_step2a` through `step2d`):

1. **Step 2a**: Deduplicate `harmonized_name + accession` pairs from `biosamples_attributes` → `__tmp_hn_accessions`
2. **Step 2b**: Create index on temp collection for fast lookup
3. **Step 2c**: Join temp collection with `sra_biosamples_bioprojects`, count unique bioprojects → `temp_bioproject_counts`
4. **Step 2d**: Drop `__tmp_hn_accessions`

### Conventions

- Temp collections use `__tmp_` or `temp_` prefix
- Each step is a separate `.js` file named with a step number suffix
- Cleanup steps explicitly drop temp collections
- Steps must run sequentially — the Makefile enforces ordering

---

## Collection Creation Pattern

Most `mongo-js/` scripts follow this lifecycle:

1. Log start time and source collection size
2. Run aggregation pipeline with `$out` (implicitly drops + recreates target)
3. Count documents in output collection
4. Create indexes on key fields
5. Log completion with summary statistics

```javascript
print("[" + new Date().toISOString() + "] Starting...");
const totalDocs = db.source.estimatedDocumentCount();
print("[" + new Date().toISOString() + "] Processing ~" + totalDocs.toLocaleString() + " documents...");

db.source.aggregate([ /* pipeline */ ], { allowDiskUse: true });

const outputCount = db.target.countDocuments();
print("[" + new Date().toISOString() + "] Created " + outputCount.toLocaleString() + " documents");

db.target.createIndex({ key_field: 1 }, { unique: true });
```

---

## Indexing Strategy

### When to create indexes

- **Always** on output collections after `$out` — the new collection has no indexes
- **On temp collections** if a subsequent step will query them (e.g., step 2b above)
- **Unique indexes** on the primary key of statistics/report collections (e.g., `harmonized_name`)

### Index conventions in this repo

| Collection | Indexes | Notes |
|---|---|---|
| `biosamples` | `accession` | Primary lookup key |
| `biosamples_attributes` | `harmonized_name + accession`, `attribute_name + harmonized_name`, `unit + harmonized_name` | Compound indexes for aggregation performance |
| `biosamples_flattened` | `accession` | Primary lookup key |
| `env_triads_flattened` | `accession + component` | Compound for per-biosample lookups |
| `harmonized_name_*` stats collections | `harmonized_name` (unique) | One doc per field name |

### Background indexing

Use `{ background: true }` for indexes on collections >1M documents to avoid blocking other operations:

```javascript
db.biosamples_attributes.createIndex({harmonized_name: 1}, {background: true});
```

---

## Skip Logic

Several scripts filter out harmonized_names that are known to produce noise in measurement/unit analysis. The skip list is maintained as an array in the aggregation scripts themselves (not in a separate collection).

### How it works

The `measurement_results_skip_filtered` collection is produced by filtering `content_pairs_aggregated` through a skip list of ~224 harmonized_names that contain free-text descriptions, identifiers, or categorical values rather than measurements.

Downstream collections (`harmonized_name_dimensional_stats`, `measurement_evidence_percentages`) operate on the filtered collection, so skip list changes propagate by re-running the pipeline from the filter step forward.

### Adding to the skip list

1. Identify the harmonized_name producing false positives in measurement parsing
2. Add it to the skip list array in the relevant script
3. Re-run from the filter step (not the full pipeline)

---

## `$out` vs Manual Insert

Aggregation-based build scripts in this repo use `$out` for collection creation (not `insertMany` or `bulkWrite` from aggregation results). This means:

- **Atomic replacement**: target is fully replaced on each run
- **No incremental updates**: partial results require full re-runs
- **Idempotent**: running the same script twice produces the same output (assuming source data hasn't changed)

This is intentional — these aggregation pipelines are designed for full rebuilds, not incremental updates. Separately, some loader scripts (`load_global_mixs_slots.js`, `load_global_nmdc_slots.js`) drop a collection and repopulate it via `insertMany`.

---

## Database Inheritance

Production aggregation scripts inherit the database from the `mongosh` connection URI and should not call `db.getSiblingDB()` or hardcode database names. (Some utility scripts in `mongo-js/prints_does_not_insert/` do use `getSiblingDB` to enumerate across databases — that's acceptable for read-only reporting.)

```bash
# Database comes from URI — script uses whatever `db` points to
poetry run mongo-js-executor \
  --mongo-uri "mongodb://localhost:27017/ncbi_metadata" \
  --js-file mongo-js/your_script.js
```

This allows the same scripts to run against different database instances without modification.

---

## Naming Conventions

| Pattern | Example | Meaning |
|---|---|---|
| `*_flattened` | `biosamples_flattened` | Flat version of a nested source collection |
| `*_stats` | `harmonized_name_usage_stats` | Aggregated statistics |
| `*_counts` | `unit_assertion_counts` | Simple frequency counts |
| `__tmp_*` / `temp_*` | `__tmp_hn_accessions` | Intermediate collections (should be cleaned up) |
| `*_skip_filtered` | `measurement_results_skip_filtered` | Filtered subset with noise removed |

---

## Common Pitfalls

1. **Forgetting `allowDiskUse`**: Aggregations over large collections silently fail or produce incomplete results without it.
2. **`$out` to the source collection**: Never `$out` to the same collection you're reading — this can corrupt the pipeline.
3. **Missing indexes after `$out`**: `$out` replaces the target with a new collection that has no indexes. Always recreate indexes after.
4. **`$addToSet` memory**: Collecting millions of unique values into a set per group exceeds the 100MB limit. Use multi-step deduplication instead.
5. **Assuming `estimatedDocumentCount` is exact**: It uses collection metadata and can be stale after bulk operations. Use `countDocuments({})` when precision matters.

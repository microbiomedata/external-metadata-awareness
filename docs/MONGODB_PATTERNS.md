# MongoDB Patterns

Patterns and conventions used in this repository's MongoDB operations. For execution methods and JS script headers, see [DEVELOPMENT.md](DEVELOPMENT.md#mongodb-javascript-patterns).

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
- **`$out` replaces the entire target collection.** There is no upsert/merge mode — the previous collection is dropped atomically. A partial failure means the old data is gone and you must re-run.
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

This repo exclusively uses `$out` for collection creation (not `insertMany` or `bulkWrite` from aggregation results). This means:

- **Atomic replacement**: target is fully replaced on each run
- **No incremental updates**: partial results require full re-runs
- **Idempotent**: running the same script twice produces the same output (assuming source data hasn't changed)

This is intentional — the pipeline is designed for full rebuilds, not incremental updates.

---

## Database Inheritance

Scripts inherit the database from the `mongosh` connection URI. They never call `db.getSiblingDB()` or hardcode database names.

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
2. **`$out` to the source collection**: Never `$out` to the same collection you're reading — this drops the source mid-pipeline.
3. **Missing indexes after `$out`**: `$out` creates a new collection with no indexes. Always recreate indexes after.
4. **`$addToSet` memory**: Collecting millions of unique values into a set per group exceeds the 100MB limit. Use multi-step deduplication instead.
5. **Assuming `estimatedDocumentCount` is exact**: It uses collection metadata and can be stale after bulk operations. Use `countDocuments({})` when precision matters.

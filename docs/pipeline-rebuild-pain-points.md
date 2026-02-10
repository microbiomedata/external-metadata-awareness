# Pipeline Rebuild Pain Points

Documented during full clean-slate rebuild on 2026-02-05 through 2026-02-08.
Source data: 51.7M biosamples, 1M bioprojects (up from ~3M biosamples in previous builds).

## SRA Data Required Earlier Than Expected

- `count-bioprojects-step2c` (measurement discovery phase 0) fails if `sra_biosamples_bioprojects` is empty
- SRA loading lives in `sra_metadata.Makefile`, completely separate from `measurement_discovery.Makefile`
- Nothing in the measurement discovery Makefile or its docs mentions this dependency
- The step 2c script has a guard that catches the error cleanly, but by that point steps 1, 2a, and 2b have already run (~3+ hours on 51M biosamples)
- **Recommendation**: Document SRA as a prerequisite at the top of `measurement_discovery.Makefile`. Consider adding a pre-flight check before step 1 that warns if SRA is empty.

## `process-measurements` Target Lives Only in `test_workflow.Makefile`

- `process-measurements` exists as a meta-target but only in `test_workflow.Makefile` (which includes other Makefiles)
- Running `make -f Makefiles/measurement_discovery.Makefile process-measurements` fails with "No rule to make target"
- The production measurement discovery pipeline requires 4 separate make invocations in order:
  1. `count-biosamples-and-bioprojects-per-harmonized-name`
  2. `count-measurement-evidence`
  3. `run-measurement-discovery`
  4. `count-attribute-harmonized-pairings calculate-measurement-percentages create-dimensional-stats load-global-mixs-slots load-global-nmdc-slots report-nmdc-range-slot-usage`
- **Recommendation**: Add a `process-measurements` (or similar) meta-target to `measurement_discovery.Makefile` itself, not just the test workflow.

## Very Long Steps With No Progress Indication

- Step 2c (`$lookup` joining 465M temp records against 33.7M SRA pairs) ran for **12+ hours** with zero output
- The script comment says "may take 20-40 min" — calibrated for ~3M biosamples, not 51M
- Multiple mongo-js aggregation scripts run 30-90+ minutes silently
- The only way to check if MongoDB is working or stuck requires using monitoring techniques from a separate shell
- **Recommendation**: Update time estimates for current data volumes. Add periodic progress logging where feasible. Document monitoring techniques (see below).

### Monitoring Long-Running Pipeline Steps

When a pipeline step appears to hang, use these techniques from a **separate terminal** or from **MongoDB Compass**.

#### From another shell: Check if MongoDB is actively working

```bash
# See all active operations, including the running aggregation's elapsed time and plan
mongosh --quiet --eval "db.getSiblingDB('ncbi_metadata').currentOp({active: true}).inprog.forEach(op => { if (op.secs_running > 5) print(JSON.stringify({ns: op.ns, op: op.op, secs: op.secs_running, yields: op.numYields, plan: op.planSummary}, null, 2)) })"
```

Key fields to watch:
- **`secs_running`**: Confirms the operation is still alive (vs. a dead connection)
- **`numYields`**: If this number increases between checks, MongoDB is making progress
- **`planSummary`**: `COLLSCAN` means full collection scan (expected for large aggregations); `IXSCAN` means index-assisted

```bash
# Quick pulse check: run this twice a minute apart. If numYields increases, it's working.
mongosh --quiet --eval "db.getSiblingDB('ncbi_metadata').currentOp({active: true}).inprog.filter(op => op.secs_running > 10).forEach(op => print('yields=' + op.numYields + ' secs=' + op.secs_running + ' ns=' + op.ns))"
```

#### From another shell: Poll output collection size

For aggregations that write to a new collection via `$out`, you can poll the target collection. Note that `$out` writes atomically at the end, so the count may stay at 0 until completion — but for `$merge` or Python-based steps, this works well.

```bash
# Poll every 30 seconds (Ctrl-C to stop)
while true; do
  echo "$(date): $(mongosh --quiet --eval "db.getSiblingDB('ncbi_metadata').TARGET_COLLECTION.estimatedDocumentCount()")"
  sleep 30
done
```

Replace `TARGET_COLLECTION` with the expected output collection name:
- `unit_assertion_counts` (during count-unit-assertions)
- `mixed_content_counts` (during count-mixed-content)
- `measurement_results_skip_filtered` (during run-measurement-discovery)
- `content_pairs_aggregated` (during run-measurement-discovery with --save-aggregation)
- `temp_bioproject_counts` (during count-bioprojects-step2c)

#### From MongoDB Compass

- Open the **Performance** tab to see real-time read/write ops, network I/O, and memory usage
- Open the target output collection and click **Refresh** periodically to watch document count grow (for non-`$out` operations)
- Use the **Explain Plan** feature on a query to understand whether indexes are being used

#### From Activity Monitor (macOS)

- Look for the `mongod` process — high CPU usage confirms it's actively processing
- Check memory pressure — if macOS is swapping heavily, the pipeline will be much slower

## Stale Downloaded Files Silently Reused

- `downloads/biosample_set.xml.gz` from September 2025 was reused by Make (file existed, target satisfied)
- User had to manually `rm -rf downloads/*` to force fresh downloads
- `make purge` (in `ncbi_metadata.Makefile`) only cleans biosample files, not bioprojects, SRA, or schema files
- **Recommendation**: Add a `purge-all` target that cleans all downloaded and derived files across all Makefiles. Document that `rm -rf downloads/*` is needed for a true clean slate.

## No Single Entry Point for Full Production Pipeline

- No `make rebuild-all` or `make full-pipeline` target for production
- The correct order must be known in advance: `ncbi_metadata` → `sra_metadata` → `ncbi_schema` → `env_triads` → `measurement_discovery`
- `test_workflow.Makefile` has `run-full-workflow` for the 1% sample, but there's no production equivalent
- **Recommendation**: At minimum, document the full ordered sequence prominently. Consider a production meta-Makefile.

## Time Estimates Stale for Current Data Volumes

- Comments throughout the codebase reference runtimes for ~3M biosamples / ~44M attributes
- At 51.7M biosamples / 756M attributes, actual times are 5-15x longer
- Step 2c comment: "20-40 min" → actual: 12+ hours
- Step 1: "30-60 min" → actual: 77 min
- `flatten_biosample_attributes`: actual 3h46m for 756M docs
- `count_unit_assertions`: actual 3.4 hours (12,289 sec) — dominated by index creation on 756M docs
- `count_mixed_content`: actual 2.5 hours (8,892 sec) — `harmonized_name` index reused from prior step
- `count_attribute_harmonized_pairings`: actual 1.8 hours (6,623 sec) — another index build on 756M docs
- `run-measurement-discovery` (quantulum3): 27 min for 2.88M content values — fast once aggregation phase completed
- **Recommendation**: Update comments to reflect current data volumes, or express estimates as a function of collection size.

### Actual Rebuild Timeline (51.7M biosamples, Intel MacBook Pro, Feb 2026)

| Step | Duration | Notes |
|---|---|---|
| Download biosample XML (3.5 GB) | ~2 min | NCBI FTP |
| Gunzip biosample XML | ~9 min | |
| Load biosamples into MongoDB | ~overnight | 51.7M docs |
| Download + load bioprojects | ~2 hours | 1M docs, ran concurrently |
| Flatten biosample attributes | 3h 46m | 756M output docs |
| Flatten biosamples_ids, links, bioprojects | ~30 min | |
| Flatten biosamples (biosamples_flattened) | ~2 hours | 51.7M docs |
| Env triads pipeline (env-triads target) | ~9 hours | Includes OAK/OLS/BioPortal annotation |
| Flatten env triads | ~1 hour | 20.7M docs |
| Download + load SRA parquet from S3 | ~15 min | 9.6 GB, 33.7M pairs |
| count-biosamples-and-bioprojects (Phase 0) | ~15 hours | Step 2c join dominated by 465M doc lookup |
| count-measurement-evidence (Phase 1) | ~6 hours | Index creation on 756M docs |
| run-measurement-discovery (Phase 2) | ~2 hours | Aggregation + quantulum3 parsing |
| Phase 3 stats & reports | ~3 hours | More index builds on 756M docs |
| NCBI schema (attributes + packages) | ~10 sec | Tiny XML files |
| **Total wall clock** | **~3-4 days** | With overnight runs and interruptions |

## Inline Index Creation on Large Collections

- Several mongo-js scripts create indexes on `biosamples_attributes` (756M docs) as a first step before running their aggregation
- `count_unit_assertions.js` creates 3 indexes: `{unit: 1}`, `{harmonized_name: 1}`, `{unit: 1, harmonized_name: 1}`
- `count_mixed_content.js` creates 2 indexes: `{content: 1}`, `{harmonized_name: 1}`
- Building each index on 756M docs takes 1-2+ hours
- The scripts produce no output during index creation — they appear hung for hours
- The `msg` field in `db.currentOp()` shows index build progress (e.g., "inserting keys from external sorter into index: 726743864/756112544 96%") but this requires manual monitoring
- If the `harmonized_name` index already exists from a prior script, MongoDB skips it — so running `count_unit_assertions` first saves time for `count_mixed_content`
- **Recommendation**: Create all needed indexes on `biosamples_attributes` in a single preparatory Makefile target before running any measurement discovery steps. This would make index creation explicit, observable, and non-redundant. Also consider persisting indexes across rebuilds by separating index creation from aggregation scripts.

## Reboot Before Long Exports

During the Feb 2026 rebuild, `mongoexport` of `biosamples_flattened` (51.7M docs × 39 fields) ran at dramatically different speeds before and after a macOS reboot:

- **Before reboot**: appeared to run for 8+ hours reaching only ~17% (per stale terminal output)
- **After reboot**: 1% per ~27 seconds, completing the full export in under an hour

The machine had been running multi-day pipeline steps continuously. Memory pressure, swap usage, or MongoDB cache fragmentation likely degraded `mongoexport` throughput. A reboot cleared all of this.

**Recommendation**: If a long `mongoexport` or aggregation seems unusually slow, check Activity Monitor for memory pressure and swap usage. A reboot before multi-hour export steps is cheap insurance.

### Caution: AI time estimates from terminal screenshots

During this same incident, an AI assistant (Claude) produced wildly wrong time estimates (ranging from 5 hours to 50 hours to 34 minutes for the same operation) due to:

1. **Stale screenshots**: The user pasted an old screenshot and the AI built estimates on obsolete data without questioning freshness
2. **Timezone confusion**: `mongoexport` timestamps use local time with UTC offset (e.g., `-0500`), while other tools may report UTC. The AI misread the timestamp format and conflated hours with minutes
3. **Confident wrong answers**: The AI presented each wrong estimate with false confidence, then "corrected" to a different wrong answer, compounding distrust

**Lesson**: Treat AI-generated time estimates with skepticism, especially when derived from screenshots. Direct measurement (timing 1% of progress yourself) is more reliable than asking an AI to extrapolate from terminal output.

## macOS Sleep Can Kill Overnight Runs

- macOS will sleep even when plugged into power, terminating long-running processes
- `caffeinate -s` is required but not documented anywhere in the repo
- **Recommendation**: Document `caffeinate -s` (macOS) as a prerequisite for pipeline runs. Consider wrapping long Make targets with caffeinate.

## Post-Pipeline Steps (Not in Makefiles)

After all Makefile targets complete, these manual steps are needed:

### Provenance notes collection

The NUC database has a `notes` collection with provenance metadata documenting how derived collections were created (source collection, date ranges, sampling parameters, etc.). This is not created by any Makefile target.

Example document:
```json
{
  "collection": "biosamples_sample_1pct",
  "created_at": "2026-01-26T20:58:14.525Z",
  "sample_size": 490490,
  "source_collection": "biosamples",
  "max_biosample_either_date": "2025-10-08T10:30:56.120",
  "note": "1% random sample from biosamples"
}
```

After a rebuild, insert a note documenting the source data vintage:
```javascript
db.notes.insertOne({
  collection: "biosamples",
  created_at: new Date().toISOString(),
  source_file: "biosample_set.xml.gz",
  download_date: "YYYY-MM-DD",
  total_biosamples: db.biosamples.estimatedDocumentCount(),
  total_bioprojects: db.bioprojects.estimatedDocumentCount(),
  note: "Full rebuild from NCBI FTP"
})
```

**Recommendation**: Formalize this as a Makefile target (e.g., `record-provenance`) so it's part of the pipeline rather than a manual step.

### NUC-only collections: investigation results

These collections exist on the NUC but are not produced by the standard pipeline. **All three non-test collections are orphaned** — created but never consumed by any downstream step.

#### Safe to skip (superseded)

- **`harmonized_name_biosample_counts`** (791 docs) — Created by older 3-step atomic scripts (`count_biosamples_per_hn_step1/2/3.js`). **Superseded by `harmonized_name_usage_stats`**, which has identical doc count and is actively used by `calculate-measurement-percentages`. The old Makefile target `count-biosamples-per-harmonized-name-atomic` is dead code.

- **`biosamples_attribute_name_counts_flat_gt_1`** (2,453 docs) — Created by `count_harmonizable_biosample_attribs.js` (not in active pipeline). Groups by (attribute_name, harmonized_name) pairs with counts. **Superseded by `attribute_harmonized_pairings`**, which covers the same mapping space and is part of the measurement discovery Phase 3.

#### Optional (no replacement, but trivially reproducible)

- **`biosample_package_usage`** (210 docs) — Created by `aggregate-biosample-package-usage` target in `ncbi_metadata.Makefile`. Simple aggregation: groups `biosamples_flattened` by `package_content`, counts per package. Nothing reads from it. Recreate if needed:
  ```bash
  make -f Makefiles/ncbi_metadata.Makefile aggregate-biosample-package-usage
  ```

#### Test artifacts (do not recreate)

- `biosamples_sample_1pct` — 1% test sample (created by test_workflow.Makefile)
- `ncbi_biosamples_20251008_1pct` — dated test sample from October 2025

#### Dead code to clean up

The Makefile `measurement_discovery.Makefile` still has targets for the old `harmonized_name_biosample_counts` workflow (`count-biosamples-per-harmonized-name-atomic`, `count-biosamples-per-hn-step1/2/3`) alongside the current `count-biosamples-and-bioprojects-per-harmonized-name`. The old targets should be removed or clearly marked as deprecated to avoid confusion.

## DuckDB Export and NERSC Distribution

### Current state (post-rebuild, Feb 2026)

The NERSC portal (`https://portal.nersc.gov/project/m3408/biosamples_duckdb/`) hosts DuckDB and Parquet exports from the **old 3M-biosample subset** (Sep/Oct 2025). That subset was intentionally filtered to triad-complete biosamples with 2017+ collection dates, to align with Google Earth Satellite Embedding V1 Annual temporal coverage. The full 51.7M corpus has never been exported to DuckDB or uploaded to NERSC.

### Two distinct use cases

1. **Full-corpus analytical DuckDB** — all 51.7M biosamples, 16 flat collections. For general querying and analysis. Produced by `make -f Makefiles/ncbi_to_duckdb.Makefile make-database`.
2. **Curated embeddings subset** — ~3M triad-complete, 2017+ samples with Google Earth satellite embeddings and ENVO ontology embeddings. Lives in `env-embeddings/` on NERSC as CSVs/TSVs. Neither replaces the other.

### NERSC portal structure

```
biosamples_duckdb/
├── ncbi/           ← Monolithic DuckDB + zip (3M subset, Sep 2025)
├── gold/           ← GOLD API + Excel DuckDB snapshots
├── nmdc/           ← NMDC API DuckDB, one with embeddings
├── env-embeddings/ ← Google Earth satellite + ENVO embeddings (CSVs/TSVs)
├── parquet/        ← Per-table Parquet exports (16 files = 16 flat collections)
│   └── ncbi_parquet/  ← Individual .parquet files, one per flat collection
└── old/            ← Historical snapshots (2024-09, 2024-11, 2025-01)
```

### Automation gaps

- ~~**Parquet export**: `export_duckdb_tables_to_parquet.py` exists on NERSC in `parquet/` but is not in the repo.~~ **Fixed (Feb 2026)**: `export_duckdb_to_parquet.py` added to repo as a Click CLI script. Makefile targets: `export-parquet` and `export-all` (DuckDB + Parquet in one step).
- **NERSC upload**: Currently manual `scp`/`rsync`. No Makefile target.
- **Embeddings subset pipeline**: The `satisfying_biosamples` SQL + normalization targets exist in `ncbi_to_duckdb.Makefile`, but the full flow from normalized CSV → coordinate extraction → Google Earth API → integrated embeddings file is not automated.

### Local file cleanup guidance

After a rebuild, these files in `local/` are safe to delete:

- `ncbi_duckdb_export/*.json` — intermediate JSON exports from `mongoexport`, only needed during DuckDB creation. The `make-database` target's space-optimized mode deletes these automatically.
- `ncbi_duckdb_export/*.duckdb` from prior eras — if the corresponding files are on NERSC.
- `sra_metadata_parquet/` (23GB) — re-fetchable from S3 in ~15 min.
- `mongo_dumps/` — old mongodump backups, superseded by fresh MongoDB.

**Keep**: `sra.duckdb` (670MB) — produced during SRA loading, used by `sra_metadata.Makefile`.

**Recommendation**: Add a `clean-intermediates` target that removes JSON exports and old DuckDB files but preserves `sra.duckdb` and the current dated DuckDB.

## Silent Failure in DuckDB Export Loop

The `make-database` target in `ncbi_to_duckdb.Makefile` processes collections in a `for` loop without error handling. During the Feb 2026 export, `biosamples_flattened` (51.7M docs × 39 fields) failed to load into DuckDB — likely OOM or JSON parsing failure — but the loop continued silently. It then deleted the JSON and printed "complete". The result: 16 of 17 tables loaded, `biosamples_flattened` missing, no error reported, and the JSON was gone.

- The `for` loop lacks `set -e` or per-command error checking
- `rm -f "$$json_file"` runs unconditionally after `duckdb` — even if `duckdb` failed
- The "complete" echo runs regardless of success
- **Fix applied**: Added per-step error checking, JSON preserved on failure, failures reported at end

### Root cause: DuckDB date auto-detection

The actual failure was DuckDB's `read_json` auto-detecting `collection_date` (and similar fields) as DATE type from the first ~20K rows, then failing on malformed values like `"08-2012"` at row 2.4M:

```
Could not parse string "08-2012" according to format specifier "%Y-%m-%d"
```

`biosamples_flattened` has 180 sparse columns across 51.7M docs. Many date-like fields contain messy submitter data that doesn't conform to any single date format.

**Fix**: Add `dateformat='DISABLED', timestampformat='DISABLED'` to the `read_json` call. This prevents DuckDB from inferring DATE/TIMESTAMP types — all date-like columns become VARCHAR. This is the correct behavior for NCBI biosample data where date fields contain values like `"2012"`, `"08-2012"`, `"missing"`, `"not collected"`, etc.

### Bolting a missing table into existing DuckDB

```bash
# Step 1: Export JSON (skip if JSON already exists)
make -f Makefiles/ncbi_to_duckdb.Makefile export-collection-json COLLECTION=biosamples_flattened

# Step 2: Load into DuckDB (uses CREATE OR REPLACE TABLE — safe for existing DB)
duckdb local/ncbi_duckdb_export/ncbi_metadata_flat_latest.duckdb -c "
CREATE OR REPLACE TABLE biosamples_flattened AS
SELECT * EXCLUDE _id FROM read_json(
  './local/ncbi_duckdb_export/biosamples_flattened.json',
  auto_detect=true, union_by_name=true,
  maximum_object_size=16777216, field_appearance_threshold=0,
  dateformat='DISABLED', timestampformat='DISABLED');"

# Step 3: Regenerate parquet
make -f Makefiles/ncbi_to_duckdb.Makefile export-parquet

# Step 4: Clean up JSON
rm local/ncbi_duckdb_export/biosamples_flattened.json
```

## What Worked Well

- **Atomic step design**: Steps 2a/2b/2c/2d write to distinct collections, enabling clean recovery from step 2c failure without re-running 2a/2b
- **Guard checks in scripts**: Step 2c checks for empty SRA collection and missing indexes before starting, failing fast with clear error messages
- **`allowDiskUse: true`**: Prevents OOM on large aggregations at the cost of speed — correct trade-off for a laptop rebuild
- **Index verification**: Step 2c verifies both the temp collection index and SRA index exist before running the join

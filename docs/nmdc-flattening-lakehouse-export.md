# NMDC Flattening for Lakehouse Export

How to produce lakehouse-ready Parquet files from an NMDC MongoDB mirror, using targets in [`Makefiles/nmdc_metadata.Makefile`](../Makefiles/nmdc_metadata.Makefile).

Output feeds BERDL tenants (e.g. `nmdc_flattened_biosamples`) via the [`/berdl-ingest`](https://github.com/kbaseincubator/BERIL-research-observatory/tree/main/.claude/skills/berdl-ingest) skill (wraps [`kbase/data-lakehouse-ingest`](https://github.com/kbase/data-lakehouse-ingest)).

## One-shot build

```bash
poetry install  # first time only
make -f Makefiles/nmdc_metadata.Makefile flatten-and-export-nmdc
```

Produces in `local/nmdc_export/`:

| Artifact | Notes |
|----------|-------|
| `parquet/*.parquet` | 6 lakehouse-ready files (one per flattened collection) |
| `nmdc_flattened.duckdb` | Queryable DuckDB for local exploration |
| `csv/flattened_biosample.csv` | CSV for coverage analysis |
| `biosample_coverage_results.json` | Schema coverage report |

## Targets

| Target | Effect |
|--------|--------|
| `flatten-nmdc` | Mongo `nmdc.*` → Mongo `nmdc.flattened_*` (writes enriched flattened collections back to Mongo) |
| `flatten-nmdc-auth` | Same, against authenticated remote Mongo (uses `local/.env.ncbi-loadbalancer.27778`) |
| `export-nmdc-duckdb` | Existing `flattened_*` Mongo collections → DuckDB |
| `export-nmdc-parquet` | DuckDB → Parquet (depends on `export-nmdc-duckdb`) |
| `export-flattened-biosample-csv` | Biosamples → CSV |
| `analyze-nmdc-biosample-coverage` | Schema coverage report |
| `flatten-and-export-nmdc` | Full chain |

The flattening step (`flatten-nmdc`) always covers the script's full collection list. To subset the **export** step, override `NMDC_FLATTENED_COLLECTIONS` (the Makefile variable the `export-nmdc-duckdb` loop iterates):

```bash
make -f Makefiles/nmdc_metadata.Makefile export-nmdc-duckdb \
  NMDC_FLATTENED_COLLECTIONS="flattened_biosample flattened_study"
```

## Configuration

| Variable | Default | Purpose |
|----------|---------|---------|
| `MONGO_URI` | `mongodb://localhost:27017/nmdc` | Source Mongo (NMDC mirror) |
| `NMDC_EXPORT_DIR` | `./local/nmdc_export` | Output base |
| `NMDC_PARQUET_DIR` | `$(NMDC_EXPORT_DIR)/parquet` | Parquet output |
| `NMDC_DUCKDB_FILE` | `$(NMDC_EXPORT_DIR)/nmdc_flattened.duckdb` | DuckDB output |
| `NMDC_FLATTENED_COLLECTIONS` | full list of 6 flattened collections | Drives the `export-nmdc-duckdb` loop; override to subset exports |

Override at invocation:

```bash
make -f Makefiles/nmdc_metadata.Makefile flatten-and-export-nmdc \
  MONGO_URI="mongodb://myhost:27017/nmdc" \
  NMDC_EXPORT_DIR="/tmp/nmdc-demo"
```

The flattener itself reads `local/.env` via its `--env-file` CLI flag (default). The NMDC Makefile targets do not pipe `ENV_FILE` through to the flattener, so Make-level overrides of `ENV_FILE` have no effect on `flatten-nmdc`.

## Output

6 flattened collections (produced by [`flatten_nmdc_collections.py`](../external_metadata_awareness/flatten_nmdc_collections.py)):

| Parquet file | Typical rows |
|--------------|-------------:|
| `flattened_biosample.parquet` | 14,938 |
| `flattened_biosample_chem_administration.parquet` | 90 |
| `flattened_biosample_field_counts.parquet` | 281 |
| `flattened_study.parquet` | 48 |
| `flattened_study_associated_dois.parquet` | 71 |
| `flattened_study_has_credit_associations.parquet` | 470 |

Row counts reflect the 2026-04-20 `nmdc_flattened_biosamples` BERDL tenant snapshot; source Mongo dictates actuals. The tenant currently holds additional tables (`flattened_data_generation`, `flattened_workflow_execution`, `flattened_workflow_execution_mags`, `flattened_data_object`) produced by the in-progress [`flatten-workflow-collections`](https://github.com/microbiomedata/external-metadata-awareness/tree/flatten-workflow-collections) branch; this doc will be updated when that branch merges.

**What the flattener does:**
- Fetches each NMDC collection from local Mongo
- Flattens nested structures with underscore-joined column names
- Pipe-joins array values to strings
- Enriches `env_broad_scale` / `env_local_scale` / `env_medium` with normalized CURIEs, canonical labels, and obsolescence flags via local OAK sqlite adapters (`sqlite:obo:envo`, etc.). The 3-layer OAK → OLS → BioPortal grounding referenced in `env-triad-data-pipeline.md` lives in separate scripts (`new_env_triad_oak_annotator.py`, `new_env_triad_ols_annotator.py`, `new_bioportal_curie_mapper.py`), not in `flatten_nmdc_collections.py`.

## Prerequisites

1. **Local MongoDB mirror of NMDC production.** Restore via `local_nmdc_mongodb_restore` target (expects `downloads/nmdc_select_mongodb_dump.gz`). Or point `MONGO_URI` at an authenticated remote NMDC Mongo and use `flatten-nmdc-auth`.
2. **Poetry environment** — `poetry install` in repo root.
3. **System tools:** `mongosh`, `mongoexport`, `duckdb`, `wget`, `yq`.
4. **Local OAK ontology databases** fetched on first use via `sqlite:obo:*` adapters (ENVO primarily). No network required once cached.

## Empirical timing (NUC, full NMDC corpus)

| Stage | Typical |
|-------|---------|
| `flatten-nmdc` (Mongo → Mongo, full enrichment) | 10–30 min |
| `export-nmdc-duckdb` | 1–2 min |
| `export-nmdc-parquet` | ~30 sec |

Enrichment is dominated by OAK ENVO grounding per unique env term. Re-runs are faster due to Mongo caching.

## Downstream

The `parquet/` directory is directly consumable by `/berdl-ingest`. Pair with a `.sql` DDL file declaring mixed-type columns as `STRING` — see [BERDL ingest skill notes](https://github.com/kbaseincubator/BERIL-research-observatory/tree/main/.claude/skills/berdl-ingest) and [`data_lakehouse_ingest`](https://github.com/kbase/data-lakehouse-ingest).

## Known limitations

- No `--help` or dry-run on Make targets; subprocess errors surface bare.
- No `_load_manifest` emitted alongside the parquet output (proposed BERDL governance artifact, not yet built).
- Multi-valued INSDC identifiers in `flattened_biosample.insdc_biosample_identifiers` are pipe-delimited; the obvious `REPLACE('biosample:', '')` strips only the first prefix. Split on `|` before joining to NCBI accessions. ~42 biosamples affected.
- `None` vs null: object-dtype columns may serialize Python `None` as the string `"None"` in parquet; downstream consumers should coerce.

## Related

- [`env-triad-data-pipeline.md`](env-triad-data-pipeline.md) — env triad grounding internals
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — collections and data flow
- [`../Makefiles/env_triads.Makefile`](../Makefiles/env_triads.Makefile), [`../Makefiles/ncbi_biosample_measurements.Makefile`](../Makefiles/ncbi_biosample_measurements.Makefile), [`../Makefiles/ncbi_metadata.Makefile`](../Makefiles/ncbi_metadata.Makefile) — related NCBI-side pipelines

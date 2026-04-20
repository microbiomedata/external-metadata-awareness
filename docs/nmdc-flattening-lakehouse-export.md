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
| `parquet/*.parquet` | 10 lakehouse-ready files (one per flattened collection) |
| `nmdc_flattened.duckdb` | Queryable DuckDB for local exploration |
| `csv/flattened_biosample.csv` | CSV for coverage analysis |
| `biosample_coverage_results.json` | Schema coverage report |

## Targets

| Target | Effect |
|--------|--------|
| `flatten-nmdc` | Mongo `nmdc.*` → Mongo `nmdc.flattened_*` (writes enriched flattened collections back to Mongo) |
| `flatten-nmdc-parquet` | Flatten + write parquet directly (skips DuckDB intermediate) |
| `flatten-nmdc-auth` | Same, against authenticated remote Mongo (uses `local/.env.ncbi-loadbalancer.27778`) |
| `export-nmdc-duckdb` | Existing `flattened_*` Mongo collections → DuckDB |
| `export-nmdc-parquet` | DuckDB → Parquet (depends on `export-nmdc-duckdb`) |
| `export-flattened-biosample-csv` | Biosamples → CSV |
| `analyze-nmdc-biosample-coverage` | Schema coverage report |
| `flatten-and-export-nmdc` | Full chain |

Subset collections:

```bash
make -f Makefiles/nmdc_metadata.Makefile flatten-nmdc-parquet COLLECTIONS=biosample,study
```

## Configuration

| Variable | Default | Purpose |
|----------|---------|---------|
| `MONGO_URI` | `mongodb://localhost:27017/nmdc` | Source Mongo (NMDC mirror) |
| `NMDC_EXPORT_DIR` | `./local/nmdc_export` | Output base |
| `NMDC_PARQUET_DIR` | `$(NMDC_EXPORT_DIR)/parquet` | Parquet output |
| `NMDC_DUCKDB_FILE` | `$(NMDC_EXPORT_DIR)/nmdc_flattened.duckdb` | DuckDB output |
| `ENV_FILE` | `local/.env` | Holds `BIOPORTAL_API_KEY` for env triad enrichment |

Override at invocation:

```bash
make -f Makefiles/nmdc_metadata.Makefile flatten-and-export-nmdc \
  MONGO_URI="mongodb://myhost:27017/nmdc" \
  NMDC_EXPORT_DIR="/tmp/nmdc-demo" \
  ENV_FILE="local/.env"
```

## Output

10 flattened collections (produced by [`flatten_nmdc_collections.py`](../external_metadata_awareness/flatten_nmdc_collections.py)):

| Parquet file | Typical rows |
|--------------|-------------:|
| `flattened_biosample.parquet` | 14,938 |
| `flattened_biosample_chem_administration.parquet` | 90 |
| `flattened_biosample_field_counts.parquet` | 281 |
| `flattened_study.parquet` | 48 |
| `flattened_study_associated_dois.parquet` | 71 |
| `flattened_study_has_credit_associations.parquet` | 470 |
| `flattened_data_generation.parquet` | 10,423 |
| `flattened_workflow_execution.parquet` | 24,698 |
| `flattened_workflow_execution_mags.parquet` | 40,580 |
| `flattened_data_object.parquet` | 226,864 |

Row counts reflect the 2026-04-20 `nmdc_flattened_biosamples` BERDL tenant snapshot; source Mongo dictates actuals.

**What the flattener does:**
- Fetches each NMDC collection from local Mongo
- Flattens nested structures with underscore-joined column names
- Pipe-joins array values to strings
- Enriches `env_broad_scale` / `env_local_scale` / `env_medium` with normalized CURIEs, canonical labels, obsolescence flags, label verification (OAK → OLS → BioPortal layered grounding)

## Prerequisites

1. **Local MongoDB mirror of NMDC production.** Restore via `local_nmdc_mongodb_restore` target (expects `downloads/nmdc_select_mongodb_dump.gz`). Or point `MONGO_URI` at an authenticated remote NMDC Mongo and use `flatten-nmdc-auth`.
2. **Poetry environment** — `poetry install` in repo root.
3. **System tools:** `mongosh`, `mongoexport`, `duckdb`, `wget`, `yq`.
4. **BioPortal API key** in `local/.env` (for OLS/BioPortal fallback in env triad grounding). OAK/ENVO grounding works without it; just fewer terms ground.

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

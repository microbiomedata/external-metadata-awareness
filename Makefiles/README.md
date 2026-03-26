# Makefiles

Pipeline orchestration for data loading, transformation, and export.

All Makefiles are invoked with `make -f Makefiles/<name>.Makefile <target>`.

## Makefiles by Pipeline

| Makefile | Database | Purpose |
|---|---|---|
| `ncbi_metadata.Makefile` | ncbi_metadata | Load NCBI XML into MongoDB, flatten biosamples/bioprojects |
| `ncbi_schema.Makefile` | ncbi_metadata | Load and flatten NCBI attribute/package schema definitions |
| `sra_metadata.Makefile` | sra_metadata / ncbi_metadata | Fetch SRA from BigQuery/S3, extract biosample-bioproject pairs |
| `env_triads.Makefile` | ncbi_metadata | Environmental triad extraction, splitting, annotation (OAK/OLS/BioPortal) |
| `measurement_discovery.Makefile` | ncbi_metadata | Measurement parsing with quantulum3, usage stats, dimensional analysis |
| `ncbi_biosample_measurements.Makefile` | ncbi_metadata | Normalize and flatten biosample measurement fields |
| `ncbi_to_duckdb.Makefile` | ncbi_metadata | Export flat MongoDB collections to DuckDB and Parquet |
| `gold.Makefile` | gold_metadata | Flatten GOLD biosamples/studies/seq_projects with ontology enrichment |
| `nmdc_metadata.Makefile` | nmdc_metadata | Flatten NMDC collections, fetch submissions, export to DuckDB |
| `nmdc_schema.Makefile` | — | Download and extract NMDC submission schema definitions |
| `mixs.Makefile` | — | Download and extract MIxS schema definitions |
| `github.Makefile` | — | Fetch GitHub release notes |
| `test_workflow.Makefile` | ncbi_metadata_test | End-to-end test pipeline using a sample subset |

## Common Variables

All Makefiles support these (with defaults):

```makefile
RUN          = poetry run
MONGO_URI   ?= mongodb://localhost:27017/<db_name>
ENV_FILE     # optional — set to path of .env file for credentials
```

When `ENV_FILE` is set, it's passed as `--env-file $(ENV_FILE)` to CLIs (except GOLD scripts, which use `--dotenv-path`).

## Conventions

**JavaScript aggregations** use `mongo-js-executor`:
```bash
make -f Makefiles/ncbi_metadata.Makefile flatten_bioprojects
```

**Dangerous targets** (drop/purge) are named with `purge-*`, `clean-*`, or `drop-*` prefixes.

**Multi-step workflows** use numbered step targets + a meta-target:
```bash
# Individual steps
make -f Makefiles/measurement_discovery.Makefile count-biosamples-per-hn-step1
make -f Makefiles/measurement_discovery.Makefile count-biosamples-per-hn-step2
make -f Makefiles/measurement_discovery.Makefile count-biosamples-per-hn-step3

# Or all at once
make -f Makefiles/measurement_discovery.Makefile count-biosamples-per-harmonized-name-atomic
```

## Timing Convention

Targets that use `mongo-js-executor` get timestamps from the JS scripts themselves — no need for `date && time` wrapping in the Makefile. Use `@date` before/after only for targets that call raw `mongosh`, Python CLIs, or other tools that don't self-report timing.

Some older targets still have redundant `@date` wrapping around `mongo-js-executor` calls. This is harmless but unnecessary.

## Best Example

`ncbi_to_duckdb.Makefile` — has a `help` target, error handling, file-existence checks, and space-optimized cleanup:
```bash
make -f Makefiles/ncbi_to_duckdb.Makefile help
```

# NMDC Data Access

How this repo accesses NMDC data after the 2026-05-18 scope narrowing.

This repo **no longer manages an NMDC MongoDB**. The flatten/restore/export pipeline that used to ingest NMDC Mongo dumps and produce lakehouse-ready parquet was retired in favor of [`kbase/data-lakehouse-ingest`](https://github.com/kbase/data-lakehouse-ingest) doing the equivalent work upstream of BERDL tenants. What remains:

| Need | Source | How |
|---|---|---|
| **NMDC submission portal data** | `https://data.microbiomedata.org/api/metadata_submission` (OAuth) | `make nmdc-submissions-to-mongo` → local Mongo → optional `export-submissions-to-duckdb` |
| **NMDC schema (submission-schema)** | `microbiomedata/submission-schema` on GitHub | `nmdc_schema.Makefile` targets fetch YAML and extract `Env*SoilEnum` value sets for the voting-sheets workflow |
| **NMDC slot definitions (materialized patterns)** | `microbiomedata/nmdc-schema` on GitHub | `make load-global-nmdc-slots` (in `measurement_discovery.Makefile`); fetched at runtime by `mongo-js/load_global_nmdc_slots.js` |
| **NMDC biosample / study analytics data** | NMDC public API (`api.microbiomedata.org/nmdcschema/...`) | Several `Makefiles/nmdc_metadata.Makefile` targets fetch JSON via `wget`/`curl` and produce TSVs (`local/nmdc-production-*`) |
| **Live NMDC MongoDB queries (ad-hoc)** | NMDC Metadata MongoDB (currently NERSC Spin; moving to GCP) | Open an SSH tunnel; point any MongoDB client at `localhost:<port>` — see below |

## Analytical scripts in this repo that target NMDC data

These run against whatever Mongo URI you pass via `--mongo-uri` (or via `MONGO_URI` env var). They don't bake in any NMDC host:

| Script | Source it reads | Notes |
|---|---|---|
| `analyze_nmdc_biosample_coverage.py` | local CSV (you produce it externally) | NMDC slot coverage against a biosample CSV; entry point `analyze-nmdc-biosample-coverage` |
| `extract_nmdc_doi_inventory.py` | a Mongo with NMDC collections | DOI/PMID/URL inventory; entry point `extract-nmdc-doi-inventory` |
| `find_nmdc_measurement_slots.py` | `nmdc-schema.tsv` | schema-only; no live Mongo needed |
| `mixs_slots_in_nmdc.py` | `mixs-schema.tsv` + `nmdc-schema.tsv` | schema-only |
| `get_authoritative_labels_only_for_nmdc_context_columns.py` | local TSV + OAK (ENVO) | local-only |
| `predict_env_package_from_nmdc_context_authoritative_labels.py` | local TSVs + OAK + sklearn | local-only |

## Ad-hoc tunnel pattern (any backend)

```shell
ssh -L <LOCAL_PORT>:<NMDC_MONGO_HOST>:<NMDC_MONGO_PORT> <BASTION_USER>@<BASTION_HOST>
```

Then connect any client with a URI like:

```
mongodb://<USER>:<PASS>@localhost:<LOCAL_PORT>/<DB>?authSource=admin
```

Any analytical CLI in this repo will work transparently against that URI:

```shell
poetry run extract-nmdc-doi-inventory \
  --mongo-uri "mongodb://<USER>:<PASS>@localhost:<LOCAL_PORT>/nmdc?authSource=admin" \
  --output-file local/nmdc_doi_inventory.tsv
```

The repo deliberately does not codify the SSH command (NERSC vs. GCP details, jump-host names) — those belong in environment-specific runbooks, not in the repo's scope.

## What was retired

- `make flatten-nmdc` / `make flatten-and-export-nmdc` (used `flatten_nmdc_collections.py` to walk a local NMDC Mongo dump)
- `make local_nmdc_mongodb_restore`, `make restore-to-{un,}authenticated`, `make nmdc-prod-to-other`, `downloads/nmdc_select_mongodb_dump.gz` — dump/restore of an NMDC Mongo via the NERSC SSH tunnel
- `make export-nmdc-{duckdb,parquet}`, `make export-flattened-biosample-csv` — DuckDB/parquet/CSV exports of flattened NMDC collections
- `docs/nmdc-flattening-lakehouse-export.md` — documented the chain above; now described upstream in `kbase/data-lakehouse-ingest`
- `NMDC_MONGO_USER` / `NMDC_MONGO_PASSWORD` slots in `local/.env.template`

For historical context see `docs/biosample-flattening-timeline-2020-2025.md` and the retrospective sections of `docs/pipeline-rebuild-pain-points.md`.

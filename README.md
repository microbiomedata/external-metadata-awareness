# external-metadata-awareness

MongoDB + Parquet analytics for NCBI BioSample/BioProject/SRA and NMDC submission-portal metadata. Environmental triad annotation, harmonized-attribute counts, measurement discovery, value-set voting sheets.

## What this repo does

Ingests bulk metadata from public sources into MongoDB, flattens nested records into queryable collections, and produces analytical outputs:

- **NCBI BioSample / BioProject / SRA** ingest from FTP XML, S3 parquet, and BigQuery; flattening, harmonization, env-triad annotation, SRA pair linking.
- **NMDC submission portal** ingest via OAuth API (`https://data.microbiomedata.org/api/metadata_submission`); flattening for review.
- **Measurement discovery** with `quantulum3` over biosample attributes; harmonized-name dimensional stats.
- **Voting-sheet generation** for NMDC submission-schema environmental-context value sets (notebooks under `notebooks/environmental_context_value_sets/`).
- **Analytics** that can run against any NMDC MongoDB backend (e.g., via SSH tunnel) without this repo owning that data's lifecycle.

Canonical formats are **MongoDB** (working data) and **Parquet** (export). CSV/TSV/DuckDB intermediates are being retired ([#387](https://github.com/microbiomedata/external-metadata-awareness/issues/387), [#410](https://github.com/microbiomedata/external-metadata-awareness/issues/410)).

## Quick start

```bash
git clone https://github.com/microbiomedata/external-metadata-awareness.git
cd external-metadata-awareness
poetry install

# Copy and fill in credentials
cp local/.env.template local/.env
$EDITOR local/.env

# A simple connection check
poetry run mongo-connect --uri mongodb://localhost:27017/ncbi_metadata --env-file local/.env --connect
```

Detailed walkthrough: [`docs/GETTING_STARTED.md`](docs/GETTING_STARTED.md).

## Pipelines

| Pipeline | Makefile | Entry point |
|---|---|---|
| NCBI BioSample ingest + flatten | `Makefiles/ncbi_metadata.Makefile` | `make load-biosamples-into-mongo` |
| NCBI BioProject ingest + flatten | `Makefiles/ncbi_metadata.Makefile` | `make load_acceptable_sized_leaf_bioprojects_into_mongodb` |
| SRA ingest (S3 parquet → Mongo) | `Makefiles/sra_metadata.Makefile` | `make -f ... load-sra-parquet-to-mongo` |
| Environmental triad annotation | `Makefiles/env_triads.Makefile` | `make env-triads` |
| Measurement discovery | `Makefiles/measurement_discovery.Makefile` | `make run-measurement-discovery` |
| NMDC submission portal ingest | `Makefiles/nmdc_metadata.Makefile` | `make nmdc-submissions-to-mongo` |
| NMDC schema (voting-sheet inputs) | `Makefiles/nmdc_schema.Makefile` | `make downloads/nmdc_submission_schema.yaml` |

Default `MONGO_URI` is `mongodb://localhost:27017/<db>`; override per-invocation. Storage paths configurable via `DOWNLOADS_DIR=` / `LOCAL_DIR=` (see [#391](https://github.com/microbiomedata/external-metadata-awareness/issues/391)).

## Documentation

| Topic | File |
|---|---|
| First-time walkthrough | [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) |
| Architecture, collections, data flow | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| MongoDB patterns (connections, aggregations, conventions) | [docs/MONGODB_PATTERNS.md](docs/MONGODB_PATTERNS.md) |
| Code style, testing, dev workflow | [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) |
| NMDC data access (post-retirement of the local Mongo ingest) | [docs/nmdc-data-access.md](docs/nmdc-data-access.md) |
| Where to get metadata (NMDC / GOLD / INSDC, lakehouses) | [docs/metadata-sources-and-access-methods.md](docs/metadata-sources-and-access-methods.md) |
| Environmental triad value-set lifecycle | [docs/environmental-triad-value-set-lifecycle.md](docs/environmental-triad-value-set-lifecycle.md) |
| Environmental triad data pipeline (technical reference) | [docs/env-triad-data-pipeline.md](docs/env-triad-data-pipeline.md) |
| Per-Makefile orientation | [Makefiles/README.md](Makefiles/README.md) |

For AI-assistant usage (cost guidelines, tool conventions): [CLAUDE.md](CLAUDE.md).

## Scope

In scope:
- NCBI BioSample / BioProject / SRA ingest and analytics
- NMDC submission-portal ingest and analytics
- Analytics on any NMDC Metadata MongoDB backend (read via tunnel; this repo no longer manages that data)
- Environmental triad annotation, measurement discovery, voting sheets, schema/slot loaders

Retired in 2026-05:
- **GOLD pipeline** (see [PR #418](https://github.com/microbiomedata/external-metadata-awareness/pull/418)) — for raw GOLD access, see the JGI Dremio lakehouse
- **NMDC main-Mongo ingest/flatten chain** (see [PR #422](https://github.com/microbiomedata/external-metadata-awareness/pull/422)) — replaced upstream by [`kbase/data-lakehouse-ingest`](https://github.com/kbase/data-lakehouse-ingest)

## Contributing

- Issues: [`microbiomedata/external-metadata-awareness/issues`](https://github.com/microbiomedata/external-metadata-awareness/issues)
- Security: [SECURITY.md](SECURITY.md)
- Development conventions: [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)

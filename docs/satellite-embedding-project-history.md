# Satellite-embedding project: history and current status

This doc exists so future readers can understand why this repo once contained an aggressive `biosamples`-filter pipeline (`create-environmental-candidates-2017-plus` and `copy-environmental-candidates-to-ncbi-metadata`) and what became of the work those targets supported. Both targets were removed on 2026-05-19 because the project they served is no longer active here.

## What the project was

The plan was to join two embedding spaces over the same physical location:

1. **Google AlphaEarth Satellite Embedding V1**: Google Earth Engine's pre-trained satellite imagery embeddings, sampled per year per geographic tile. Coverage starts in **2017**.
2. **Biosample ENVO triad embeddings**: text embeddings (or other vector representations) of NCBI BioSample `env_broad_scale`, `env_local_scale`, `env_medium` values, joined to `lat_lon` from the same biosample record.

If both vectors describe the same site, you should be able to learn a mapping that lets you predict an ENVO triad annotation from satellite imagery, or conversely flag suspicious biosamples whose annotated environment doesn't match what the satellite says is there.

Two pieces of the work lived in two repos:

- **EMA (this repo)**: produced the metadata-side substrate, a 3M-biosample DuckDB containing biosamples with complete env triads and `collection_date >= 2017-01-01`. The 2017 cutoff existed solely to align with AlphaEarth's temporal coverage. The filter targets here (`create-environmental-candidates-2017-plus`, then `copy-environmental-candidates-to-ncbi-metadata`) materialized that subset *destructively* into the `biosamples` collection.
- **`contextualizer-ai/env-embeddings`** (separate GitHub repo): held the satellite-embedding side and the modeling code (~41 GB of CSV/TSV files).

The shared metadata DuckDB was published to NERSC at `https://portal.nersc.gov/project/m3408/biosamples_duckdb/`.

## What became of it

Status: **paused / archived**, with the data side effectively gone.

- The local working copy of `contextualizer-ai/env-embeddings` and the ~41 GB of satellite-embedding source data were not retained and were not backed up. The GitHub repo presumably still exists but is not wired into any of EMA's current pipelines.
- The metadata-side DuckDB snapshot (`ncbi_metadata_3M_biosamples_flat_20250930.duckdb`, 2.2 GiB) was deleted on 2026-05-15 as part of the embedding-and-snapshot cleanup. It contained only the standard EMA analytics tables filtered to the 3M subset, no embeddings.
- The architecture design for the join was not preserved in this repository and is not publicly available.
- The NERSC portal at `https://portal.nersc.gov/project/m3408/biosamples_duckdb/` still hosts the 3M-row DuckDB and Parquet exports (project `m3408` is NMDC's NERSC project). Reachable, but stale: it predates the Feb 2026 pipeline rebuild.

## Why we removed the filter targets

Two reasons:

1. **The project they served is no longer active**, so running the targets just to "complete the pipeline" produces a destructively pruned `biosamples` collection for no current purpose.
2. **The replacement is in flight**: the Feb 2026 pipeline rebuild and the in-progress refactor (issue #424) target a full 51.7M-biosample workflow, not a 3M-row subset. Keeping the 2017-plus filter around invites accidental reactivation that would silently shrink the working dataset.

The targets were removed in the same commit that introduced this doc.

## If someone wants to revive the work

- The satellite-embedding side: check whether `contextualizer-ai/env-embeddings` on GitHub still has the modeling code; the raw embeddings may need to be re-derived from Google Earth Engine.
- The metadata side: rebuild the filter inline if needed. The `$match` aggregation that the removed `create-environmental-candidates-2017-plus` target used is preserved in git history (search `git log --all -p Makefiles/ncbi_metadata.Makefile`).
- Open a new issue scoping the join's current relevance before re-introducing any of this; it's been ~6 months idle and the surrounding ecosystem has moved.

## Cross-refs

- `docs/pipeline-rebuild-pain-points.md`: NERSC portal reference and the 3M to 51.7M rebuild context
- `docs/data-products-inventory.md`: historical inventory of DuckDB tables
- `unorganized/September-2025-Biosample-DuckDB-documentation.html`: per-table schema for the 3M subset, from when the project was active

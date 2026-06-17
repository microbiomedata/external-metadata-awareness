# notebooks/

Analysis notebooks for EMA. They fall into three kinds; see each subdirectory's
README for status, when to rerun, and provenance.

## 1. Live tools (run as part of real workflows)
- `environmental_context_value_sets/generate_voting_sheet.ipynb` — generates the
  env_broad_scale / env_local_scale / env_medium "voting sheets" (the canonical
  env-triad value-set method; drives submission-schema enum PRs). See
  `voting-sheet-generation-readme.md` in that directory.
- `mixs_inline_examples_checking/` — validates MIxS inline `examples` against
  their LinkML types/patterns/enums.

## 2. Study provenance (kept as worked examples + reusable patterns)
How higher-quality environmental triads were derived for specific studies,
identifiable by place / person / project. See `studies_exploration/README.md`.
- `studies_exploration/emp_500_ng/` (+ `myrold/`, `MacRae-Crerar/`) — EMP500 GOLD-vs-NCBI env-triad re-curation.
- `studies_exploration/simons_wishlist/` — Simon Roux SRA import candidates.
- `studies_exploration/stream_bank_riparian/` — stream vs river-bank env_local_scale guidance.
- `studies_exploration/streams_assessments_llm/` — STREAMS reporting-standards LLM assessment.
- `studies_exploration/marie_kroeger_gs0153999/` — single GOLD study env extraction.
- `studies_exploration/predict_env_local_scale_from_{nlcd_geotiff,osm}.ipynb`, `map_with_folium.ipynb` — reusable geospatial env_local_scale inference.

## 3. Superseded / reference (kept for provenance; production path is a script)
- `studies_exploration/ncbi_annotation_mining/` — original env-triad mining; happy
  path is now `env_triads` Makefile + `new_env_triad_*.py` (retains a few un-ported algorithms).
- `software_methods_exploration/` — method R&D that fed `oak_helpers.py` and the env-triad annotators.
- `multi-lexmatch/`, `github-repo-metadata/`, `mixs_preferred_units/` — unique data-acquisition / analysis utilities with no script equivalent yet.

Deleted notebooks (superseded/orphaned) are recorded in `REMOVED.md`.

## Notes
- Helper modules: `core.py` (Mongo helpers used by a couple of study notebooks)
  and `environmental_context_value_sets/common.py`. New code should prefer
  `external_metadata_awareness.mongodb_connection`.
- Many directories commit their output data (TSV/JSON/HTML/PDF) alongside the
  notebook for provenance.

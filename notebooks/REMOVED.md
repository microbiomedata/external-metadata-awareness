# Removed notebooks

Notebooks deleted because they were superseded or orphaned. Kept here as a
record of what they did and where the functionality went. The deletion commit
is in this PR / issue #474; use `git log --all --diff-filter=D -- <path>` to
recover a file from history.

## `old/infer_biosample_env_context_obo_curies.ipynb`
- **What it did:** the original pre-MongoDB prototype for inferring environmental-context CURIEs. Regex-extracted CURIEs from a local `ncbi_biosamples.duckdb` and annotated them against ENVO/PO with OAK.
- **Why removed:** fully superseded by the MongoDB env-triad pipeline (`Makefiles/env_triads.Makefile` + `external_metadata_awareness/new_env_triad_*.py`). It also referenced a stale Intel-MBP virtualenv path and predated the current repo layout.
- **Removed in:** issue #474 (https://github.com/microbiomedata/external-metadata-awareness/issues/474).

## `mixs-slot-ranking/` (`build_mixs_slot_rank_template.ipynb`, `mixs_class_ancestry.tsv`, `mixs_slot_rank_template.tsv`)
- **What it did:** built a MIxS slot-ranking template (live SchemaView -> per-slot rank template + class-ancestry table) that fed a schema-based measurement-target ranking system.
- **Why removed:** that ranking system was deliberately removed on 2025-09-28 (see `docs/schema-based-ranking-removal-2025-09-28.md`; the `prioritize_measurement_targets.py` script and several Makefile/mongo-js targets were deleted). This notebook was the orphaned upstream of a discontinued workflow.
- **Removed in:** issue #474 (https://github.com/microbiomedata/external-metadata-awareness/issues/474).

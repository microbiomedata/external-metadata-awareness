## Status (2026)

This is the **original** env-triad mining pipeline. The happy path is now the
production `env_triads` Makefile target plus `external_metadata_awareness/new_env_triad_*.py`
(see `docs/env-triad-data-pipeline.md`). Kept for reference and because a few
algorithms were never ported to the scripts:
- the `compact_mined_triads` 4-way join (in `compact_mined_triads.ipynb`),
- the greedy longest-match coverage optimizer (`optimize_annotations()` in the NER notebook),
- the CURIE-repair regex (in `extract_and_parse_env_triad_values.ipynb`).

Rerun only to re-derive those un-ported pieces or to study how the pipeline was built.

## Notebook order 

1. biosample_flattening_etc_cleanup.ipynb
    - don't drop `biosample_harmonized_attributes` collection unless you intent to rerun flatten_all_ncbi_biosample_harmonized_attributes
2. flatten_all_ncbi_biosample_harmonized_attributes.ipynb
    - hours (no benefit from requests caching)
3. extract_and_parse_env_triad_values.ipynb
4. notebooks/lexical_index_functions.ipynb
5. build_and_apply_lexical_index_from_env_triad_values_ner.ipynb
    - fast if requests have been cached
    - check for creation of `preferred_mappings_curies` in `target_collection` aka "class_label_cache"
    - rerun some steps after second lexical index is created?
        - how to assess benefit?
        - before: 69% of `triad_components_labels` have an `partial_matches_vs_precedent.partial_matches_vs_precedent` with average length of 1.69
        - after: 71% of `triad_components_labels` have an `partial_matches_vs_precedent.partial_matches_vs_precedent` with average length of 1.75
6. compact_mined_triads.ipynb


## Second pass

replace 
`biosamples_env_triads_precedent_lexical_index = load_lexical_index(biosamples_env_triads_precedent_lexical_index_yaml)`
with
`biosamples_env_triads_precedent_lexical_index = load_lexical_index(biosamples_env_triads_precedent_lexical_index_second_pass_filtered_yaml)`

replace
`df.to_csv(absent_from_lexical_index_first_pass_tsv, sep='\t', index=False)`

which has 1839 lines

with
`df.to_csv(absent_from_lexical_index_second_pass_tsv, sep='\t', index=False)`

which has 1630


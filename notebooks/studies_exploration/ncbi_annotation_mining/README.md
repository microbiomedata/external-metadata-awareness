## Notebook order 

1. biosample_flattening_etc_cleanup.ipynb
    - don't drop `biosample_harmonized_attributes` collection unless you intent to rerun flatten_all_ncbi_biosample_harmonized_attributes
2. flatten_all_ncbi_biosample_harmonized_attributes.ipynb
    - hours (no benefit from requests caching)
3. extract_and_parse_env_triad_values.ipynb
    - fast if requests have been cached
4. build_and_apply_lexical_index_from_env_triad_values_ner.ipynb
    - fast if requests have been cached
    - check for creation of `preferred_mappings_curies` in `target_collection` aka "class_label_cache"
    - rerun some steps after second lexical index is created?
        - how to assess benefit?
        - before: 69% of `triad_components_labels` have an `partial_matches_vs_precedent.partial_matches_vs_precedent` with average length of 1.69
        - after: 71% of `triad_components_labels` have an `partial_matches_vs_precedent.partial_matches_vs_precedent` with average length of 1.75
5. compact_mined_triads.ipynb


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


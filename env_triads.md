- populate `biosamples` collection
    - `load-biosamples-into-mongo` makefile target, which uses `xml-to-mongo`, an alias for `xml_to_mongo.py`
- build `biosamples_flattened` collection
    - `flatten_biosamples.js`
    - also see biosamples_ids and biosamples_links

----


- build `biosamples_env_triad_value_counts_gt_1`
    - `enriched_biosamples_env_triad_value_counts_gt_1.js`
        - add more missing data indicators
    - `split_env_triad_values_from_local` makefile target, which uses `new_env_triad_values_splitter.py`
- build `env_triad_component_labels`
    - `aggregate_env_triad_label_components.js`
    - check label_length, digits_only 
- add optimal OAK annotations
    - `new_env_triad_oak_annotator.py`
- add full-length OLS annotations
    - `new_env_triad_ols_annotator.py`
- build `env_triad_component_curies_uc`
    - `aggregate_env_triad_curies.js`
    - deal with ENV, ENV0, NCIT, SNOMED/SNOMEDCT
- add label, obsolete to ENVO and PO CURIes
    - `new_check_semsql_curies.py`


don't forget about curies and filtered mappings, possible with expansion overrides!


env_triads



# multi-lexmatch/

Data-acquisition and aggregation notebooks for the multi-ontology lexical
matching work. These build the ontology corpus that lexmatch runs against; no
Python script in this repo duplicates them.

| Notebook | What it does | Output |
|---|---|---|
| `fetch_bioportal_class_counts.ipynb` | BioPortal API -> per-ontology class counts. | `bioportal_ontology_class_counts.tsv` |
| `parse_obo_ontologies_yaml.ipynb` | OBO Foundry registry -> tidy table. | `obo_ontologies.tsv` |
| `interleave_s3_catalog_yaml_registry_bioportal_obo.ipynb` | Merge BBOP S3 SemanticSQL catalog + registry + BioPortal/OBO into a filtered ontology list. | `bbop-sem-sql-catalog-filtered.tsv` |
| `aggregate_lexmatch_results.ipynb` | Concatenate the per-ontology SSSOM lexmatch TSVs. | `lexmatch-combined.tsv` |

`aggregate_lexmatch_results` is related to `prioritize_lexmatch_results.py`
(which filters/ranks SSSOM mappings) but does raw aggregation, not ranking.

**Rerun when:** rebuilding the set of ontologies to lexmatch, or refreshing the
combined lexmatch output.

# software_methods_exploration/

Method R&D notebooks. Most fed the productionized code and are kept as
reference for how approaches were chosen, not as workflows to rerun.

| Notebook(s) | Status |
|---|---|
| `biosample_to_bioproject_via_duckdb.ipynb`, `biosample_to_bioproject_via_sra.ipynb` (+ `biosample_to_bioproject.md`) | **Superseded** by the parquet route `derive-sra-pairs-from-parquet` (issue #399) + `export_sra_accession_pairs.py` / `sra_accession_pairs_tsv_to_mongo.py`. Kept as a debugging/provenance note. |
| `lexical_indexing.ipynb`, `oak_experiments.ipynb`, `oak_min_annotations_max_coverage.ipynb` | OAK annotation R&D; production logic now in `oak_helpers.py` + `new_env_triad_oak_annotator.py`. |
| `envo_subsets.ipynb`, `oak_generate_ancs_descs_dict.ipynb`, `oak_reflexivity_experiments.ipynb` | Pure OAK experiments (ENVO subset filtering, ancestor/descendant export, reflexivity); no direct script equivalent. |

**Rerun when:** rarely; reference only. The superseded biosample<->bioproject
route should not be used (use the parquet derive path).

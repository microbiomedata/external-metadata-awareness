- Python (.py): 5 files from root moved into external_metadata_awareness
    - copy_database_without_compression.py
    - nomalize_samp_size.py
    - plot_oak_annotation_coverage.py
    - populate_env_triads_collection.py
    - prioritize_lexmatch_results.py

1. Main Python package:
   - In external_metadata_awareness/ (large number of Python scripts, all were moved here including your scripts)
2. Notebooks supporting files:
   - notebooks/core.py (utility functions used by notebooks)
   - notebooks/environmental_context_value_sets/common.py
   - Several Python files in notebooks/studies_exploration/ and subdirectories:
    - entire_submissions_extraction_flattening.py
    - flattening/insert_all_flat_gold_biosamples.py
    - flattening/insert_all_flat_submission_biosamples.py
    - get_nmdc_submissions.py
3. Tests:
   - tests/init.py (only contains initialization, no actual tests)


- Markdown (.md): 4 files in root
    - CLAUDE.md
    - env_triad_annotation.md
    - env_triads.md
    - requests-caching.md

Markdown (.md) files repo-wide:

1. Root directory:
   - CLAUDE.md, env_triad_annotation.md, env_triads.md, requests-caching.md
2. claude-mds directory:
   - nmdc-env-triad-valueset-lifecycle.md, submission-schema-CLAUDE.md
3. Notebooks directory:
   - voting-sheet-generation-readme.md
   - Multiple README.md files in subfolders
   - Documentation in studies_exploration/
4. Unorganized directory:
   - Various documentation and notes including README files


- YAML (.yaml): 3 files in root
    - env_triad_annotation.yaml
    - env_triads_chat_gpt_linkml_schema.yaml
    - expanded_envo_po_lexical_index.yaml

YAML/YML files repo-wide:

1. Root directory:
   - env_triad_annotation.yaml
   - env_triads_chat_gpt_linkml_schema.yaml
   - expanded_envo_po_lexical_index.yaml
2. Package directory:
   - expanded_envo_po_lexical_index.yaml (duplicate in external_metadata_awareness/)
3. Flag data directory:
   - flag_data.yaml, flag_data_with_colors.yaml, flag_schema.yaml
4. Notebooks directory:
   - voting_sheets_configurations.yaml
   - Various data files in studies_exploration/
   - Several lexical index files
5. Prompt templates:
   - mixs-slots-sex-gender-analysis-prompt.yaml
   - unused-terrestrial-biomes-prompt.yaml
6. Unorganized directory:
   - docker-compose.yml
   - extra-openai-models.yaml


- SQLite (.sqlite): 3 files in root
    - my_cache.sqlite
    - new_env_triad_values_splitter_cache.sqlite
    - requests_cache.sqlite

SQLite/DB files repo-wide:

1. Root directory:
   - my_cache.sqlite
   - new_env_triad_values_splitter_cache.sqlite
   - requests_cache.sqlite
2. lexmatch-shell-scripts:
   - env_triad_pvs_sheet.db
   - nmdc.db
3. metpo directory:
   - mpo_v0.74.en_only.db
   - n4l_merged.db
4. Notebooks directory:
   - requests_cache.sqlite in studies_exploration/ncbi_annotation_mining/

- Jupyter Notebooks (.ipynb): 2 files in root, both deleted because of equivalent (or better) .py files, since moved
  into external_metadata_awareness
    - nomalize_samp_size.ipynb
    - populate_env_triads_collection.ipynb

Jupyter Notebooks (.ipynb) repo-wide:

1. Package directory:
   - new_env_triad_values_splitter.ipynb
2. Notebooks directory:
   - Large collection of notebooks (45+ files)
   - Main categories:
    - environmental_context_value_sets/
    - mixs_preferred_unts/
    - multi-lexmatch/
    - software_methods_exploration/
    - studies_exploration/ (many subdirectories with notebooks)


- Other files:
    - Makefile (no extension)
    - poetry.lock
    - pyproject.toml
    - .gitignore
    - .yamlfmt
    - bioportal_class_mapping_errors.txt
    - env_triad_annotation-etc-collections.tsv

Makefiles repo-wide:

1. Root directory:
   - Makefile (main)
2. Makefiles directory:
   - envo.Makefile
   - gold.Makefile
   - mixs.Makefile
   - ncbi_metadata.Makefile
   - ncbi_schema.Makefile
   - nmdc_metadata.Makefile
   - nmdc_schema.Makefile
3. Unorganized directory:
   - docker.Makefile

Files with "postgres" in their name:

1. /external_metadata_awareness/count_biosample_context_vals_from_postgres.py
   - Script that queries a Postgres database for biosample attribute values
   - Counts occurrences of environmental context values (env_broad_scale, env_local_scale, env_medium)
   - Uses environment variable 'BIOSAMPLES_PG_DATABASE_URL' for connection
2. /external_metadata_awareness/load_tsv_into_postgres.py
   - Loads TSV files into Postgres tables
   - Uses pandas to read TSV and SQLAlchemy to load into database
   - Also uses 'BIOSAMPLES_PG_DATABASE_URL' environment variable

Files that mention Postgres:

1. /external_metadata_awareness/sql_to_tsv.py
   - Executes SQL from file against a Postgres database
   - Outputs results to TSV
   - Uses the same environment variable for connection
2. /Makefiles/ncbi_schema.Makefile
   - Contains a target to generate context value counts using the count-biosample-context-vals-from-postgres script
   - Target: local/ncbi-biosamples-context-value-counts.csv
3. /CLAUDE.md
   - Mentions PostgreSQL as "Deprecated" in the database technologies section
   - Notes it's "being phased out in favor of MongoDB-centered processing"
4. /unorganized/PRODUCT_STATUS.md and /unorganized/README_root.md
   - Also contain references to Postgres, likely in documentation

Key insights:

- Postgres appears to be a legacy system in this codebase
- CLAUDE.md explicitly states it's deprecated
- All scripts use the same environment variable 'BIOSAMPLES_PG_DATABASE_URL'
- The scripts primarily deal with biosample data and environmental context values
- No Jupyter notebooks were found that use Postgres
- The functionality is being migrated to MongoDB based on documentation

SQLite Database Files

1. Cache Files in Root Directory:
   - /my_cache.sqlite: General request cache
   - /new_env_triad_values_splitter_cache.sqlite: Cache for the env triad values splitter
   - /requests_cache.sqlite: Cache for web requests
2. Ontology Databases:
   - /lexmatch-shell-scripts/env_triad_pvs_sheet.db
   - /lexmatch-shell-scripts/nmdc.db
   - /metpo/mpo_v0.74.en_only.db: Metadata object database
   - /metpo/n4l_merged.db: Name for Life merged database
3. Other SQLite Databases:
   - /notebooks/studies_exploration/ncbi_annotation_mining/requests_cache.sqlite: Cache for a specific notebook

SQLite Usage Patterns

1. OAK Adapter Pattern:
   - Most common usage is through OAK adapters with sqlite:obo:envo syntax
   - Used for accessing ontology data
   - Example: my_adapter = get_adapter("sqlite:obo:envo")
   - This pattern appears in multiple files, including:
    - /external_metadata_awareness/new_env_triad_values_splitter.py
    - /external_metadata_awareness/new_env_triad_oak_annotator.py
    - /external_metadata_awareness/extract_value_set_evidence.py
2. Direct SQLite API Usage:
   - Found in /external_metadata_awareness/sem_sql_combine.py
   - Uses the standard Python sqlite3 library
   - Implements database merging with deduplication
   - Only file that imports sqlite3 directly
3. Request Caching:
   - Several files use SQLite-based request caching
   - Most use the requests_cache library
   - Example: Import requests_cache in new_env_triad_values_splitter.py
4. Makefile Integration:
   - Makefiles extensively use OAK commands with SQLite adapters
   - Example in envo.Makefile: runoak --input sqlite:obo:envo
   - Used for extracting relationships, metadata, and visualization

Key Documentation References

The CLAUDE.md file describes SQLite usage in three main contexts:

1. OAK Adapters:
   - sqlite:obo:envo: Environmental Ontology adapter
   - sqlite:obo:po: Plant Ontology adapter
   - Used for text annotation and CURIE lookup
2. Local Ontology Files:
   - local/envo.db: Environmental Ontology database
   - local/goldterms.db: GOLD ontology database
   - Used for ecosystem path mappings
3. Caching:
   - Various cached SQLite files for lexical matching operations
   - Web request caching for performance

Role in the Architecture

SQLite serves three primary roles in this codebase:

1. Ontology Access: The OAK library uses SQLite for efficient ontology data access
2. Caching: Web requests and other operations are cached in SQLite for performance
3. Local Data Storage: Used for storing intermediate datasets during analysis

Unlike PostgreSQL (which is deprecated according to CLAUDE.md), SQLite appears to be an actively used and integral part
of the workflow, particularly for accessing ontology data through the OAK library.


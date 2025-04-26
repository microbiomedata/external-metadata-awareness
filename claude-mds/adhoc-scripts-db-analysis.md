# Ad-hoc Scripts Database Connection Analysis

## Updated MongoDB Connection Pattern

The updated MongoDB connection pattern centralizes connection handling through the `mongodb_connection.py` utility. This module provides:

- Consistent URI-based connection handling
- Proper authentication and credentials management
- Support for environment variables via `.env` files
- Improved error handling

The utility function `get_mongo_client()` is designed to be the single point of MongoDB connection creation.

## Core Scripts Updated to Use the New Pattern

The following scripts have been updated to use the new MongoDB connection utility:

1. **new_env_triad_values_splitter.py**:
   - Updated to use `get_mongo_client` instead of direct `MongoClient` calls
   - Simplified connection parameters to use standard URI and env_file approach
   - Added proper database name extraction from URI using `uri_parser`

2. **sra_parquet_to_mongodb.py**:
   - Replaced custom password handling with standardized connection utility
   - Simplified command-line parameters for consistent interface
   - Added verbose flag for connection diagnostics

## Makefile Integration

The Makefile has been updated to support the new connection pattern with the following key additions:

```makefile
# Default MongoDB URI
MONGO_URI ?= mongodb://localhost:27017/ncbi_metadata

# Optional environment file (user must set ENV_FILE externally if they want it)
ifdef ENV_FILE
  ENV_FILE_OPTION := --env-file $(ENV_FILE)
endif
```

New flexible targets support optional row limits through conditional parameters:

```makefile
# SRA Parquet collection variables
SRA_PARQUET_MAX_ROWS ?=

# Define row limit option if SRA_PARQUET_MAX_ROWS is set
ifdef SRA_PARQUET_MAX_ROWS
  SRA_PARQUET_ROWS_OPTION := --nrows $(SRA_PARQUET_MAX_ROWS)
endif

load-sra-parquet-to-mongo: local/sra_metadata_parquet
  @date
  @echo "Using MONGO_URI=$(MONGO_URI)"
  $(RUN) sra-parquet-to-mongodb \
      --parquet-dir $< \
      --drop-collection \
      --progress-interval 1000 \
      --mongo-uri "$(MONGO_URI)" \
      --mongo-collection sra_metadata \
      $(SRA_PARQUET_ROWS_OPTION) \
      $(ENV_FILE_OPTION) \
      --verbose
  @date
```

## Ad-hoc Scripts Database Usage Analysis

All scripts in the `adhoc` directory avoid using PyMongo or direct MongoDB connections. These appear to be purpose-built utility scripts for specific one-off tasks:

1. **nmdc_collection_stats.py**: Uses the NMDC API and pandas for data handling, no database connections
2. **list_public_gcp_bq_databases.py**: Uses Google BigQuery client, not MongoDB
3. **dict_print_biosamples_from_efetch.py**: Uses the NCBI E-utilities API (REST), no database
4. **extract_left_bioproject_by_accession.py**: Processes XML files directly, no database
5. **random_sample_resources.py**: Processes JSON files, no database
6. **infer_first_committer.py**: Uses GitHub API, no database
7. **gsheets_helper.py**: Uses Google Sheets API, no database
8. **detect_curies_in_subset.py**: Processes TSV files with pandas, no database
9. **cborg_test.py**: Tests OpenAI API access, no database

### Alternative Data Access Patterns in Ad-hoc Scripts:

1. **File-based Processing**: Most scripts work directly with files (XML, JSON, TSV, CSV)
2. **APIs**: Several scripts use REST APIs (NCBI Entrez, GitHub, Google Sheets)
3. **BigQuery**: One script (`list_public_gcp_bq_databases.py`) connects to Google BigQuery
4. **Pandas**: Many scripts use pandas for data manipulation without database connections

The `adhoc` directory appears to be a collection of specialized utility scripts, each operating independently from the main database infrastructure. They don't share a common database connection pattern, as each script is tailored to a specific data source or processing need, without requiring MongoDB access.

## Next Steps for MongoDB Connection Standardization

To complete the standardization of MongoDB connections:

1. Update any remaining scripts that directly use `pymongo.MongoClient`
2. Convert scripts with hardcoded host/port parameters to use URI-based connections
3. Update CLI arguments in older scripts to match the new pattern (`--mongo-uri` and `--env-file`)
4. Consider adding database and collection name defaults in the Makefile for more consistency

This will ensure all database connections are managed through a single, consistent pattern across the codebase.
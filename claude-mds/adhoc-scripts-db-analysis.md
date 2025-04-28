# Ad-hoc Scripts and Database Operations

## Updated MongoDB Connection Pattern

The updated MongoDB connection pattern centralizes connection handling through the `mongodb_connection.py` utility. This module provides:

- Consistent URI-based connection handling
- Proper authentication and credentials management
- Support for environment variables via `.env` files
- Improved error handling

The utility function `get_mongo_client()` is designed to be the single point of MongoDB connection creation.

## MongoDB Collection Dependencies

### Scripts in `mongo-js/needs_prerequisites`

#### `measurement_evidence_by_harmonized_name.js`

**Depends on:** `biosamples_measurements` collection

**Creation path:**
1. `biosamples` (original collection)
2. `biosamples_flattened` (created by `flatten_biosamples.js` in `mongo-js/`)
3. `biosamples_measurements` (created by `normalize_biosample_measurements.py`)

**How to create the prerequisite collection:**
```bash
# First ensure biosamples_flattened exists
poetry run mongo-js-executor --mongo-uri "mongodb://localhost:27017/ncbi_metadata" --js-file mongo-js/flatten_biosamples.js

# Then create biosamples_measurements
poetry run normalize-biosample-measurements
```

**Parameters for `normalize_biosample_measurements.py`:**
- `--mongodb-uri` (default: 'mongodb://localhost:27017/ncbi_metadata')
- `--input-collection` (default: 'biosamples_flattened')
- `--output-collection` (default: 'biosamples_measurements')
- `--field` (can be specified multiple times)

**Notes:**
- The `biosamples_flattened` collection creation is also included in `Makefiles/env_triads.Makefile`
- Full dependency chain: biosamples → biosamples_flattened → biosamples_measurements → measurement_evidence_by_harmonized_name

## SRA Biosample-Bioproject Extraction

A MongoDB aggregation-based solution has been implemented to efficiently extract biosample-bioproject pairs from SRA metadata:

```javascript
// mongo-js/extract_sra_biosample_bioproject_pairs_simple.js
db.sra_metadata.aggregate([
    // Match documents with both biosample and bioproject fields
    { $match: { 
        biosample: { $exists: true, $ne: null },
        bioproject: { $exists: true, $ne: null }
    }},
    
    // Project just what we need
    { $project: {
        _id: 0,
        biosample_accession: "$biosample",
        bioproject_accession: "$bioproject"
    }},
    
    // Group to get distinct pairs
    { $group: {
        _id: { 
            biosample: "$biosample_accession", 
            bioproject: "$bioproject_accession" 
        },
        biosample_accession: { $first: "$biosample_accession" },
        bioproject_accession: { $first: "$bioproject_accession" }
    }},
    
    // Write results to a new collection
    { $out: "sra_biosamples_bioprojects" }
], { allowDiskUse: true });
```

This approach:
1. Extracts distinct pairs directly from MongoDB without intermediate files
2. Uses MongoDB's $out operator to write results to the target collection
3. Maintains a clean and simple aggregation pipeline
4. Creates appropriate indices for query optimization
5. Is compatible with all MongoDB versions

The script is available via a Makefile target:
```makefile
make -f Makefiles/sra_metadata.Makefile extract-sra-biosample-bioproject-pairs
```

This solution is significantly more efficient than the previous BigQuery extraction approach, especially for large SRA datasets.

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
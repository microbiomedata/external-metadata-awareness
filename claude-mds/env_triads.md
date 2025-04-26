# Environmental Triads Processing Pipeline

This document outlines the complete process to create the environmental triad collection from a raw biosamples collection in MongoDB.

## Pipeline Steps Overview

1. **Populate biosamples collection**
   - `load-biosamples-into-mongo` makefile target, which uses `xml-to-mongo` (alias for `xml_to_mongo.py`)
   - Downloads and processes NCBI BioSample XML data

2. **Build biosamples_flattened collection**
   - `biosamples-flattened` makefile target, which uses `mongo-js-executor` with `flatten_biosamples.js`
   - Flattens hierarchical biosamples into tabular structure with environmental context fields
   - Creates indices for performance optimization

3. **Extract unique environmental triad values**
   - `env-triad-value-counts` makefile target, which uses `mongo-js-executor` with `enriched_biosamples_env_triad_value_counts_gt_1.js`
   - Extracts values that appear in at least 2 biosamples
   - Filters out missing data indicators, digits-only values, etc.

4. **Split environmental triad values**
   - Uses `env-triad-values-splitter` (alias for `new_env_triad_values_splitter.py`)
   - Parses values to extract CURIEs and components
   - Requires BioPortal API key in local/.env file
   - Fastest step (<1 minute) but requires expanded_envo_po_lexical_index.yaml for best results

5. **Generate label components**
   - Uses `mongo-js-executor` with `aggregate_env_triad_label_components.js`
   - Creates env_triad_component_labels collection
   - Indexes label_digits_only and label_length fields

6. **Annotate with OAK (Ontology Access Kit)**
   - Uses `env-triad-oak-annotator` (alias for `new_env_triad_oak_annotator.py`)
   - Processes labels through local ontology lookup
   - Fast, entirely local process (~3 minutes)

7. **Annotate with OLS (Ontology Lookup Service)**
   - Uses `env-triad-ols-annotator` (alias for `new_env_triad_ols_annotator.py`)
   - Processes labels through the EBI OLS web service
   - Much slower without cache (7 hours vs 7 minutes with cache)

8. **Extract CURIEs**
   - Uses `mongo-js-executor` with `aggregate_env_triad_curies.js`
   - Creates env_triad_component_curies_uc collection
   - Deals with ENV, ENV0, NCIT, SNOMED/SNOMEDCT

9. **Validate CURIEs with SemSQL**
   - Uses `env-triad-check-semsql-curies` (alias for `new_check_semsql_curies.py`)
   - Adds label and obsolete status to ENVO, PO, and other CURIEs

10. **Map CURIEs with BioPortal**
    - Uses `env-triad-bioportal-curie-mapper` (alias for `new_bioportal_curie_mapper.py`)
    - Maps CURIEs to related terms via BioPortal API
    - Adds mappings to the collection
    - Faster with cache (2 minutes vs 13 minutes without)

11. **Populate final env_triads collection**
    - Uses `populate-env-triads-collection` (alias for `populate_env_triads_collection.py`)
    - Creates the final structured collection with all annotations
    - Creates appropriate indices
    - Takes approximately 30 minutes plus 6 minutes for indexing

## Starting from a Fresh Biosamples Collection

If you have a raw biosamples collection in MongoDB with no indices besides _id_, you can run the entire pipeline with:

```bash
# Using default MongoDB connection
make -f Makefiles/env_triads.Makefile env-triads

# With custom MongoDB URI and credentials from .env file
make -f Makefiles/env_triads.Makefile env-triads MONGO_URI="mongodb://custom-host:27017/ncbi_metadata" ENV_FILE=local/.env
```

The env-triads makefile target depends on:
1. biosamples-flattened - Flattens the biosamples collection
2. env-triad-value-counts - Extracts unique values with counts

These prerequisites will run automatically as part of the make process.

## Performance Expectations

- **Flattening biosamples**: ~30 minutes for ~45 million biosamples
- **Extracting values**: ~3 minutes
- **Splitting values**: <1 minute
- **OAK annotation**: ~3 minutes
- **OLS annotation**: ~7 minutes with cache, ~7 hours without
- **BioPortal mapping**: ~2 minutes with cache, ~13 minutes without
- **Populating final collection**: ~30 minutes + 6 minutes for indexing

Total process time: ~1.5 hours with cache, ~9 hours without

## Requirements for BioPortal API

You need a BioPortal API key in a `local/.env` file with the following format:

```
BIOPORTAL_API_KEY=your-api-key-here
```

This key is used for both the env-triad-values-splitter and env-triad-bioportal-curie-mapper steps.

## Notes

- The process requires significant memory, especially during the MongoDB aggregation steps
- 32GB RAM is recommended for processing the full NCBI biosamples collection
- If memory becomes an issue, consider running on a more powerful machine
- All Python scripts use the mongodb_connection.py module for consistent connection handling
- The updated Makefile handles MongoDB operations in two ways:
  - JavaScript files are executed with mongosh via mongo-js-executor
  - Direct MongoDB commands use PyMongo's native methods

## Authentication and Connection Handling

The pipeline supports both authenticated and unauthenticated MongoDB connections:

1. **Without authentication**: Simply run the makefile targets without an ENV_FILE parameter.

2. **With authentication**: Create an environment file (e.g., `local/.env`) with:
   ```
   MONGO_USER=username
   MONGO_PASSWORD=password
   BIOPORTAL_API_KEY=your-api-key-here  # Required for some steps
   ```

3. **Missing credentials**: If you provide an ENV_FILE that doesn't contain MONGO_USER and MONGO_PASSWORD, the pipeline will continue with an unauthenticated connection.

All commands use the same connection handling logic from mongodb_connection.py, ensuring consistent behavior across the pipeline.


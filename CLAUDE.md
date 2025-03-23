# External Metadata Awareness Commands and Guidelines

## Build & Run Commands
- Poetry: `poetry run python external_metadata_awareness/script_name.py` or `poetry run script-alias`
- Makefiles: `make -f Makefiles/target.Makefile target_name`
- Primary Makefile commands: `make duck-all`, `make purge`, etc.
- Run notebooks: `poetry run jupyter notebook`

## Environmental Context Voting Sheets - Quickstart
This repository includes tooling to generate environmental triad (environmental context) voting sheets for standardizing environmental metadata.

### Overview
- **Purpose**: Generate structured voting sheets for environmental contexts (env_broad_scale, env_local_scale, env_medium)
- **Primary Files**: Find everything in `notebooks/environmental_context_value_sets/`
- **Config**: `voting_sheets_configurations.yaml` defines environments and context slots
- **Main Notebook**: `generate_voting_sheet.ipynb` orchestrates the entire process

### Running the Pipeline
1. Start Jupyter: `poetry run jupyter notebook`
2. Open `notebooks/environmental_context_value_sets/generate_voting_sheet.ipynb`
3. Ensure DuckDB file (`ncbi_biosamples_*.duckdb`) is available
4. Run all cells to generate voting sheets in `voting_sheets_output/`

### Data Flow
1. Load biosamples data from NMDC, GOLD, and NCBI sources
2. Predict environmental packages using ML model (F1≈0.99)
3. Extract CURIEs and normalize environmental context values
4. Generate voting sheets with boolean classification columns
5. Output TSVs for domain expert review

### Review Process and Value Set Construction
1. TSV files are shared as Google Sheets for collaborative review
2. Reviewers add columns with their initials for voting (+1/-1) and comments
3. Completed sheets are submitted to Mark/Montana for vote compilation
4. Results are used to:
   - Create final environmental context value sets
   - Inject into submission-schema repo as LinkML enumerations (PR #260)
   - Eventually add `in_subset` assertions in ontologies like EnvO

## Cross-Repository Integration with submission-schema

### Process Flow Between Repositories
1. **external-metadata-awareness**: Generates voting sheets from biosample data analysis
2. **submission-schema**: Receives and processes voted terms into LinkML enumerations

### Ontology Term Selection Guidelines
When evaluating environmental terms for inclusion in voting sheets:

1. **Semantic Clarity**: Terms should have clear, unambiguous definitions
2. **Ontological Positioning**: Prefer terms properly positioned in their ontology hierarchy
3. **Community Acceptance**: Prioritize terms accepted by relevant scientific communities
4. **Granularity Balance**: Choose terms specific enough to be useful but not overly granular
5. **FAIR Principles**: Prefer terms from ontologies following FAIR principles

### Extending to New Environments
When planning to add new environmental contexts beyond soil, water, sediment, and plant-associated:

1. **Initial Research**: Explore term availability in EnvO or other relevant ontologies
2. **Gap Analysis**: Identify where existing ontology terms might be insufficient
3. **Stakeholder Input**: Engage domain experts before creating voting sheets
4. **Configuration Update**: Add new environment type to `voting_sheets_configurations.yaml`
5. **Naming Conventions**: Follow established naming patterns:
   - Voting sheets: `[environment]_env_[scale]_voting_sheet`
   - Output files: `post_google_sheets_[environment]_env_[scale].tsv`
   - Enumerations (in submission-schema): `Env[Scale][Environment]Enum`

### Data Format Standards
For consistent integration between repositories:

1. **Term Format**: Use the pattern `term_name [term_id]` for all ontology terms
2. **CURIE Standards**: Follow consistent CURIE format (e.g., ENVO:00002297)
3. **Vote Aggregation**: Sum threshold ≥1 is typically used for term inclusion
4. **TSV Format**: Maintain consistent column headers for compatibility with submission-schema scripts

### Sustainability Considerations
To ensure maintained alignment between repositories:

1. **Version Tracking**: Document which versions of source ontologies were used
2. **Term Deprecation**: Establish processes for updating when ontology terms become deprecated
3. **Pipeline Testing**: Test full pipeline from term selection through schema integration
4. **Reproducibility**: Document thresholds and criteria used for each voting round

## MongoDB Infrastructure

### Servers
- **Development Server**: `localhost:27017` (default MongoDB port)
- **NMDC Server**: `localhost:27777` (with authentication required)

### Primary Databases (Code References)
The codebase references these primary databases:

1. **ncbi_metadata**
   - Main database storing NCBI-related data
   - Used extensively throughout the codebase

2. **biosamples_dev**
   - Development/testing database  
   - Used in early development and testing scripts
   - Not present in current database instance

3. **nmdc**
   - External NMDC MongoDB database
   - Accessed with authentication credentials

### Collections Referenced in Code

#### In ncbi_metadata Database (Expected Structure)

##### Core Collections:
- **biosamples**: Primary storage for NCBI BioSample XML data
- **biosample_harmonized_attributes**: Flattened BioSample attributes
- **class_label_cache**: Cached ontology class labels
- **unique_triad_values**: Extracted unique environmental triad values
- **triad_components_labels**: Labels for environmental context components
- **compact_mined_triads**: Optimized storage of environmental triads with CURIEs (not found in current instance)

##### BioProject Collections:
- **bioprojects**: BioProject data (~893,527 documents, ~1.59GB raw)
- **bioprojects_submissions**: Submission metadata (~893,527 documents, ~695MB raw)

##### Relationships:
- **sra_biosamples_bioprojects**: Relational data linking SRA, BioSamples, and BioProjects

##### Other Collections:
- **filtered_sra_metadata**: Filtered SRA metadata from BigQuery
- **etl_log**: Logging of data download dates and processing events (not found in current instance)

### Actual Database Statistics

Current MongoDB instance contains several databases with substantial data volumes:

#### 1. ncbi_metadata (24944.00 MB)
- **biosamples**: 44,376,624 documents (117214.77 MB, avg: 2.70 KB)
- **biosample_harmonized_attributes**: 44,376,624 documents (15174.80 MB, avg: 0.35 KB)
- **class_label_cache**: 10,585 documents (2.14 MB, avg: 0.21 KB)
- **unique_triad_values**: 191,970 documents (78.54 MB, avg: 0.42 KB)
- **triad_components_labels**: 46,519 documents (4.28 MB, avg: 0.09 KB)
- **bioprojects**: 893,527 documents (1516.02 MB, avg: 1.74 KB)
- **bioprojects_submissions**: 893,527 documents (703.14 MB, avg: 0.81 KB)
- **sra_biosamples_bioprojects**: 29,128,964 documents (2722.20 MB, avg: 0.09 KB)
- **filtered_sra_metadata**: 2,724,015 documents (8204.37 MB, avg: 3.08 KB)
- **simons_wishlist**: 61,599 documents (253.89 MB, avg: 4.22 KB)
- **packages**: 228 documents (0.14 MB, avg: 0.61 KB)

#### 2. biosamples (28608.75 MB)  
- **sra_metadata**: 34,953,268 documents (108105.45 MB, avg: 3.17 KB)
- **metagenomic_wgs_metadata**: 972,718 documents (3259.04 MB, avg: 3.43 KB)

#### 3. gold_metadata (86.89 MB)
- **studies**: 4,697 documents (6.36 MB, avg: 1.39 KB)
- **projects**: 221,079 documents (233.57 MB, avg: 1.08 KB)
- **biosamples**: 216,758 documents (321.72 MB, avg: 1.52 KB)

#### 4. nmdc (1621.52 MB)
- **biosample_set**: 9,349 documents (15.56 MB, avg: 1.70 KB)
- **functional_annotation_agg**: 20,027,853 documents (3133.95 MB, avg: 0.16 KB)
- **data_object_set**: 112,397 documents (50.69 MB, avg: 0.46 KB)
- **workflow_execution_set**: 13,019 documents (376.44 MB, avg: 29.61 KB)
- Plus 15+ additional collections for various data types

#### 5. misc_metadata (5.42 MB)
- **submission_biosample_rows**: 19,312 documents (22.81 MB, avg: 1.21 KB)
- **nmdc_submissions**: 321 documents (12.86 MB, avg: 41.03 KB)

### Load Balancer Instance Database Statistics (mongo-ncbi-loadbalancer)

For comparison, the mongo-ncbi-loadbalancer instance contains the following:

#### 1. ncbi_metadata (49729.38 MB)
- **biosamples**: 43,169,967 documents (114155.03 MB, avg: 2.71 KB)
- **compact_mined_triads**: 43,169,967 documents (20419.22 MB, avg: 0.48 KB)
- **sra_metadata**: 31,413,414 documents (73866.97 MB, avg: 2.41 KB)
- **sra_biosamples_bioprojects**: 29,128,964 documents (2722.20 MB, avg: 0.09 KB)
- **bioprojects**: 880,412 documents (1493.05 MB, avg: 1.74 KB)
- **bioprojects_submissions**: 880,411 documents (653.64 MB, avg: 0.76 KB)
- **simons_wishlist**: 61,599 documents (253.89 MB, avg: 4.22 KB)

#### 2. gold_metadata (88.29 MB)
- **biosamples**: 216,758 documents (321.72 MB, avg: 1.52 KB)
- **projects**: 221,079 documents (233.57 MB, avg: 1.08 KB)
- **studies**: 4,697 documents (6.36 MB, avg: 1.39 KB)
- **notes**: 2 documents (0.00 MB, avg: 0.08 KB)

#### 3. misc_metadata (5.60 MB)
- **submission_biosample_rows**: 19,312 documents (22.81 MB, avg: 1.21 KB)
- **nmdc_submissions**: 321 documents (12.86 MB, avg: 41.03 KB)
- **notes**: 1 documents (0.00 MB, avg: 0.09 KB)

### Comparison Between Instances

1. **Structural Differences**:
   - **compact_mined_triads**: Present in loadbalancer (43.1M documents) but missing from local instance
   - **SRA Data Organization**: Loadbalancer has SRA metadata in ncbi_metadata.sra_metadata, while local instance uses a separate biosamples database
   - **Analysis Collections**: Local instance has several additional collections (biosample_harmonized_attributes, class_label_cache, unique_triad_values, triad_components_labels) not present in loadbalancer
   - **Database Size**: Loadbalancer ncbi_metadata is nearly twice as large (49.7GB vs 24.9GB)

2. **Development vs. Production**:
   - Loadbalancer appears more consolidated with fewer normalized tables
   - Local instance contains more intermediate and analytical collections
   - Both share similar core data volumes despite structural differences
   - GOLD and misc_metadata databases are nearly identical across instances

3. **Pipeline Implications**:
   - Local instance might be missing the final compact_mined_triads generation step
   - Local instance appears optimized for analysis while loadbalancer for retrieval
   - The code references match the loadbalancer structure for critical collections

## DuckDB and SQLite Database Usage

### Primary DuckDB Files
1. **ncbi_biosamples.duckdb**
   - Main database storing NCBI biosample data extracted from MongoDB
   - Generated by `mongodb_biosamples_to_duckdb.py`
   - Path: `local/ncbi_biosamples.duckdb`
   - Created by `make duck-all` in `ncbi_metadata.Makefile`

2. **ncbi_biosamples_YYYY-MM-DD.duckdb**
   - Date-stamped versions used in notebooks
   - Referenced in `notebooks/environmental_context_value_sets/generate_voting_sheet.ipynb`
   - Used as source for voting sheet generation

### DuckDB Tables
1. **Core Tables**
   - `normalized_context_strings`: Normalized environmental context values
   - `curies_asserted`: CURIEs extracted directly via regex
   - `curies_ner`: CURIEs identified via text annotation
   - `curie_free_strings`: Context strings with CURIEs removed
   - `ncbi_package_info`: NCBI biosample package metadata

2. **Analytical Tables**
   - `etl_log`: Processing metadata, download dates
   - `ontology_class_candidates`: CURIEs for environmental context options
   - `normalized_context_content_count`: Frequency counts of normalized values

### SQLite Ontology Files
1. **OAK Adapters**
   - `sqlite:obo:envo`: Environmental Ontology adapter
   - `sqlite:obo:po`: Plant Ontology adapter
   - Used for text annotation and CURIE lookup

2. **Local Ontology Files**
   - `local/envo.db`: Environmental Ontology database
   - `local/goldterms.db`: GOLD ontology database 
   - Used for GOLD ecosystem path mappings

3. **Other SQLite Files**
   - `notebooks/studies_exploration/ncbi_annotation_mining/requests_cache.sqlite`: Web request cache for performance
   - Various cached SQLite files for lexical matching operations

### Database Technologies for Biosample CURIE Mapping
The repository uses multiple database technologies for managing environmental triads:

1. **MongoDB** (Primary Storage)
   - Primary database for biosample storage with environmental context values
   - Collections listed above handle various aspects of the data workflow
   - Future emphasis will shift to in-MongoDB environmental triad mapping, normalization, and NER

2. **DuckDB** (Analytical Processing)
   - Used for preparing and generating voting sheets
   - Tables for normalized values, extracted CURIEs, and annotation results
   - DuckDB enhancement work in progress (PR #32)

3. **PostgreSQL** (Deprecated)
   - Previously used for some operations but now mostly deprecated
   - Being phased out in favor of MongoDB-centered processing

The workflow for environmental triad mapping is evolving toward greater use of OAK adapters for direct text annotation within MongoDB, reducing the need for data migration between systems.

### MongoDB Operations
- `make purge` drops the entire MongoDB database (`ncbi_metadata`) but not individual collections
- To clear individual collections: `mongosh --eval "db.getSiblingDB('ncbi_metadata').collection_name.drop()"`
- Most data load scripts don't clear collections before inserting new data
- For `load_acceptable_sized_leaf_bioprojects_into_mongodb.py`, manually clear collections first:
  ```
  mongosh --eval "db.getSiblingDB('ncbi_metadata').bioprojects.drop()"
  mongosh --eval "db.getSiblingDB('ncbi_metadata').bioprojects_submissions.drop()"
  ```
- Oversized documents are saved to `local/oversize/projects/` and `local/oversize/submissions/`

### BioProjects Loading Performance Notes
- Processing speed: Complete XML file (~893,527 records) processed in ~15 minutes
- Final counts:
  - Projects: 893,525 normal + 2 oversized = 893,527 total
  - Submissions: 893,526 normal + 1 oversized = 893,527 total
- MongoDB collection statistics:
  - bioprojects collection:
    - Document count: 893,527
    - Raw size: 1,589,661,089 bytes (~1.59GB)
    - Storage size with compression: 565,919,744 bytes (~566MB)
    - Total size with indexes: 579,997,696 bytes (~580MB)
    - Average document size: 1,779 bytes
    - Index size: 14,077,952 bytes (~14MB)
  - bioprojects_submissions collection:
    - Document count: 893,527 
    - Raw size: 695,331,767 bytes (~695MB)
    - Storage size with compression: 155,648,000 bytes (~156MB)
    - Total size with indexes: 169,717,760 bytes (~170MB)
    - Average document size: 778 bytes
    - Index size: 14,069,760 bytes (~14MB)
- Oversized files:
  - Projects: PRJNA230403 (28MB), PRJNA514245 (65MB)
  - Submission: 35MB (without submission ID)
- Oversized files are very rare (only 3 out of ~893,527 records)
- First oversized entity detected in early processing

## Code Style Guidelines
- Python >= 3.10 required
- Type hints expected (use `from typing import List, Dict, Tuple, Optional`)
- Use docstrings for functions/classes (Google style preferred)
- Click library for CLI commands
- Environment variables in .env files (load with dotenv)
- Exception handling with specific exceptions
- Snake case for variables/functions (e.g., `calculate_value`)
- Log, don't print (except for CLI tool output)
- Classes use PascalCase

## Project Structure
- Package scripts via poetry.scripts in pyproject.toml
- Data processing tools primarily using pandas, duckdb, and MongoDB
- Configuration in YAML files where applicable

## XML Processing Workflow

### XML Data Sources

1. **Core XML Files**
   - **BioSamples XML**: `biosample_set.xml.gz` from NCBI FTP (~3GB, ~45 million samples)
   - **BioProjects XML**: `bioproject.xml` from NCBI FTP (~3GB, ~893,527 projects) 
   - **Package Definitions**: `ncbi-biosample-packages.xml` defining metadata standards
   - **Attributes XML**: XML defining available attributes for BioSamples

### XML Processing Pipeline

1. **Download**: Files fetched via `wget` from NCBI FTP servers
   ```
   wget -O downloads/biosample_set.xml.gz "https://ftp.ncbi.nlm.nih.gov/biosample/biosample_set.xml.gz"
   ```

2. **Parse and Load**: XML transformed to nested documents in MongoDB
   - Uses `lxml.etree.iterparse` for memory-efficient streaming
   - `xml_to_mongo.py` converts XML elements to nested dictionaries
   - Oversized documents (>16MB) saved as files with references in MongoDB

3. **Structure Analysis**:
   - `count_xml_paths.py` analyzes XML structure and frequency
   - Counts distributions of elements and attributes

4. **Extraction and Transformation**:
   - `mongodb_biosamples_to_duckdb.py` flattens XML structure
   - Creates tabular representations in DuckDB tables
   - Special focus on environmental context attributes

### Environmental Context Extraction

XML files are the primary source of environmental metadata:
- Environmental context fields (env_broad_scale, env_local_scale, env_medium)
- Package types (soil, water, plant-associated, sediment)
- Harmonized attributes containing ontology references

### Key XML Processing Tools

- `xml_to_mongo.py`: Primary XML loading script
- `load_acceptable_sized_leaf_bioprojects_into_mongodb.py`: BioProject XML handler
- `extract_all_ncbi_packages_fields.py`: Package information extractor
- `mongodb_biosamples_to_duckdb.py`: XML to tabular converter

## External Data Fetching

### Primary Data Sources

1. **NCBI Repositories**
   - **BioSamples XML**: Downloaded via `wget` from `ftp.ncbi.nlm.nih.gov/biosample/biosample_set.xml.gz` (~3GB)
   - **BioProjects XML**: Downloaded via `wget` from `ftp.ncbi.nlm.nih.gov/bioproject/bioproject.xml` (~3GB)
   - **Package Definitions**: Fetched from `ncbi.nlm.nih.gov/biosample/docs/packages/?format=xml`
   - **E-utilities API**: `eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi` for fetching specific BioSamples

2. **Ontology Data**
   - **OBO Foundation Metadata**: From `raw.githubusercontent.com/OBOFoundry/OBOFoundry.github.io`
   - **MIxS Schema**: Via `raw.githubusercontent.com/GenomicsStandardsConsortium/mixs`
   - **BioPortal API**: `data.bioontology.org` for ontology metadata and metrics

3. **Other Sources**
   - **GOLD Data**: Excel format via `gold.jgi.doe.gov/download?mode=site_excel`
   - **Google BigQuery**: SRA metadata from `nih-sra-datastore.sra.metadata`
   - **Unpaywall API**: `api.unpaywall.org/v2/{doi}` to retrieve open access PDFs

### Methods & Tools

1. **Command-line Tools in Makefiles**
   - `wget`: For large FTP XML files (primary method in Makefiles)
   - `curl`: Used in GOLD data fetching

2. **Python Libraries**
   - `requests`: For API calls to NCBI E-utilities, BioPortal, and Unpaywall
   - Google BigQuery client: For SRA metadata
   - `LXML/ElementTree`: For XML parsing

### Authentication & Headers

- **BioPortal API Key**: Referenced as `BIOPORTAL_API_KEY` in `.env` file
- **Google BigQuery**: Uses application default credentials
- **NCBI E-utilities**: Uses URL parameters for queries

### Data Pipeline Workflow

1. Initial download with wget/curl into `downloads/` directory
2. Processing and loading into MongoDB
3. Extraction to DuckDB for analysis
4. Batch processing with progress tracking for large datasets

### Notable Patterns

- No automated refresh schedules visible in the codebase
- Manual refreshes with timestamps stored in DuckDB metadata
- OAK library for ontology access with caching
- MongoDB as intermediate storage before analytical processing

## Current Loose Ends and Development Areas

### Unused Dependencies
- Several dependencies in pyproject.toml appear unused:
  - `git-filter-repo`
  - `llm`
  - `textdistance`
  - `case-converter`

### Orphaned Python Scripts
- `cborg_test.py`: Test script for CBORG API
- `dict_print_biosamples_from_efetch.py`: Standalone script not in Makefiles
- `entrez_vs_mongodb.py`: Comparison tool not used in data pipelines
- `study-image-table.py`: Uses non-standard naming convention

### Unfinished Testing Infrastructure
- `/tests/__init__.py` exists but no test files are present
- No test coverage for main functionality

### Development TODOs
The codebase contains numerous TODOs, particularly in:
- `Makefiles/ncbi_metadata.Makefile`: 18+ TODOs about architecture and improvements
- `notebooks/environmental_context_value_sets/common.py`: Questions about memory handling
- Several notebooks contain TODO comments about refactoring or optimization

### Abandoned/Transitional Components
- `notebooks/old/` directory contains superseded notebooks
- `unorganized/` directory contains documentation that may be outdated
- Several temporary files appear uncommitted in the repo

### Data Processing Improvements
The TODOs suggest several areas for improvement:
- Replacing print statements with proper logging
- More consistent MongoDB connection string handling
- Optimizing data extraction and annotation
- Better documentation of resource requirements

## MongoDB Connection Methods

This repository uses several different approaches to connect to MongoDB across scripts, notebooks, and Makefiles.

### Connection String Formats

1. **Component-Based (CLI Parameters)**
   - **Most Common Pattern**: Scripts like `xml_to_mongo.py` use separate parameters
   ```python
   @click.option('--mongo-host', default='localhost', help='MongoDB host address.')
   @click.option('--mongo-port', default=27017, type=int, help='MongoDB port.')
   ```
   - **Implementation**: `MongoClient(host=mongo_host, port=mongo_port)`
   - **Used In**: `xml_to_mongo.py`, `sra_accession_pairs_tsv_to_mongo.py`

2. **URI-Style Connection Strings**
   - **Format**: `--mongo_uri mongodb://host:port/`
   - **Implementation**: `MongoClient(mongo_uri)`
   - **Used In**: `mongodb_biosamples_to_duckdb.py`, `load_acceptable_sized_leaf_bioprojects_into_mongodb.py`
   - **Makefile Example**: `--mongo-uri mongodb://$(MONGO_HOST):$(MONGO_PORT)/`

3. **Utility Function Approach**
   - **Core Function**: `notebooks/core.py` contains `get_mongo_client()`
   - **Handles Authentication**: Optional username/password with proper auth mechanism
   - **Used In**: Some notebooks but not consistently across codebase

### Hardcoded Values

1. **Makefiles**
   - **Variables**: `MONGO_HOST=localhost`, `MONGO_PORT=27017`, `MONGO_DB=ncbi_metadata`
   - **Inconsistency**: Some scripts use `mongo_uri` with underscores, others `mongo-uri` with hyphens
   
2. **Python Scripts**
   - **Default Values**: Almost all scripts default to `localhost:27017`
   - **Database Names**: Inconsistent - `biosamples_dev`, `ncbi_metadata`, or passed as parameter
   - **TODO Comment**: Makefile contains `# todo switch to more consistent mongodb connection strings`

### Authentication Handling

1. **Most Scripts**: No authentication mechanism
2. **core.py Utility**: Proper authentication with multiple parameters
   ```python
   if username and password:
       mongo_uri = f"mongodb://{username}:{password}@{host}:{port}/"
       client = pymongo.MongoClient(
           mongo_uri,
           directConnection=direct_connection,
           authMechanism=auth_mechanism,
           authSource=auth_source
       )
   ```
3. **Environment Variables**: Some notebooks use `.env` files for credentials
   - Loading with `dotenv_values("../../../local/.env")`
   - Variables: `NMDC_MONGO_USER`, `NMDC_MONGO_PASSWORD`

### Recommendation for Consistency

The repository would benefit from:
1. Standardizing on URI-style connections with a utility function
2. Consistent parameter naming (`mongo_uri` vs `mongo-uri`)
3. Centralized authentication handling
4. Unified environment variable approach for sensitive data
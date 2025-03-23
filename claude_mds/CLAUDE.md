# NMDC Submission Schema - Guidelines for Claude

## Build/Test/Lint Commands
- Build: `make site`
- Install dependencies: `make setup` or `poetry install`
- Run all tests: `make test` or `poetry run pytest`
- Run single test: `poetry run pytest tests/test_file.py::test_function -v`
- Lint schema: `make lint` or `poetry run linkml-lint src/nmdc_submission_schema/schema/nmdc_submission_schema.yaml`
- Generate docs: `make gendoc`
- Build DataHarmonizer: `make dh-build`

## Code Style Guidelines
- **Python**: Python 3.9+ compatible code
- **Naming**: Use snake_case for variables/functions, CamelCase for classes
- **Imports**: Group standard library, third-party, and local imports
- **Error handling**: Use pytest assertions in tests, proper exception handling in application code
- **Schema development**: Always validate schema changes with `linkml-lint`
- **Environment contexts**: Use predefined patterns for environmental context values
- **Commits**: Keep focused on single issues, follow semantic versioning principles

## Environmental Triad Process
This repository manages environmental context terms through a structured voting and integration process:

### 1. Google Sheets Voting Mechanism
- Expert voting is conducted on Google Sheets for environmental context terms
- Currently tracks four environments: soil, water, sediment, and plant-associated
- Each environment has three scales: env_broad_scale, env_local_scale, and env_medium
- Experts vote +1 (include), 0 (neutral), or -1 (exclude) for each term
- Authentication uses service account credentials in `env-context-voting-sheets-*.json`

### 2. Vote Processing in Jupyter Notebooks
- Each environment-scale combination has a notebook in `notebooks/environmental_context_value_sets/`
- Notebooks follow naming pattern: `post_google_sheets_[environment]_env_[scale].ipynb`
- Terms are filtered using configurable vote sum threshold (typically ≥1)
- Results are saved as TSV files with term ID and label columns

### 3. Term Aggregation
- `genreate_env_triad_pvs_sheet.ipynb` consolidates individual TSV files
- Processes all `post_google_sheets_*.tsv` files and formats them for schema integration
- Outputs aggregated data to `env_triad_pvs_sheet.tsv`

### 4. Schema Integration
- `generate_env_triad_enums.py` converts TSV files to LinkML enumerations
- Creates permissible values in format: `term_name [term_id]`
- Enumerations follow naming pattern: `Env[Scale][Environment]Enum`
- Script maps from TSV filenames to appropriate enumeration names

### 5. Build Automation
- `ingest-triad` Makefile target integrates terms during the build process
- Watches for TSV files in the environmental_context_value_sets directory
- For each matching TSV, runs `inject-env-triad-terms` to update schema

## Technical Implementation Details

### Database and External Data Interactions
This repository has minimal database interactions:

1. **SQLite Usage in Notebooks**: 
   - OAK adapters (e.g., `envo_adapter_string = "sqlite:obo:envo"`) for accessing EnvO ontology
   - Used for analyzing class hierarchies and validating ontology terms
   - No persistent database storage beyond ontology access

2. **External Data Retrieval**: Limited to one key resource:
   - Uses `wget` in Makefile to download GOLD ecosystem tree JSON data:
     ```
     wget https://gold.jgi.doe.gov/download?mode=biosampleEcosystemsJson -O project/thirdparty/GoldEcosystemTree.json
     ```
   - Primary external data comes through Google Sheets API in notebooks

### XML/OWL Usage
The repository has minimal XML interaction:

1. **OWL Files**: 
   - Contains `env_triad_pvs_sheet.owl` and `env_triad_pvs_sheet.owl.ttl` - ontology files representing environmental triads
   - Uses ENVO OWL file as an external dependency for term validation

2. **ROBOT Templates**: 
   - The `create_env_context_robot_template.py` script generates ROBOT templates
   - Parses OWL files using RDFLib's XML parser: `graph.parse(file_path, format="xml")`
   - Creates TSV templates for asserting in-subset relationships between EnvO classes and NMDC subsets

3. **Purpose**:
   - Enables ontology annotation to mark which EnvO terms belong to which subsets
   - Part of a feedback loop to improve source ontologies with NMDC usage information

## Adding New Environments
To process additional environments beyond the current set:
1. Create appropriate Google Sheet voting tables
2. Copy and adapt existing notebooks for the new environment
3. Ensure names follow established patterns for filenames and enum names
4. The build system will automatically process new TSV files that follow the naming conventions

## Cross-Repository Integration

### Related Repository: external-metadata-awareness
The external-metadata-awareness repository is a companion project that handles the earlier stages of the environmental term pipeline:

1. **Purpose**: Generates voting sheets from biosample data analysis
2. **Technology Stack**:
   - Uses MongoDB for primary biosample storage
   - Uses DuckDB for analytical processing
   - Uses machine learning to predict environmental packages (F1≈0.99)

3. **Data Flow**:
   - Extracts environmental context values from NMDC, GOLD, and NCBI sources
   - Normalizes and extracts CURIEs
   - Generates TSV files for expert review
   - Outputs become inputs to this repository's voting process

### Process Flow Between Repositories
1. **external-metadata-awareness**: Generates voting sheets from biosample data analysis
2. **submission-schema** (this repo): Receives and processes voted terms into LinkML enumerations

### Data Format Standards
For consistent integration between repositories:
1. **Term Format**: Use the pattern `term_name [term_id]` for all ontology terms
2. **CURIE Standards**: Follow consistent CURIE format (e.g., ENVO:00002297)
3. **Vote Aggregation**: Sum threshold ≥1 is typically used for term inclusion
4. **TSV Format**: Maintain consistent column headers for compatibility with this repo's scripts

## Notes
Schema uses LinkML for modeling with YAML as the source format. Test examples thoroughly before committing changes.
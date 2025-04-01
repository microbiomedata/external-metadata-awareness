# NMDC Environmental Context Value Sets Lifecycle with MIxS Integration

This document details the complete lifecycle of NMDC environmental context value sets ("triads") across three key repositories:
1. **external-metadata-awareness** - Data extraction and voting sheet preparation
2. **submission-schema** - Integration of voted terms into LinkML schema
3. **envo** - Ontological integration of NMDC terms via inSubset annotations

## Environmental Triad Concept

The environmental triad consists of three scales of environmental context:
- **env_broad_scale**: Largest geographic context (e.g., biome)
- **env_local_scale**: Local-level environmental features
- **env_medium**: Specific material context where sampling occurs

Currently implemented for four primary environments:
- Soil
- Water
- Sediment
- Plant-associated

## Repository 1: external-metadata-awareness

### Stage 1: Data Collection

1. **Data Source Extraction**:
   - Script: `xml_to_mongo.py` loads NCBI BioSample XML data (~45 million samples) into MongoDB
   - Script: `extract_all_ncbi_packages_fields.py` extracts package information
   - Collections stored in MongoDB database `ncbi_metadata`

2. **Data Transformation**:
   - Script: `mongodb_biosamples_to_duckdb.py` converts MongoDB data to DuckDB tables
   - Creates `ncbi_biosamples_YYYY-MM-DD.duckdb` with normalized environmental context values
   - DuckDB tables include `normalized_context_strings`, `curies_asserted`, `curies_ner`

3. **Machine Learning Classification**:
   - Python notebooks predict environmental packages with F1≈0.99
   - Normalizes environmental context values and extracts CURIEs
   - Frequency analysis in DuckDB identifies most common terms

### Stage 2: Voting Sheet Generation

1. **Configuration Setup**:
   - File: `voting_sheets_configurations.yaml` defines environments and context slots
   - Notebook: `generate_voting_sheet.ipynb` orchestrates the entire process
   - Paths: `notebooks/environmental_context_value_sets/`

2. **Candidate Term Selection**:
   - Ontology adapters (OAK) used to access EnvO (`sqlite:obo:envo`)
   - Terms extracted from DuckDB tables with CURIEs identified
   - Text annotation performed for context strings without explicit CURIEs

3. **Sheet Generation**:
   - Output location: `voting_sheets_output/`
   - File pattern: `[environment]_env_[scale]_voting_sheet.tsv`
   - Sheets shared as Google Sheets using service account credentials in `env-context-voting-sheets-*.json`

### Stage 3: Expert Voting

1. **Voting Process**:
   - Google Sheets shared with domain experts
   - Experts vote +1 (include), 0 (neutral), -1 (exclude) for each term
   - Reviewers add columns with their initials for voting (e.g., `PLB+1`, `XX-1`)

2. **Vote Collection**:
   - Completed sheets collected by project coordinators
   - Sheets downloaded as TSVs for further processing
   - Common vote threshold: ≥1 (sum of all expert votes)

## Repository 2: submission-schema

### Stage 4: Vote Processing

1. **Notebook Processing**:
   - Directory: `notebooks/environmental_context_value_sets/`
   - File pattern: `post_google_sheets_[environment]_env_[scale].ipynb`
   - Example: `post_google_sheets_soil_env_broad_scale.ipynb`

2. **Term Filtering**:
   - Terms with vote sums ≥1 are kept
   - Code snippet (from notebooks):
   ```python
   # Filter terms based on vote threshold
   vote_columns = [col for col in df.columns if col.endswith('+1') or col.endswith('-1')]
   df['vote_sum'] = df[vote_columns].sum(axis=1)
   filtered_df = df[df['vote_sum'] >= 1]
   ```

3. **Term Aggregation**:
   - Notebook: `generate_env_triad_pvs_sheet.ipynb`
   - Consolidates all `post_google_sheets_*.tsv` files
   - Outputs: `env_triad_pvs_sheet.tsv`, `env_triad_pvs_sheet.owl`, `env_triad_pvs_sheet.owl.ttl`

### Stage 5: Schema Integration

1. **Enumeration Generation**:
   - Script: `generate_env_triad_enums.py`
   - Creates LinkML enumerations with naming pattern: `Env[Scale][Environment]Enum`
   - Example: `EnvBroadScaleSoilEnum`, `EnvLocalScaleWaterEnum`, `EnvMediumSedimentEnum`

2. **Permissible Value Format**:
   - Terms stored in format: `term_name [term_id]`
   - Example: `oceanic epipelagic zone biome [ENVO:01000033]`
   - Code snippet:
   ```python
   pv = PermissibleValue(text=f"{label} [{curie}]")
   ```

3. **Build Automation**:
   - Makefile target: `ingest-triad`
   - Updates schema file: `src/nmdc_submission_schema/schema/nmdc_submission_schema.yaml`
   - Validates with `linkml-lint`

### Stage 6: ROBOT Template Generation

1. **Template Creation**:
   - Script: `create_env_context_robot_template.py`
   - Input: `env_triad_pvs_sheet.owl`
   - Output: ROBOT template for ENVO

2. **Template Format**:
   - TSV with columns: `ID`, `label for convenience`, `subset`
   - Example row: `ENVO:00000428`, `biome`, `ENVO:03605013`
   - Subset IDs map to specific categories (e.g., `ENVO:03605013` = Terrestrial biomes)

## Repository 3: envo

### Stage 7: Ontology Integration

1. **Template Import**:
   - File: `/src/envo/robot_templates/nmdc_env_context_subset_membership.tsv`
   - Contains mappings between ENVO terms and NMDC subset IDs
   - Example subset IDs (copied from submission-schema):
     ```
     ENVO:03605013 - Terrestrial biomes
     ENVO:03605014 - Environmental features (terrestrial)
     ENVO:03605015 - Soil types
     ENVO:03605017 - Aquatic biomes
     ENVO:03605018 - Environmental features (aquatic)
     ENVO:03605019 - Water types
     ```

2. **Annotation Mechanism**:
   - Uses `oboInOwl:inSubset` to tag ENVO terms
   - Implemented via ROBOT template command:
   ```
   robot template --template nmdc_env_context_subset_membership.tsv -o nmdc_env_context_subset_membership.owl
   ```

3. **Makefile Integration**:
   - Primary target: `nmdc-robot-all`
   - Dependencies: `nmdc-robot-clean`, `robot_templates/nmdc_env_context_subset_membership.owl`
   - Integration into main ontology:
   ```make
   $(ONT)-base.owl: $(EDIT_PREPROCESSED) $(OTHER_SRC)
       $(ROBOT) merge --input $< $(patsubst %, --input %, $(OTHER_SRC)) \
       ...
   ```

### Stage 8: Ontology Subset Generation

1. **Define Subsets in Makefile**:
   ```make
   SUBSETS += nmdc_env_water nmdc_env_soil nmdc_env_biomes
   ```

2. **SPARQL Query Creation**:
   - File: `sparql/extract_subset.sparql`
   - Content:
   ```sparql
   SELECT ?term
   WHERE {
     ?term oboInOwl:inSubset obo:ENVO_03605019 .
   }
   ```

3. **Subset Build Process**:
   ```make
   subsets/nmdc_env_water.owl: envo.owl
       $(ROBOT) query --query sparql/extract_subset.sparql subsets/nmdc_water_terms.txt && \
       $(ROBOT) filter --input $< --term-file subsets/nmdc_water_terms.txt \
         --select "annotations self descendants" \
         --signature true \
         annotate --ontology-iri $(ONTBASE)/$@ \
         --output $@
   ```

## MIxS Integration Details

### MIxS Terminology and Evolution

1. **Field Terminology Evolution**:
   - Originally: "biome," "feature," "material"
   - MIxS v5: "env_broad_scale," "env_local_scale," "env_medium"

2. **MIxS Field Definitions**:
   - **env_broad_scale**: Report the major environmental system (coarse spatial grain)
   - **env_local_scale**: Report entities with significant causal influences in local vicinity
   - **env_medium**: Report materials immediately surrounding the sample

### MIxS Guidelines Implementation in NMDC

1. **Repository: external-metadata-awareness**
   - Voting sheet generation considers term appropriateness for each scale
   - ML model prediction helps associate terms with appropriate scales
   - Candidate terms are aligned with relevant MIxS fields

2. **Repository: submission-schema**
   - Schema annotations include MIxS field definitions
   - Example (from schema YAML):
   ```yaml
   env_broad_scale:
     description: >-
       Report the major environmental system the sample or specimen came from...
     annotations:
       expected_value:
         tag: expected_value
         value: >-
           The major environment type(s) where the sample was collected.
           Recommend subclasses of biome [ENVO:00000428].
   ```

3. **Repository: envo**
   - Subset categories align with MIxS field expectations
   - Terrestrial/aquatic biomes for env_broad_scale
   - Environmental features for env_local_scale
   - Material types for env_medium

### Specific MIxS-ENVO Guidelines

1. **Biome Selection (env_broad_scale)**:
   - Use ENVO's biome class (ENVO:00000428) for env_broad_scale
   - Examples: oceanic epipelagic zone biome, urban biome, tundra biome

2. **Scale Considerations (env_local_scale)**:
   - Add more fine-grained information than env_broad_scale
   - Example: env_broad_scale = "village biome [ENVO:01000246]", 
     env_local_scale = "farm [ENVO:00000078]" (not "village [ENVO:01000773]")

3. **Host-Associated Samples**:
   - For host-associated samples:
     - Include host taxonomy in MIxS host fields
     - env_broad_scale = ecosystem where host is found
     - env_local_scale = anatomical parts from UBERON or PO
     - env_medium = specific medium (e.g., mucus, tissue)

4. **Cross-Ontology Integration**:
   - Terms from other OBO ontologies can be used where appropriate
   - EnvO import mechanism ensures semantic compatibility
   - Pattern-based semantics recommended for complex cases

## Detailed Data Flow Between Repositories

```
external-metadata-awareness                  submission-schema                      envo
┌─────────────────────────┐                 ┌─────────────────────┐              ┌─────────────────────┐
│1. NCBI/GOLD/NMDC Data   │                 │                     │              │                     │
│   Extraction            │                 │                     │              │                     │
│2. MongoDB & DuckDB      │                 │                     │              │                     │
│   Processing            │                 │                     │              │                     │
│3. ML Classification     │                 │                     │              │                     │
│4. Voting Sheet Creation ├────────────────►│5. Vote Processing   │              │                     │
│                         │ TSV Voting      │6. Term Aggregation  │              │                     │
│                         │ Sheets          │7. LinkML Integration│              │                     │
│                         │                 │8. ROBOT Template    ├─────────────►│9. TSV Template      │
│                         │                 │   Generation        │ ROBOT        │   Import            │
│                         │                 │                     │ Template     │10.inSubset          │
│                         │                 │                     │              │   Annotations       │
│                         │                 │                     │              │11.Subset            │
│                         │                 │                     │              │   Generation        │
│                         │                 │                     │              │                     │
└─────────────────────────┘                 └─────────────────────┘              └─────────────────────┘
```

## File Paths and Technical Details

### external-metadata-awareness
- MongoDB DB: `ncbi_metadata`
- Primary collections: `biosamples`, `biosample_harmonized_attributes`
- DuckDB file: `local/ncbi_biosamples_YYYY-MM-DD.duckdb`
- Voting sheet config: `voting_sheets_configurations.yaml`
- Notebook: `notebooks/environmental_context_value_sets/generate_voting_sheet.ipynb`
- Output: `voting_sheets_output/[environment]_env_[scale]_voting_sheet.tsv`

### submission-schema
- Notebook dir: `notebooks/environmental_context_value_sets/`
- Processing notebooks: `post_google_sheets_[environment]_env_[scale].ipynb`
- Aggregation notebook: `generate_env_triad_pvs_sheet.ipynb`
- Output: `env_triad_pvs_sheet.tsv`, `env_triad_pvs_sheet.owl`
- Schema file: `src/nmdc_submission_schema/schema/nmdc_submission_schema.yaml`
- Template generator: `create_env_context_robot_template.py`

### envo
- Template location: `/src/envo/robot_templates/nmdc_env_context_subset_membership.tsv`
- Makefile targets: `nmdc-robot-all`, `nmdc-robot-clean`
- Output OWL: `robot_templates/nmdc_env_context_subset_membership.owl`
- Integration: `envo-base.owl`, `envo-full.owl`
- SPARQL directory: `sparql/`
- Subset output: `subsets/nmdc_env_*.owl`

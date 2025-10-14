# Environmental Triad Value Set Workflow

**Complete end-to-end workflow for NMDC environmental context value sets**

**Last Updated**: 2025-10-02

---

## Table of Contents
- [Quick Overview](#quick-overview)
- [What Are Environmental Triads?](#what-are-environmental-triads)
- [Repository Responsibilities](#repository-responsibilities)
- [Complete Workflow (8 Stages)](#complete-workflow-8-stages)
- [Quick Start Guide](#quick-start-guide)
- [For More Detail](#for-more-detail)

---

## Quick Overview

Environmental triads are three-scale environmental context descriptors required for all NMDC biosamples:
- **env_broad_scale**: Broad biome context (e.g., "temperate grassland biome [ENVO:01000193]")
- **env_local_scale**: Local environment (e.g., "agricultural field [ENVO:00000114]")
- **env_medium**: Sample material (e.g., "soil [ENVO:00001998]")

**The workflow** extracts environmental terms from millions of biosamples across three databases (NCBI, GOLD, NMDC), generates voting sheets for domain expert review, and integrates approved terms into NMDC's submission schema and the ENVO ontology.

**Currently implemented** for four environments: soil, water, sediment, and plant-associated.

**Three repositories involved**:
1. **external-metadata-awareness**: Data extraction → Voting sheets (this repo)
2. **submission-schema**: Vote processing → LinkML enumerations
3. **envo**: Ontology integration → inSubset annotations

---

## What Are Environmental Triads?

Environmental triads follow the **MIxS (Minimum Information about any Sequence) standard v5**, which defines three scales of environmental context:

### MIxS Field Definitions

**env_broad_scale** (MIxS:0000012):
- Report the major environmental system (coarse spatial grain)
- Recommendation: Use ENVO biome subclasses (ENVO:00000428)
- Examples: oceanic epipelagic zone biome, urban biome, tundra biome

**env_local_scale** (MIxS:0000013):
- Report entities with significant causal influences in local vicinity
- More fine-grained than env_broad_scale
- Example: env_broad_scale = "village biome", env_local_scale = "farm"

**env_medium** (MIxS:0000014):
- Report materials immediately surrounding the sample
- Recommendation: Use ENVO environmental material subclasses (ENVO:00010483)
- Examples: soil, mucus, seawater

### Host-Associated Samples

For samples from or on a host organism:
- **env_broad_scale**: Ecosystem where host is found
- **env_local_scale**: Anatomical parts (use UBERON for animals, PO for plants)
- **env_medium**: Specific material (e.g., mucus, tissue, blood)
- Plus: MIxS host fields for taxonomy

### Value Format Standard

All terms MUST follow the pattern: `term_name [term_id]`
- Example: `oceanic epipelagic zone biome [ENVO:01000033]`
- CURIEs use standard prefixes (ENVO, UBERON, PO, etc.)

---

## Repository Responsibilities

### 1. external-metadata-awareness (This Repo)

**Stages 1-3**: Data extraction through voting sheet generation

**Key Activities**:
- Load 44M+ NCBI biosamples from XML to MongoDB
- Extract environmental context values from NMDC, GOLD, and NCBI
- Normalize values and extract ontology CURIEs
- Predict environmental packages using ML (F1≈0.99)
- Generate voting sheets with candidate terms
- Share voting sheets with domain experts via Google Sheets

**Primary Output**: TSV voting sheets (`[environment]_env_[scale]_voting_sheet.tsv`)

### 2. submission-schema

**Stages 4-6**: Vote processing through ROBOT template generation

**Key Activities**:
- Process completed voting sheets (sum votes, apply threshold ≥1)
- Aggregate terms across all environments and scales
- Generate LinkML enumerations with naming pattern `Env[Scale][Environment]Enum`
- Create ROBOT templates for ENVO integration
- Validate schema with linkml-lint

**Primary Output**:
- Updated `nmdc_submission_schema.yaml` with LinkML enumerations
- ROBOT template TSV for ENVO

### 3. envo

**Stages 7-8**: Ontology integration and subset generation

**Key Activities**:
- Import ROBOT template with NMDC term-to-subset mappings
- Add `oboInOwl:inSubset` annotations to ENVO terms
- Generate NMDC-specific subsets (e.g., nmdc_env_water.owl)
- Integrate into main ENVO release

**Primary Output**: ENVO releases with NMDC subset annotations

---

## Complete Workflow (8 Stages)

### Stage 1: Data Collection (external-metadata-awareness)

**Scripts**:
- `xml_to_mongo.py`: Load NCBI biosample XML (~3GB, 44M samples)
- `extract_all_ncbi_packages_fields.py`: Extract package information
- `mongodb_biosamples_to_duckdb.py`: Convert to DuckDB tables

**MongoDB Collections** (database: `ncbi_metadata`):
- `biosamples`: Raw XML structure (~3M documents)
- `biosamples_flattened`: Normalized tabular structure
- `biosamples_attributes`: Individual attribute key-value pairs

**DuckDB Output**: `local/ncbi_biosamples_YYYY-MM-DD.duckdb`

**Tables**:
- `normalized_context_strings`: Environmental values normalized
- `curies_asserted`: CURIEs extracted via regex
- `curies_ner`: CURIEs identified via OAK text annotation

---

### Stage 2: Voting Sheet Generation (external-metadata-awareness)

**Location**: `notebooks/environmental_context_value_sets/`

**Configuration**:
- File: `voting_sheets_configurations.yaml`
- Defines: Environments, context slots, parent classes

**Main Notebook**: `generate_voting_sheet.ipynb`

**Process**:
1. Load biosamples from DuckDB
2. Predict environmental packages (ML model, F1≈0.99)
3. Extract CURIEs from environmental context values
4. Use OAK adapters for text annotation (EnvO: `sqlite:obo:envo`)
5. Generate candidate term lists with frequency counts
6. Output TSV files to `voting_sheets_output/`

**File Pattern**: `[environment]_env_[scale]_voting_sheet.tsv`
- Example: `soil_env_broad_scale_voting_sheet.tsv`

**Columns**:
- Term label
- CURIE
- Frequency count
- Boolean classification columns
- Vote columns (added by reviewers)

---

### Stage 3: Expert Voting (external-metadata-awareness)

**Sharing Process**:
1. TSV files uploaded to Google Sheets
2. Shared using service account credentials (`env-context-voting-sheets-*.json`)
3. Domain experts granted edit access

**Voting Instructions**:
1. Reviewers add columns:
   - `[INITIALS]_vote`: +1 (include), 0 (neutral), -1 (exclude)
   - `[INITIALS]_comment`: Justification or alternative suggestions
2. Focus on:
   - Term appropriateness for the scale
   - Alternative slot suggestions
   - Semantic clarity and precision

**Completion**:
- Sheets downloaded as TSV files
- File pattern: `post_google_sheets_[environment]_env_[scale].tsv`
- Submitted to project coordinators (Mark/Montana)

---

### Stage 4: Vote Processing (submission-schema)

**Location**: `notebooks/environmental_context_value_sets/`

**Processing Notebooks**:
- Pattern: `post_google_sheets_[environment]_env_[scale].ipynb`
- Example: `post_google_sheets_soil_env_broad_scale.ipynb`

**Vote Compilation**:
```python
# Sum all vote columns
vote_columns = [col for col in df.columns if col.endswith('_vote')]
df['vote_sum'] = df[vote_columns].sum(axis=1)

# Apply threshold (typically ≥1)
filtered_df = df[df['vote_sum'] >= 1]
```

**Output**: `post_google_sheets_[environment]_env_[scale].tsv`

---

### Stage 5: Schema Integration (submission-schema)

**Aggregation Notebook**: `generate_env_triad_pvs_sheet.ipynb`
- Consolidates all `post_google_sheets_*.tsv` files
- Outputs: `env_triad_pvs_sheet.tsv`, `env_triad_pvs_sheet.owl`

**Enumeration Generation**: `generate_env_triad_enums.py`

**Naming Pattern**: `Env[Scale][Environment]Enum`
- Examples:
  - `EnvBroadScaleSoilEnum`
  - `EnvLocalScaleWaterEnum`
  - `EnvMediumSedimentEnum`

**Permissible Value Format**:
```python
pv = PermissibleValue(text=f"{label} [{curie}]")
# Example: "oceanic epipelagic zone biome [ENVO:01000033]"
```

**Integration**:
- Target file: `src/nmdc_submission_schema/schema/nmdc_submission_schema.yaml`
- Makefile target: `ingest-triad`
- Validation: `linkml-lint`

**Example Schema Entry**:
```yaml
env_broad_scale:
  description: >-
    Report the major environmental system the sample or specimen came from...
  range: EnvBroadScaleSoilEnum  # For soil samples
  annotations:
    expected_value:
      tag: expected_value
      value: >-
        The major environment type(s) where the sample was collected.
        Recommend subclasses of biome [ENVO:00000428].
```

---

### Stage 6: ROBOT Template Generation (submission-schema)

**Script**: `create_env_context_robot_template.py`

**Input**: `env_triad_pvs_sheet.owl`

**Output**: ROBOT template TSV

**Format**:
| ID | label for convenience | subset |
|----|----------------------|--------|
| ENVO:00000428 | biome | ENVO:03605013 |
| ENVO:01000193 | temperate grassland biome | ENVO:03605013 |

**Subset IDs** (defined in submission-schema):
- `ENVO:03605013`: Terrestrial biomes
- `ENVO:03605014`: Environmental features (terrestrial)
- `ENVO:03605015`: Soil types
- `ENVO:03605017`: Aquatic biomes
- `ENVO:03605018`: Environmental features (aquatic)
- `ENVO:03605019`: Water types

**Handoff**: ROBOT template TSV sent to ENVO maintainers

---

### Stage 7: Ontology Integration (envo)

**Location**: `/src/envo/robot_templates/nmdc_env_context_subset_membership.tsv`

**ROBOT Processing**:
```bash
robot template \
  --template nmdc_env_context_subset_membership.tsv \
  -o nmdc_env_context_subset_membership.owl
```

**Annotation Mechanism**:
- Adds `oboInOwl:inSubset` annotations to ENVO terms
- Links terms to NMDC-specific subsets
- Example: ENVO:00001998 (soil) → inSubset ENVO:03605015 (Soil types)

**Makefile Integration**:
- Primary target: `nmdc-robot-all`
- Dependencies: `nmdc-robot-clean`, `robot_templates/nmdc_env_context_subset_membership.owl`

**Merge Process**:
```makefile
$(ONT)-base.owl: $(EDIT_PREPROCESSED) $(OTHER_SRC)
    $(ROBOT) merge --input $< $(patsubst %, --input %, $(OTHER_SRC)) \
    ...
```

---

### Stage 8: Subset Generation (envo)

**Makefile Definition**:
```makefile
SUBSETS += nmdc_env_water nmdc_env_soil nmdc_env_biomes
```

**SPARQL Query** (`sparql/extract_subset.sparql`):
```sparql
SELECT ?term
WHERE {
  ?term oboInOwl:inSubset obo:ENVO_03605019 .
}
```

**Build Process**:
```makefile
subsets/nmdc_env_water.owl: envo.owl
    $(ROBOT) query --query sparql/extract_subset.sparql \
      subsets/nmdc_water_terms.txt && \
    $(ROBOT) filter --input $< \
      --term-file subsets/nmdc_water_terms.txt \
      --select "annotations self descendants" \
      --signature true \
      annotate --ontology-iri $(ONTBASE)/$@ \
      --output $@
```

**Output**: NMDC-specific ENVO subsets (OWL format)
- `subsets/nmdc_env_water.owl`
- `subsets/nmdc_env_soil.owl`
- etc.

---

## Quick Start Guide

### Running the Voting Sheet Generation Pipeline

**Prerequisites**:
- MongoDB running with `ncbi_metadata` database populated
- DuckDB file: `local/ncbi_biosamples_YYYY-MM-DD.duckdb`
- Poetry environment installed

**Steps**:
1. Start Jupyter: `poetry run jupyter notebook`
2. Navigate to: `notebooks/environmental_context_value_sets/`
3. Open: `generate_voting_sheet.ipynb`
4. Run all cells
5. Output appears in: `voting_sheets_output/`

**Configuration**:
Edit `voting_sheets_configurations.yaml` to:
- Add new environments
- Modify parent class CURIEs
- Adjust frequency thresholds

### Extending to New Environments

**Planning**:
1. Research term availability in ENVO (or other ontologies)
2. Identify parent classes for each scale
3. Engage domain experts early
4. Define naming conventions

**Configuration Update**:
Add to `voting_sheets_configurations.yaml`:
```yaml
environments:
  new_environment:
    env_broad_scale:
      parent_classes:
        - ENVO:00000xxx  # Appropriate parent
    env_local_scale:
      parent_classes:
        - ENVO:00000yyy
    env_medium:
      parent_classes:
        - ENVO:00000zzz
```

**Naming Conventions**:
- Voting sheets: `[environment]_env_[scale]_voting_sheet`
- Post-voting files: `post_google_sheets_[environment]_env_[scale].tsv`
- Enumerations (submission-schema): `Env[Scale][Environment]Enum`

---

## For More Detail

### Implementation Details
- **Voting sheet technical notes**: `notebooks/environmental_context_value_sets/voting-sheet-generation-readme.md`
- **Historical workflow analysis**: `docs/nmdc-env-triad-valueset-lifecycle.md` (299 lines)
- **Submission schema README**: `repo_data/microbiomedata/submission-schema_README.md`

### Repository Links
- **external-metadata-awareness**: https://github.com/microbiomedata/external-metadata-awareness
- **submission-schema**: https://github.com/microbiomedata/submission-schema
- **envo**: https://github.com/EnvironmentOntology/envo

### Related Documentation
- **MIxS Standard**: https://genomicsstandardsconsortium.github.io/mixs/
- **LinkML**: https://linkml.io/linkml-model/latest/docs/EnumDefinition/
- **ENVO Ontology**: http://obofoundry.org/ontology/envo.html
- **ROBOT Tool**: http://robot.obolibrary.org/

### Key Data Files
- **DuckDB exports**: https://portal.nersc.gov/project/m3408/biosamples_duckdb/
- **NMDC Schema**: https://github.com/microbiomedata/submission-schema/tree/main/src/nmdc_submission_schema/schema

---

## Sustainability Considerations

### Version Tracking
- Document which versions of source ontologies were used
- Record dates of biosample data snapshots
- Track DuckDB file versions (YYYY-MM-DD stamps)

### Term Deprecation
- Monitor ENVO releases for deprecated terms
- Update submission-schema enumerations when terms become obsolete
- Maintain backward compatibility for existing submissions

### Pipeline Testing
- Test full pipeline end-to-end before major updates
- Verify CURIE extraction accuracy periodically
- Validate LinkML schema after enumeration updates

### Reproducibility
- Document vote thresholds used for each voting round
- Archive voting sheets and results
- Maintain audit trail of term additions/removals

---

## Common Issues and Solutions

### Issue: Low CURIE Coverage
**Symptom**: Many environmental context values lack ontology CURIEs

**Solutions**:
- Run OAK text annotation with broader parent classes
- Use BioPortal mapper for additional ontology coverage
- Engage ENVO maintainers to add missing terms

### Issue: Inconsistent Package Predictions
**Symptom**: ML model assigns unexpected env_package values

**Solutions**:
- Review prediction confidence scores (model F1≈0.99)
- Manually verify edge cases
- Retrain model with updated training data

### Issue: Vote Compilation Conflicts
**Symptom**: Reviewers disagree significantly (vote_sum near 0)

**Solutions**:
- Convene reviewer discussion
- Consider term refinement or splitting
- Document rationale for inclusion/exclusion decision

---

## Contact and Support

**Questions about**:
- **Data extraction & voting sheets**: Submit issue to external-metadata-awareness repo
- **Schema integration**: Submit issue to submission-schema repo
- **ENVO integration**: Contact ENVO maintainers or submit issue to envo repo

**Maintainers**:
- Mark A. Miller (external-metadata-awareness)
- Montana Smith (submission-schema)
- Chris Mungall (envo, ENVO ontology)

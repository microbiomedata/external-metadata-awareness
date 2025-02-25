# Environmental Context Value Set Generator - Draft Documentation

## Core Purpose and Implementation
This notebook generates voting sheets for reviewing proposed environmental context value sets across two dimensions:
- Sample type/environment (from MIxS extensions: https://genomicsstandardsconsortium.github.io/mixs/#extensions)
- Environmental context questions from MIxS:
  - env_broad_scale (https://genomicsstandardsconsortium.github.io/mixs/0000012/)
  - env_local_scale (https://genomicsstandardsconsortium.github.io/mixs/0000013/)
  - env_medium (https://genomicsstandardsconsortium.github.io/mixs/0000014/)

The ultimate goal is to develop sets of OBO foundry ontology classes suitable for LinkML enumerations (https://linkml.io/linkml-model/latest/docs/EnumDefinition/).

## Data Sources and Processing Details

### NMDC Biosamples
- Structured annotations with sub-slots:
  - Raw user-provided value
  - CURIE
  - Label (retrieved if missing)
- Environment type challenges:
  - Stored in env_package slots
  - Often empty or inconsistently populated
  - Requires normalization and inference
- Circular Dependency Note:
  - Current workflow predicts env_package from environmental context values
  - Then queries for environmental context values based on predicted env_package
  - High confidence in predictions (F1 ≈ 0.99)
  - Team review needed for predictions
  - Injection into MongoDB required ASAP

### GOLD Biosamples
- Source: Microsoft Excel file
- Uses GOLD path values instead of MIxS questions
- Inference through GOLD ontology (https://github.com/cmungall/gold-ontology)
- API limitations:
  - API available (https://gold-ws.jgi.doe.gov/)
  - No "all biosamples" mode
  - Requires specific ID for retrieval
- Current state: Using Chris' mappings rather than full biosample download

### NCBI Biosamples
- Complex processing due to low curation
- Two-phase CURIE identification:
  1. CURIE extraction via regex
     - Multiple settings available
     - False positive/negative rates not yet assessed
  2. String matching via OAK annotations
     - Currently EnvO-only
     - Multi-backend selection mechanism needed

#### Auto-increment Issue Details
- Example Case: Coastal Sea Water
  - stretch_summary_df shows:
    - Stretch id 1: 661 rows (2151 to 2811) sharing text annotation ENVO:00002150
    - Stretch id 2: 7 terms (1000302 to 1000308) for ENVO:01000301
  - Verification:
    - SAMN19460489 and SAMN37714815 show "coastal sea water [ENVO:00002152]"
    - Discovered during env_medium water sample analysis

## Value Set Seeding Details

### Current Parent Classes
- env_broad_scale: ENVO:00000428 ('biome')
- env_local_scale: ENVO:01000813 ('astronomical body part')
- env_medium: ENVO:00010483 ('environmental material')

### Coverage Gaps and Limitations
- Plant-associated samples excluded (no single parent class)
- Sediment samples excluded (no single parent class)
- No NMDC sediment samples currently exist
- Hydrocarbon and miscellaneous/artificial environment samples present but lacking value sets
- EnvO-exclusive for labels and annotations
- Parent classes not indicated in output sheets
- Multiple-superclass seeding needed
  - env_local_scale candidates:
    - astronomical body part
    - environmental system
    - Review other material entity subclasses
    - Check soil env_local_scale enumeration

## Development Notes and TODOs
- Better documentation needed for debugging variables/dataframes
  - Example: "daily farm" investigation support
- DuckDB development in progress:
  - PR: https://github.com/microbiomedata/external-metadata-awareness/pull/32
  - Lacks auto-increment handling
  - Not yet integrated

## Voting Process Implementation
Reviewers should:
1. Add personal columns:
   - `[INITIALS]_vote` (-1 or +1)
   - `[INITIALS]_comment`
2. Comment focus:
   - Alternative slot suggestions
   - Vote justification
3. Submit TSV to Mark/Montana for:
   - Vote compilation
   - Inter-annotator scoring

## Technical Implementation Notes
- Looking up labels only for EnvO CURIEs currently
- Need resolution for cases with both CURIE and annotatable text
- Need mechanism for selecting best annotations across multiple backends
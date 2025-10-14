# NMDC Biosample Measurement Discovery Strategy

## Overview

This document outlines the comprehensive strategy for discovering, processing, and correcting measurement fields in NCBI biosamples for environmental metadata analysis. The approach emphasizes data-driven discovery over manual curation and implements systematic unit correction to address quantulum3 parsing limitations.

## Problem Statement

### Quantulum3 Unit Parsing Issues
Quantulum3, while powerful for general text measurement parsing, produces incorrect unit interpretations for scientific measurements:
- **PSU** (Practical Salinity Units) → "pico-seconds-atomic-mass-units"
- **pH** values → incorrect compound units
- **Host age abbreviations**: `'6m' → 6.0 metre` (should be "6 months"), `'21d' → 21.0 dime` (should be "21 days")
- **Time period units**: `'5-16 wks' → 5.0-16.0 watt kibibyte second` (should be "weeks")
- Environmental measurement units often misinterpreted

### Manual Curation Limitations
Previous approach used hardcoded field lists (`curated_measurements` in `normalize_biosample_measurements.py`):
- 258-field list with duplicates
- No systematic discovery of new measurement fields
- Manual maintenance burden
- Misses emerging measurement types

## Automated Discovery Pipeline

### Architecture Overview
Four-phase pipeline implemented in `Makefiles/measurement_discovery.Makefile`:

1. **Discovery Phase**: Find fields with units and numeric content
2. **Prioritization Phase**: Combine discoveries into priority targets
3. **Processing Phase**: Apply unit correction and normalization
4. **Export Phase**: Generate flat measurement tuples

### Phase 1: Field Discovery

#### Discovery Target 1: Fields with Unit Assertions
**File**: `mongo-js/discover_measurement_fields_with_units.js`
**Collection**: `measurement_fields_with_units`
**Checkpoint**: `local/measurement_fields_with_units.json`

```javascript
// Query pattern
{
    $match: {
        unit: { $exists: true, $ne: null, $ne: "" }
    }
}
```

**Index**: `{unit: 1, harmonized_name: 1}`
**Output**: Fields with authoritative unit assertions from original submissions

#### Discovery Target 2: Fields with Embedded Units (Mixed Content)
**File**: `mongo-js/discover_numeric_content_fields.js`
**Collection**: `numeric_content_fields`
**Checkpoint**: `local/numeric_content_fields.json`

```javascript
// Query pattern
{
    $match: {
        content: { 
            $regex: ".*[0-9].*[a-zA-Z].*|.*[a-zA-Z].*[0-9].*"  // matches: 25.3 meters, 6m, 21d, pH 7.5
        }
    }
}
```

**Index**: `{content: 1, harmonized_name: 1}`
**Output**: Fields with mixed numeric and alphabetical content containing embedded units

### Phase 2: Target Prioritization
**Script**: `prioritize-measurement-targets` (to be implemented)
**Input**: Both discovery checkpoint files
**Output**: `local/priority_measurement_fields.json`
**Criteria**: 
- Minimum occurrence count (e.g., 100+ samples)
- Unit availability scoring
- Field name relevance weighting

### Phase 3: Measurement Processing
**Script**: `normalize-biosample-measurements`
**Enhancement**: Use authoritative units when available
**Processing Strategy**:
1. Prefer authoritative units from `biosamples_attributes.unit`
2. Apply quantulum3 parsing for unit-less numeric fields
3. Implement LLM-based unit correction for quantulum3 failures

### Phase 4: Flat Export
**Target**: `export-flat-measurements`
**Output**: `local/flat_measurements.tsv`
**Schema**: `biosample_id | harmonized_name | value | unit`
**Purpose**: Enable similarity analysis and embedding generation

## Data Sources and Collections

### Input Collections
- **biosamples_attributes**: Flattened attributes from environmental biosamples
  - Fields: `harmonized_name`, `content`, `unit`, `accession`
  - Size: ~4.56M environmental samples (2017+)
  - Filtering: Complete environmental triads required

### Output Collections
- **measurement_fields_with_units**: Discovery results for fields with units
- **numeric_content_fields**: Discovery results for numeric fields
- **biosamples_measurements**: Processed measurements with corrected units
- **flat_measurements**: Final export collection

### Checkpoint Files
All discovery results saved as JSON files in `local/` directory:
- `measurement_fields_with_units.json`
- `numeric_content_fields.json`
- `priority_measurement_fields.json`
- `flat_measurements.tsv`

## LLM-Based Unit Correction Strategy

### Problem Context
Quantulum3 produces scientifically implausible unit interpretations that need correction before downstream analysis.

### Proposed Solutions

#### Option 1: PydanticAI Agent (Recommended)
```python
class UnitCorrection(BaseModel):
    original_unit: str
    corrected_unit: str
    confidence: float
    reasoning: str

class MeasurementContext(BaseModel):
    field_name: str
    sample_values: List[str]
    quantulum_unit: str
    authoritative_unit: Optional[str] = None

unit_agent = Agent(
    'claude-3-5-sonnet-20241022',
    result_type=UnitCorrection,
    system_prompt="""You are a scientific unit expert..."""
)
```

**Advantages**:
- Structured output with confidence scores
- Batch processing efficiency
- Reasoning capture for debugging
- Easy MongoDB pipeline integration

#### Option 2: Claude Code CLI Integration
Headless mode processing for batch unit corrections:
```python
def correct_units_via_claude_cli(measurements_batch):
    prompt = f"Correct these quantulum3 unit interpretations: {measurements_batch}"
    result = subprocess.run(['claude-code', '--headless', '--prompt', prompt], 
                          capture_output=True, text=True)
    return parse_unit_corrections(result.stdout)
```

#### Option 3: Hybrid Approach
1. **Rules-based corrections** for obvious cases (PSU → practical salinity units)
2. **LLM agent** for ambiguous quantulum3 failures
3. **Authoritative unit preference** when available from original submissions

### Implementation Priority
1. Enhance `normalize_biosample_measurements.py` with authoritative unit preference
2. Add PydanticAI unit correction agent
3. Integrate as optional phase in measurement discovery pipeline
4. Implement confidence-based fallback strategies

## Key Learnings

### Harmonized vs Attribute Names
- **Use `harmonized_name`** for consistency across biosamples
- Harmonized names provide standardized field identification
- Original attribute names vary significantly across submissions

### Environmental Sample Focus
- Pipeline targets environmental samples with complete triads
- Clinical/human samples excluded from measurement analysis
- 2017+ samples ensure metadata quality and completeness

### Index Strategy
- Create beneficial indexes before aggregation queries
- Composite indexes: `{unit: 1, harmonized_name: 1}`, `{content: 1, harmonized_name: 1}`
- Index creation integrated into Makefile targets

### Checkpoint Approach
- File-based checkpoints preferred over hardcoded Python lists
- JSON exports enable manual inspection and debugging
- Makefile dependencies ensure proper execution order

## Usage Instructions

### Running the Complete Pipeline
```bash
make measurement-pipeline -f Makefiles/measurement_discovery.Makefile MONGO_URI="mongodb://localhost:27017/ncbi_metadata"
```

### Running Individual Phases
```bash
# Phase 1: Discovery
make discover-measurement-fields -f Makefiles/measurement_discovery.Makefile MONGO_URI="mongodb://localhost:27017/ncbi_metadata"
make discover-numeric-fields -f Makefiles/measurement_discovery.Makefile MONGO_URI="mongodb://localhost:27017/ncbi_metadata"

# Phase 2: Prioritization  
make prioritize-targets -f Makefiles/measurement_discovery.Makefile MONGO_URI="mongodb://localhost:27017/ncbi_metadata"

# Phase 3: Processing
make process-priority-measurements -f Makefiles/measurement_discovery.Makefile MONGO_URI="mongodb://localhost:27017/ncbi_metadata"

# Phase 4: Export
make export-flat-measurements -f Makefiles/measurement_discovery.Makefile MONGO_URI="mongodb://localhost:27017/ncbi_metadata"
```

### Cleanup
```bash
make clean-discovery -f Makefiles/measurement_discovery.Makefile MONGO_URI="mongodb://localhost:27017/ncbi_metadata"
```

## Future Enhancements

### Immediate Next Steps
1. Implement `prioritize-measurement-targets` script
2. Add LLM unit correction to `normalize_biosample_measurements.py`
3. Create `export_flat_measurements.js` for final export phase
4. Test complete pipeline end-to-end

### Long-term Improvements
1. **Semantic similarity analysis** using flat measurement tuples
2. **Google Earth Alpha embeddings** integration for geospatial analysis
3. **Automated unit standardization** across measurement types
4. **Confidence scoring** for measurement quality assessment
5. **Integration with submission-schema** for metadata validation

## Technical Notes

### MongoDB Collections Schema
```javascript
// measurement_fields_with_units
{
    harmonized_name: "salinity",
    unit: "PSU", 
    count: 1250,
    sample_values: ["35.2", "34.8", "36.1"],
    sample_accessions: ["SAMN123", "SAMN456"],
    has_authoritative_unit: true
}

// numeric_content_fields  
{
    harmonized_name: "host_age",
    count: 2840,
    has_units: 1200,
    unit_coverage_percent: 42.25,
    sample_values: ["6m", "21d", "5-16 wks", "25.3 meters"],
    units_found: ["m", "d", "wks", "meters"],
    has_embedded_units: true
}
```

### Performance Considerations
- Index creation before aggregation queries (30+ seconds for large collections)
- Batch processing for memory efficiency
- Progress reporting for long-running operations
- File checkpoints prevent re-processing completed phases

### Integration Points
- **DuckDB export**: Flat measurements compatible with analytical workflows
- **Similarity analysis**: Enables biosample clustering and recommendation
- **Submission validation**: Quality scoring for new submissions
- **Ontology mapping**: Unit standardization against QUDT/UO ontologies
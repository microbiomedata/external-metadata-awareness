# NCBI Biosamples Analysis Session Summary

## Schema Structure and Complexity

### Core Document Structure
NCBI biosamples in MongoDB follow a deeply nested XML-derived structure with the critical `Attributes.Attribute` array containing metadata. Each attribute has:
- `harmonized_name`: Standardized field name (preferred for queries)
- `attribute_name`: Original field name from submission
- `content`: Raw, unharmonized values (still original submission text)
- Optional: `display_name`, `unit`

**Critical distinction**: Field names are harmonized, but values in `content` remain unharmonized original submissions.

### Environmental Triad Fields
The three environmental context fields are:
- `env_broad_scale`: Broad environmental context (e.g., terrestrial biome)
- `env_local_scale`: Local environmental context (e.g., forest soil)
- `env_medium`: Environmental medium (e.g., soil)

### Required Indexes
For nested array queries:
```javascript
db.biosamples.createIndex({"Attributes.Attribute.harmonized_name": 1, "Attributes.Attribute.content": 1})
db.biosamples.createIndex({"publication_date": 1})
```

**Index limitations**: Regex queries cannot utilize indexes effectively for substring matching.

### Schema Validation Learning
The provided JSON schema revealed:
- Complex nested structures with mixed array/object patterns
- Optional vs required field patterns
- ObjectId reference patterns for MongoDB documents
- Distinction between harmonized field names and raw content values

## Date Handling

### Publication Date Format
All dates stored as ISO timestamp strings: `"2017-01-01T00:00:00.000"`
- No abbreviated date formats found (e.g., no `"2017-01-01"`)
- String comparison safe for cutoff: `publication_date: {$gte: "2017-01-01T00:00:00.000"}`

## Data Distribution Analysis

### Scale and Scope
- **Total NCBI biosamples**: ~44.3 million documents
- **Publication date ≥2017**: ~30+ million documents (satellite embedding alignment)
- **Complete environmental triads**: ~5 million documents (12% hit rate from sampling)
- **ENVO CURIE triads**: ~428,000 documents (strict ontological references)

### Environmental vs Clinical Distinction
Environmental samples characterized by complete environmental triad metadata, distinguishing them from clinical/host-associated samples that typically lack these annotations.

### Temporal Alignment
The 2017+ filter aligns with Google Earth Alpha satellite embedding availability (2017-2024).

### Sampling Methodology
Used 1000-document samples to estimate distribution patterns:
- Reliable hit rate calculations (12% for complete triads)
- Cost-effective alternative to expensive full collection scans
- Validated approach for query development

## User Objectives and Strategy

### Primary Goal
Create enriched environmental biosamples subset for enhanced metadata analysis, moving away from CSV exports to focus exclusively on DuckDB as the analytical target format.

### Value-Add Pipeline
1. **Subset Creation**: Filter to environmental samples (2017+, complete triads)
2. **Flattening**: Convert nested XML structure to tabular format
3. **Enhancement**: Add ENVO ontology CURIEs and satellite embeddings
4. **Export**: Generate DuckDB database for analysis

### Integration Requirements
Maintain compatibility with existing workflow expectations:
- Database: `ncbi_metadata`
- Collection: `biosamples` (nested XML structure, then flattened later in pipeline)
- Preserve existing Makefile and script patterns

## Google Earth Alpha Satellite Embeddings

### Technical Specifications
- **Dimensions**: 64-dimensional vectors
- **Resolution**: 10m x 10m pixels
- **Temporal Coverage**: 2017-2024
- **Purpose**: Geospatial context enhancement for environmental samples
- **Integration Point**: Aligns with 2017+ publication date filter

Future enhancement opportunity using satellite embeddings for geospatial context enrichment of environmental samples.

## Technical Discoveries

### Query Performance Patterns
- **$all with $elemMatch**: Efficient pattern for requiring multiple attributes
- **Regex vs Exact Matching**: Non-anchored regex queries cannot use indexes effectively
- **String Comparison Behavior**: `"2017-01-01" < "2017-01-01T00:00:00.000"` in MongoDB
- **Sampling strategy**: 1000-document samples provide reliable distribution estimates
- **Materialization approach**: Creating subset collections improves subsequent query performance

### Database Operations

#### Collection Creation Commands
**Create subset in same database**:
```javascript
{$out: "environmental_candidates_2017_plus"}
```

**Move to different database**:
```javascript
db.environmental_candidates_2017_plus.aggregate([{$out: {db: "ncbi_metadata", coll: "biosamples"}}])
```

#### Final Materialization Query
```javascript
db.biosamples.aggregate([
  {$match: {
    publication_date: {$gte: "2017-01-01T00:00:00.000"},
    "Attributes.Attribute": {
      $all: [
        {$elemMatch: {harmonized_name: "env_broad_scale", content: {$exists: true, $ne: null, $ne: ""}}},
        {$elemMatch: {harmonized_name: "env_local_scale", content: {$exists: true, $ne: null, $ne: ""}}},
        {$elemMatch: {harmonized_name: "env_medium", content: {$exists: true, $ne: null, $ne: ""}}}
      ]
    }
  }},
  {$out: "environmental_candidates_2017_plus"}
]);
```

## Database Architecture Analysis

### Instance Comparisons
**Local vs Loadbalancer Differences**:
- Local: `ncbi_metadata_20250919` (dated database) 
- Loadbalancer: `ncbi_metadata` (standard naming)
- **Structural Differences**:
  - `compact_mined_triads`: Present in loadbalancer (43.1M documents) but missing from local instance
  - **SRA Data Organization**: Loadbalancer has SRA metadata in `ncbi_metadata.sra_metadata`, while local instance uses separate `biosamples` database
  - **Analysis Collections**: Local instance has additional collections (`biosample_harmonized_attributes`, `class_label_cache`, `unique_triad_values`, `triad_components_labels`) not present in loadbalancer
  - **Database Size**: Loadbalancer `ncbi_metadata` nearly twice as large (49.7GB vs 24.9GB)

### Development vs Production Patterns
- Loadbalancer appears more consolidated with fewer normalized tables
- Local instance contains more intermediate and analytical collections
- Both share similar core data volumes despite structural differences

### MongoDB Connection Standardization
Multiple connection patterns across codebase:
- **Component-based**: Scripts like `xml_to_mongo.py` use separate host/port parameters
- **URI-style**: `--mongo_uri mongodb://host:port/` format
- **Utility function**: `notebooks/core.py` contains `get_mongo_client()` with authentication
- **Inconsistent naming**: `mongo_uri` vs `mongo-uri` parameter variations

### Database Name Parameterization Challenge
Scripts expect standard `ncbi_metadata` database name, but user has dated version requiring:
- Database name parameterization across tools
- Or data movement to standard location

## SRA Integration Context

### Relationship Data
- **SRA-Biosample-Bioproject pairs**: ~29 million relationships
- **BigQuery source**: `nih-sra-datastore.sra.metadata`
- **Collection**: `sra_biosamples_bioprojects` for linking data
- **Processing approaches**: Direct BigQuery to MongoDB, two-step via Parquet

### Integration Potential
SRA metadata provides additional context for environmental sample enhancement and validation.

## Existing Codebase Infrastructure

### Key Scripts and Workflows
- **`mongo-js/flatten_biosamples.js`**: Collection flattening patterns
- **`external_metadata_awareness/normalize_biosample_measurements.py`**: Quantulum3 measurement parsing with curated measurements list
- **`mongodb_biosamples_to_duckdb.py`**: DuckDB export functionality
- **`Makefiles/env_triads.Makefile`**: Environmental enhancement pipeline

### Value-Add Processing Infrastructure
Extensive existing tooling for:
- XML to MongoDB conversion with oversized document handling
- Environmental triad extraction and normalization
- ENVO ontology integration via OAK adapters
- Measurement standardization using quantulum3
- DuckDB analytical export with tabular representations

### Workflow Integration Points
- **Existing Infrastructure Leverage**: Designed to work with established `biosamples_flattened` collection patterns
- **Makefile Integration**: Targets in `ncbi_metadata.Makefile` for complete processing pipeline
- **Library Dependencies**: quantulum3 for measurement parsing, OAK for ontology operations
- **Data Flow**: XML → MongoDB → flattened → enhanced → DuckDB

## Filtering Strategy Evolution

### Initial Approach
Attempted broad environmental sample identification through various metadata patterns.

### Refined Strategy
Complete environmental triads as reliable indicator of environmental (vs clinical) samples, requiring all three fields with non-empty content:
```javascript
"Attributes.Attribute": {
  $all: [
    {$elemMatch: {harmonized_name: "env_broad_scale", content: {$exists: true, $ne: null, $ne: ""}}},
    {$elemMatch: {harmonized_name: "env_local_scale", content: {$exists: true, $ne: null, $ne: ""}}},
    {$elemMatch: {harmonized_name: "env_medium", content: {$exists: true, $ne: null, $ne: ""}}}
  ]
}
```

### ENVO Integration Levels
- **Relaxed**: Any complete environmental triad (~5M samples)
- **Strict**: ENVO CURIEs in environmental fields (~428K samples)
- **Substring matching**: Case-insensitive "envo" detection for ontological references

## Performance and Scale Considerations

### Memory Management
- **WiredTiger cache**: 80% utilization during materialization observed
- **Insert rates**: 5-10K documents/second during aggregation output
- **Timeout patterns**: Complex nested queries require extended timeouts (10+ minutes)
- **Resident memory**: Growing from 10.5G to 10.9G during processing

### Indexing Strategy
Focus on `harmonized_name` over `attribute_name` for standardization, though regex performance limitations remain for flexible text matching.

### Monitoring Tools
- **mongostat**: Real-time server statistics showing insert/query rates, cache usage
- **mongotop**: Collection-level read/write time analysis
- **Progress indicators**: Steady insert rates indicate healthy materialization progress

## Architecture Improvements Identified

### Consistency Needs
1. **Database name parameterization** across scripts
2. **Standardized MongoDB connection patterns** (currently inconsistent)
3. **Performance optimization** for large-scale environmental context queries
4. **Unified environment variable approach** for sensitive data

### Pipeline Testing Requirements
- Test full pipeline from term selection through schema integration
- Reproducibility documentation with version tracking
- Term deprecation processes for ontology updates

## Next Phase Requirements

### Immediate Tasks
1. Complete materialization to `environmental_candidates_2017_plus`
2. Move subset to `ncbi_metadata.biosamples`
3. Execute flattening and enhancement pipeline using existing infrastructure
4. Generate DuckDB export with environmental and geospatial context

### Critical Understanding
The value-add pipeline is essential because while field names are harmonized, the actual values in `content` remain as raw, unharmonized submission text requiring normalization and ENVO enhancement for meaningful analysis. This distinguishes between harmonized field structure and the need for value harmonization.
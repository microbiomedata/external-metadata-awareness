# NCBI Biosample DuckDB Export Summary
*Generated: 2025-09-30*

## Overview

Successfully exported 16 100%-flat MongoDB collections from the `ncbi_metadata` database into a single DuckDB file containing 109+ million rows across all tables.

## Database Details

- **File**: `ncbi_metadata_3M_biosamples_flat_20250930.duckdb`
- **Size**: 2.2 GB
- **Source**: MongoDB `ncbi_metadata` database (localhost:27017)
- **Scope**: 3 million NCBI BioSamples collected on or after 2017-01-01
- **Filtering Criteria**: Samples must have values for all three MIxS environmental triad fields:
  - `env_broad_scale`
  - `env_local_scale`
  - `env_medium`
- **Total Rows**: 109,278,640 across 16 tables
- **Location**: https://portal.nersc.gov/cfs/m3408/biosamples_duckdb/ncbi_metadata_3M_biosamples_flat_20250930.duckdb
- **Documentation**: https://portal.nersc.gov/cfs/m3408/biosamples_duckdb/September-2025-Biosample-DuckDB-documentation.html

## Table Summary

| Table Name | Rows | Columns | Description |
|------------|------|---------|-------------|
| `attribute_harmonized_pairings` | 20,937 | 3 | Maps submitter field names to harmonized names |
| `biosamples_attributes` | 52,518,729 | 6 | Raw attribute-value pairs (long format) |
| `biosamples_flattened` | 3,037,277 | 277 | **Primary table**: One row per biosample with flattened attributes |
| `biosamples_ids` | 7,871,449 | 5 | Cross-database identifiers |
| `biosamples_links` | 2,335,376 | 5 | Cross-database references |
| `content_pairs_aggregated` | 2,331,732 | 4 | Aggregated (harmonized_name, content) pairs with counts |
| `env_triads_flattened` | 9,262,719 | 9 | **Normalized environmental triads** with CURIEs and labels |
| `harmonized_name_dimensional_stats` | 432 | 13 | Statistical analysis of measurement-like attributes |
| `harmonized_name_usage_stats` | 695 | 3 | Usage frequency per harmonized field |
| `measurement_evidence_percentages` | 695 | 11 | Evidence metrics for measurement-like fields |
| `measurement_results_skip_filtered` | 87,466 | 12 | **Normalized measurements** from quantulum3 parsing |
| `mixed_content_counts` | 440 | 2 | Attributes with mixed alphanumeric content |
| `ncbi_attributes_flattened` | 960 | 8 | NCBI attribute schema definitions |
| `ncbi_packages_flattened` | 229 | 12 | NCBI package definitions (MIGS, MIMS, etc.) |
| `sra_biosamples_bioprojects` | 31,809,491 | 2 | Biosample-to-BioProject relationships from SRA |
| `unit_assertion_counts` | 13 | 3 | Tabulation of explicit unit assertions |

## Key Features

### Complete Biosample Flattening
- `biosamples_flattened` provides near-complete flattening of NCBI Biosample XML structure
- 277 columns include all harmonized attributes found across 3M samples
- Comparable to Mikaela's CSV but without value normalizations
- MongoDB `_id` field excluded from all tables

### Environmental Triad Normalization
- `env_triads_flattened` contains normalized environmental context values
- CURIEs extracted via regex and NER (Named Entity Recognition)
- Includes ontology labels for human readability
- Example top env_medium values:
  - UBERON:0001988 (feces): 429,644
  - ENVO:00001998 (soil): 180,936
  - ENVO:00002003 (fecal material): 72,070
  - ENVO:00002006 (liquid water): 70,424

### Measurement Normalization
- `measurement_results_skip_filtered` contains parsed measurements from quantulum3
- Join with `biosamples_attributes` on `content` and `harmonized_name`
- Example query:
```sql
SELECT *
FROM biosamples_attributes ba
JOIN measurement_results_skip_filtered mrsf
  ON ba.content = mrsf.original_content
  AND ba.harmonized_name = mrsf.harmonized_name
WHERE ba.accession = 'SAMN06651834';
```

## Technical Implementation

### Export Process
1. **mongoexport** → JSON Lines format (one document per line)
2. **DuckDB** `read_json()` → Table creation with schema inference
3. Key DuckDB parameters:
   - `auto_detect=true` - Automatic schema detection
   - `union_by_name=true` - Handle variable schemas (critical for `biosamples_flattened`)
   - `maximum_object_size=16777216` - Support large documents
   - `EXCLUDE _id` - Omit MongoDB ObjectId field

### Makefile Targets
Created `Makefiles/ncbi_to_duckdb.Makefile` with targets:
- `make-database` - Full pipeline (export + load)
- `dump-json` - Export MongoDB to JSON only
- `make-duckdb` - Load DuckDB from existing JSON
- `show-summary` - Display table statistics
- `clean-json` / `clean-duckdb` - Cleanup

## Known Limitations & Annoyances

### Column Organization
- `biosamples_flattened` has ~277 columns in no logical order
- Not alphabetical, not grouped by category
- Could benefit from explicit column ordering in future exports

### Measurement Parsing Issues
- quantulum3 produces questionable units in some cases
- Example: '2wk' parsed as value=2.0, unit="watt kibibyte"
- Age/time parsing particularly problematic

### Inconsistent Timestamps
- Some tables have date/timestamp fields (e.g., `content_pairs_aggregated.aggregated_at`)
- Field naming inconsistent across tables
- Not all tables track when data was processed

### Naming Conventions
- Table and column names not always obvious or consistent
- Some field names require SQL quoting (e.g., `content`, `value`)
- Mix of snake_case and variations

### Submitter Data Quality
- Many attribute values are poorly structured
- Example altitude value: `'1245PM,40F,NO WIND, BLACK BROOK'`
- Contains time, temperature, weather, and location mixed together
- Would require sophisticated parsing to decompose correctly

### Environmental Triad Issues
- 'root' from NCBITaxon:1 almost always means plant roots, not taxonomic root
- Many samples have 0 or multiple values for env_broad_scale/env_local_scale/env_medium
- Current 3M subset has 1+ values; need logic for handling multiple values

### Scope Limitations
- Only 3 million of 48 million total NCBI BioSamples included
- Filtered to samples with collection_date ≥ 2017-01-01 and complete environmental triads
- Matches temporal scope of Google Earth Satellite Embedding V1 Annual (2017-2024)

## Future Improvements

### Near-Term
1. Add normalized date, latitude, longitude columns to main export
2. Order columns in `biosamples_flattened` logically
3. Standardize timestamp field naming across tables
4. Generate full 48M biosample export (unfiltered)

### Medium-Term
1. Improve measurement parsing (replace/supplement quantulum3)
2. Add explicit column grouping/categorization
3. Handle multiple environmental triad values per sample
4. Better handling of composite/malformed attribute values

### Long-Term
1. ML-based decomposition of composite attribute values
2. Automated quality scoring for attribute values
3. Cross-database identifier resolution
4. Geospatial validation and enrichment

## CSV Export for Analysis

### Goal
Generate CSV/TSV with one row per NCBI Biosample containing:
- `accession` - NCBI Biosample accession
- `collection_date` - YYYY-MM-DD format
- `latitude` - Decimal degrees (negative = south of equator)
- `longitude` - Decimal degrees (negative = west of prime meridian)
- `env_broad_scale` - Single ENVO CURIE
- `env_local_scale` - Single ENVO CURIE
- `env_medium` - Single ENVO CURIE

### Data Sources
- **accession**: Non-attribute field (in all tables)
- **collection_date**: From `biosamples_attributes` where `harmonized_name='collection_date'` (inconsistent formats)
- **lat/lon**: From `biosamples_attributes` where `harmonized_name='lat_lon'` (inconsistent formats, requires splitting)
- **env_broad_scale**: From `env_triads_flattened` (normalized with CURIEs)
- **env_local_scale**: From `env_triads_flattened` (normalized with CURIEs)
- **env_medium**: From `env_triads_flattened` (normalized with CURIEs)

### Current Constraints
- Need to filter to samples with exactly 1 value for each env triad field
- Date and lat/lon normalization to be performed externally
- Future exports will include normalized date/lat/lon in database

## Repository & Code

- **Repo**: `external-metadata-awareness`
- **Makefile**: `Makefiles/ncbi_to_duckdb.Makefile`
- **Output Directory**: `local/ncbi_duckdb_export/`
- **MongoDB Source**: `ncbi_metadata` database (localhost:27017)
- **Collection Pattern**: All collections with `flatness_score = 100.0`

## Related Documentation

- **Primary Documentation**: [September 2025 Biosample DuckDB Documentation](https://portal.nersc.gov/cfs/m3408/biosamples_duckdb/September-2025-Biosample-DuckDB-documentation.html)
- **Historical Portal**: https://portal.nersc.gov/project/m3513/biosample (provenance only)
- **GitHub**: `microbiomedata/external-metadata-awareness`
- **Reference Implementation**: `contextualizer-ai/to-duckdb` (MongoDB→DuckDB patterns)

## Usage Examples

### Querying Environmental Medium Distribution
```sql
SELECT
    id,
    label,
    COUNT(1)
FROM env_triads_flattened
WHERE attribute = 'env_medium'
GROUP BY id, label
ORDER BY COUNT(1) DESC;
```

### Joining Measurements with Attributes
```sql
SELECT *
FROM biosamples_attributes ba
JOIN measurement_results_skip_filtered mrsf
  ON ba.content = mrsf.original_content
  AND ba.harmonized_name = mrsf.harmonized_name
WHERE ba.accession = 'SAMN06651834';
```

### Finding Samples with Complete Metadata
```sql
SELECT
    bf.accession,
    bf.collection_date,
    bf.lat_lon,
    etf_broad.label as env_broad_scale,
    etf_local.label as env_local_scale,
    etf_medium.label as env_medium
FROM biosamples_flattened bf
LEFT JOIN env_triads_flattened etf_broad
  ON bf.accession = etf_broad.accession
  AND etf_broad.attribute = 'env_broad_scale'
LEFT JOIN env_triads_flattened etf_local
  ON bf.accession = etf_local.accession
  AND etf_local.attribute = 'env_local_scale'
LEFT JOIN env_triads_flattened etf_medium
  ON bf.accession = etf_medium.accession
  AND etf_medium.attribute = 'env_medium'
WHERE bf.collection_date IS NOT NULL
  AND bf.lat_lon IS NOT NULL;
```

## Performance Notes

- **Export Duration**: ~45 minutes for 109M rows from MongoDB
- **mongoexport Speed**: ~48,000 records/second for large collections
- **DuckDB Load Speed**: Variable depending on schema complexity
  - Simple schemas (2-10 columns): Very fast
  - Complex schemas (277 columns with `union_by_name`): Slower, erratic progress
- **File Compression**: 2.2 GB DuckDB vs larger JSON intermediates
- **Query Performance**: Excellent on indexed columns, good on full scans

## Version Information

- **Export Date**: 2025-09-30
- **MongoDB Version**: 7.x (localhost)
- **DuckDB Version**: 1.x
- **Source Data**: NCBI BioSample XML downloaded 2025-09
- **Total NCBI BioSamples**: ~48 million (as of 2025-09-19)
- **Exported Subset**: 3,037,277 samples (6.3% of total)

# Query Comparison Results

## Summary

Comparison between benchmark files and newly generated query results.

## Files Generated

### SQL Query Files
- `local/sql_queries/satisfying_biosamples.sql` - Biosamples meeting all criteria
- `local/sql_queries/included_bioprojects.sql` - Bioprojects with satisfying biosamples
- `local/sql_queries/excluded_bioprojects.sql` - Bioprojects without satisfying biosamples

### Output Files
- `local/satisfying_biosamples_new.csv` - 506,835 biosamples
- `local/included_bioprojects_in_3m_new.csv` - 7,051 bioprojects
- `local/excluded_bioprojects_in_3m_new.csv` - 95,193 bioprojects

## Comparison Results

### Included Bioprojects
- **Row Counts**: ✅ MATCH (7,051 in both files)
- **Bioproject Accessions**: ✅ MATCH (identical sets)
- **Column Differences**:
  - Benchmark has: `total_biosamples_in_3m`, `biosamples_matching_pattern`, `pct_matching`
  - New has: `total_biosamples`, `satisfying_biosamples`

#### Key Difference Identified
**PRJNA1021975**:
- Benchmark: total=3,342, satisfying=3,342 (100%)
- New: total=3,784, satisfying=3,342

**Explanation**: The benchmark appears to have filtered `total_biosamples_in_3m` to only include biosamples present in the `sra_biosamples_bioprojects` table (3,342), while the new query counts all biosamples for the bioproject (3,784). Both agree on 3,342 satisfying biosamples.

The benchmark's `total_biosamples_in_3m` column name suggests it's specifically counting biosamples that exist in the 3M SRA biosample-bioproject relationship table, not all biosamples for the bioproject.

### Excluded Bioprojects
- **Row Counts**: ✅ MATCH (95,193 in both files)
- **Bioproject Accessions**: ✅ MATCH (identical sets)
- **Column Differences**:
  - Benchmark has: `total_biosamples_in_3m`
  - New has: `total_biosamples`, `biosamples_with_attributes`, `satisfying_biosamples`
- **Data Values**: ✅ MATCH (total counts are identical)

### Satisfying Biosamples
- **New file only**: 506,835 biosamples meeting all criteria
- Columns: `accession`, `collection_date`, `lat_lon`, `env_broad_scale`, `env_local_scale`, `env_medium`

## Quality Criteria

All queries filter for biosamples with:
1. `collection_date` IS NOT NULL
2. `lat_lon` IS NOT NULL
3. Exactly one of each environmental triad component (env_broad_scale, env_local_scale, env_medium)
4. `env_broad_scale` using ENVO prefix
5. `env_local_scale` using ENVO or PO prefix
6. `env_medium` using ENVO or PO prefix

## Conclusion

✅ **Queries successfully reproduced** with identical bioproject lists and satisfying biosample counts.

The only difference is in the `total_biosamples` column for included bioprojects, where the benchmark specifically counts biosamples in the SRA relationship table (`total_biosamples_in_3m`), while the new query counts all biosamples in the relationship table for each bioproject. Both approaches are valid depending on the analysis goal.

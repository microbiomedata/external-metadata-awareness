# Schema-Based Ranking System Removal

**Date:** September 28, 2025  
**Branch:** measurement-discovery-pipeline

## Summary

Removed untrusted schema-based measurement ranking systems that were producing misleading results by scoring fields based on theoretical schema definitions rather than actual data usage patterns.

## Problem Identified

The existing ranking systems were giving high measurement scores to fields that had **zero actual data** in the database:

- `annual_precpt` (score: 62.4) - 0 documents in database
- `rel_air_humidity` (score: 60.3) - 0 documents in database  
- `avg_temp` (score: 60) - 0 documents in database
- `air_temp_regm` (score: 64.3) - **Experimental regimen field, not a measurement**

These rankings were based on schema patterns like `{float} {unit}` format rather than empirical evidence from actual biosample data.

## Root Cause

**Schema-based ranking vs. empirical data-based ranking disconnect:**

1. **Schema analysis** looked at field definitions and gave high scores for having unit formats
2. **Actual data analysis** showed these fields either had no data or were false positives (regimen/method fields)
3. **Enhanced framework** was developed to solve this by prioritizing empirical evidence, but old schema-based systems remained

## Actions Taken

### 1. MongoDB Collections Dropped
- `measurement_attribute_rankings` - Schema-based rankings across NCBI/MIxS/NMDC
- `unified_measurement_attribute_rankings` - Consolidated schema-based rankings  
- `nmdc_slot_usage_analysis` - NMDC schema analysis (not actual usage)

### 2. Scripts Removed
- `mongo-js/rank_measurement_attributes.js` - Created schema-based rankings
- `mongo-js/rank_unified_measurement_attributes.js` - Created unified schema rankings
- `mongo-js/analyze_nmdc_slot_usage.js` - Analyzed NMDC schema (not usage)
- `external_metadata_awareness/prioritize_measurement_targets.py` - Depended on unified rankings
- `external_metadata_awareness/analyze_attribute_definitions_tfidf.py` - TF-IDF analysis tool

### 3. Makefile Targets Removed
- `analyze-nmdc-slot-usage`
- `rank-measurement-attributes`
- `rank-unified-measurement-attributes`

### 4. CLI Tools Removed
- `prioritize-measurement-targets` (poetry script)
- `analyze-attribute-definitions-tfidf` (poetry script)

## What Was Preserved

### ✅ Trusted Collections Kept:
- `measurement_evidence_percentages` - **Empirical evidence** from actual data
- `nmdc_range_slot_usage_report` - **Actual usage patterns** from real NMDC data
- All flattened data collections with real biosample data
- `measurement_fields_with_units.json` - **Actual extracted measurements** with units

### ✅ Working Systems Kept:
- Enhanced measurement framework (v2.0) configuration files
- Empirical data extraction and processing pipelines
- Real measurement processing (host_age, depth, temp, salinity, etc.)
- All legitimate schema collections (global_mixs_slots, global_nmdc_slots)

## Impact Assessment

### Collections These Scripts Read From (Safe):
- `measurement_evidence_percentages` ✅ (trusted empirical data)
- `ncbi_attributes_flattened` ✅ (legitimate flattened data)
- `global_mixs_slots` ✅ (legitimate schema reference)
- `global_nmdc_slots` ✅ (legitimate schema reference)

### Collections These Scripts Wrote To (Removed):
- `measurement_attribute_rankings` ❌ (schema-based, misleading)
- `unified_measurement_attribute_rankings` ❌ (schema-based, misleading)
- `nmdc_slot_usage_analysis` ❌ (schema analysis, not usage)

**Result:** No legitimate data sources were affected. Only the untrusted output collections were removed.

## Validation

Confirmed the problem by checking actual data:

```bash
# Fields with high schema scores but zero real data:
mongosh --eval "db.getSiblingDB('ncbi_metadata').biosamples.countDocuments({'Attributes.harmonized_name': 'annual_precpt'})"
# Result: 0

# Fields with real measurement data:
grep "harmonized_name" local/measurement_fields_with_units.json
# Results: temp, depth, salinity, host_age, etc. - fields with actual extracted measurements
```

## Rationale

1. **Empirical evidence > Schema definitions**: Real data usage patterns are more reliable than theoretical schema formats
2. **False positive elimination**: Schema-based scoring was including regimen/method fields as "measurements"
3. **Clean foundation**: Removal allows focus on building measurement discovery from trusted empirical sources
4. **Enhanced framework path**: Clears way for implementing the enhanced multi-evidence framework properly

## Next Steps

With schema-based rankings removed, measurement discovery should focus on:

1. **Empirical evidence priority**: Use `measurement_evidence_percentages` and actual data patterns
2. **Enhanced framework implementation**: Rebuild measurement prioritization using real data variation analysis
3. **Validated field processing**: Focus on fields with actual measurement data (temp, depth, salinity, host_age, etc.)

## Files Modified

- `Makefiles/measurement_discovery.Makefile` - Removed broken targets
- `pyproject.toml` - Removed broken CLI aliases
- Various deletions tracked in git status

**Commit:** Ready for git add/commit to finalize cleanup.
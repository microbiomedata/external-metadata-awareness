# Environmental Context/Triad Targets Not Covered by Main Pipeline
*Analysis Date: September 29, 2025*

## Overview

While `make -f Makefiles/env_triads.Makefile env-triads` covers the core NCBI environmental context triad processing pipeline, there are several additional environmental context targets across multiple makefiles that serve different purposes and data sources.

## Main Pipeline Coverage

✅ **Covered by `env-triads` target:**
- `biosamples-flattened` - XML structure flattening
- `env-triad-value-counts` - Comprehensive triad extraction and annotation
- All annotation steps: OAK, OLS, BioPortal, semantic SQL validation
- Final `env_triads` collection assembly with provenance

## Not Covered - Additional Environmental Context Opportunities

### 1. NMDC-Specific Environmental Context Processing
**Makefile:** `Makefiles/nmdc_metadata.Makefile`

**Purpose:** Works with NMDC production data rather than NCBI data

**Key Targets:**
```bash
# Extract environmental context columns from NMDC biosamples
make -f Makefiles/nmdc_metadata.Makefile local/nmdc-production-biosamples-env-context-columns.tsv

# Get authoritative labels for environmental context terms
make -f Makefiles/nmdc_metadata.Makefile local/nmdc-production-biosamples-env-context-authoritative-labels.tsv

# Predict environmental packages from context labels
make -f Makefiles/nmdc_metadata.Makefile local/nmdc-production-biosamples-env_package-predictions.tsv

# Extract specific triad components for soil samples
make -f Makefiles/nmdc_metadata.Makefile local/nmdc-production-biosamples-soil-env_local_scale.tsv
make -f Makefiles/nmdc_metadata.Makefile local/nmdc-production-biosamples-soil-env_broad_scale.tsv
make -f Makefiles/nmdc_metadata.Makefile local/nmdc-production-biosamples-soil-env_medium.tsv
```

**Scripts Used:**
- `biosample_json_to_context_tsv.py` - Extract environmental context from NMDC JSON
- `get_authoritative_labels_only_for_nmdc_context_columns.py` - Label resolution
- `predict_env_package_from_nmdc_context_authoritative_labels.py` - ML prediction for packages

**Value:** Provides environmental package prediction capabilities and works with NMDC's production data format

### 2. MIxS Environmental Triad Schema Extraction
**Makefile:** `Makefiles/mixs.Makefile`

**Purpose:** Extract MIxS schema definitions for environmental triad fields

**Key Target:**
```bash
# Extract env_broad_scale, env_local_scale, env_medium schema from MIxS YAML
make -f Makefiles/mixs.Makefile local/mixs-env-triad.json
```

**Value:** Provides canonical MIxS schema definitions for the three environmental context fields

### 3. NCBI Environmental Candidates Collection
**Makefile:** `Makefiles/ncbi_metadata.Makefile`

**Purpose:** Create filtered collections of biosamples with complete environmental triads

**Key Targets:**
```bash
# Create collection of biosamples from 2017+ with complete environmental triads
make -f Makefiles/ncbi_metadata.Makefile create-environmental-candidates-2017-plus

# Copy environmental candidates to ncbi_metadata database
make -f Makefiles/ncbi_metadata.Makefile copy-environmental-candidates-to-ncbi-metadata
```

**Implementation:**
- Filters biosamples for collection_date >= "2017-01-01"
- Requires all three environmental fields (env_broad_scale, env_local_scale, env_medium) to be present and non-empty
- Creates `environmental_candidates_2017_plus` collection

**Value:** Pre-filters biosamples for high-quality environmental context data

### 4. GOLD Environmental Context Processing
**Makefile:** `Makefiles/gold.Makefile`

**Purpose:** Process GOLD database environmental context fields

**Key Target:**
```bash
# Full GOLD processing including environmental context normalization
make -f Makefiles/gold.Makefile gold-all
```

**Features:**
- Flattens GOLD biosample documents with environmental field focus
- Converts environmental IDs to canonical CURIEs
- Creates normalized collections with environmental context fields

**Value:** Provides environmental context processing for GOLD ecosystem data

## Workflow Recommendations

### For NCBI Environmental Context Work (Primary Use Case)
**Current setup is optimal:**
```bash
make -f Makefiles/env_triads.Makefile env-triads
```

**Optional enhancement:**
```bash
# If working with full NCBI dataset, first create environmental candidates
make -f Makefiles/ncbi_metadata.Makefile create-environmental-candidates-2017-plus
# Then run main pipeline on filtered data
make -f Makefiles/env_triads.Makefile env-triads
```

### For Cross-Database Environmental Context Analysis
**Sequential processing:**
```bash
# 1. Process NCBI environmental triads
make -f Makefiles/env_triads.Makefile env-triads

# 2. Process GOLD environmental context
make -f Makefiles/gold.Makefile gold-all

# 3. Get MIxS schema definitions for reference
make -f Makefiles/mixs.Makefile local/mixs-env-triad.json

# 4. Process NMDC environmental context (if NMDC data available)
make -f Makefiles/nmdc_metadata.Makefile local/nmdc-production-biosamples-env-context-columns.tsv
```

### For Environmental Package Prediction
**NMDC-based workflow:**
```bash
# Extract and predict environmental packages from NMDC data
make -f Makefiles/nmdc_metadata.Makefile local/nmdc-production-biosamples-env_package-predictions.tsv
```

## Data Source Compatibility

| Target | Data Source | Output Format | Integration Point |
|--------|-------------|---------------|-------------------|
| `env-triads` | NCBI biosamples | MongoDB collections | Primary pipeline |
| NMDC targets | NMDC production | TSV files | Environmental package prediction |
| MIxS target | MIxS YAML schema | JSON schema | Reference/validation |
| GOLD targets | GOLD database | MongoDB collections | Cross-database analysis |
| Environmental candidates | NCBI biosamples | MongoDB collection | Data filtering |

## Current Database Context

**Note:** The current working database was created using `create-environmental-candidates-2017-plus`, which explains why:
- Biosample count is ~3M instead of ~44M
- All biosamples have complete environmental triads
- Data quality is optimized for environmental context work

This pre-filtering makes the main `env-triads` pipeline more efficient and focused on high-quality environmental data.

## Future Integration Opportunities

1. **Cross-Database Environmental Harmonization:** Compare environmental context patterns across NCBI, GOLD, and NMDC
2. **Environmental Package Prediction:** Apply NMDC-based ML models to NCBI data
3. **Schema Validation:** Use MIxS definitions to validate environmental context completeness
4. **Temporal Analysis:** Leverage the 2017+ filter for environmental metadata quality trends
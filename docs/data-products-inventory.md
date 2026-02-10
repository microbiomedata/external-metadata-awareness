# Data Products Inventory

Full inventory of all data products from the NCBI biosample pipeline, as of 2026-02-09.
Source data: 51.7M biosamples, 1M bioprojects, 33.7M SRA pairs.

## Data Flow

```
NCBI FTP (XML)  ──►  MongoDB (29 collections)  ──►  DuckDB (17 flat tables)  ──►  Parquet (17 files)
                          │
SRA S3 (Parquet) ──► sra.duckdb ──► TSV ──┘
```

Intermediate JSON files are created during MongoDB→DuckDB export and deleted automatically after loading.

## Format Comparison

| Format | Size | Tables/Collections | Queryable? | Portable? | Notes |
|---|---:|---:|---|---|---|
| MongoDB | ~52 GB storage + 41 GB indexes | 29 | Yes (server required) | No | Authoritative source; includes nested/mixed collections |
| DuckDB | 14 GB | 17 | Yes (single file) | Yes | All flat collections; best for interactive analysis |
| Parquet | 2.9 GB | 17 | Yes (via DuckDB/Spark/pandas) | Yes | Best for sharing; ZSTD compressed |
| sra.duckdb | 670 MB | 1 | Yes | Yes | SRA pipeline intermediate; columns named differently |

## MongoDB Collections (29 total)

### Source/Native Collections (loaded from external sources)

| Collection | Rows | Data (MB) | Storage (MB) | Indexes | Fields | Exported? | Source |
|---|---:|---:|---:|---:|---:|---|---|
| `biosamples` | 51,711,888 | 134,238 | 17,851 | 1 | 15 | No (nested) | NCBI biosample_set.xml.gz |
| `bioprojects` | 1,034,221 | 1,786 | 636 | 1 | 5 | No (nested) | NCBI bioproject.xml |
| `bioprojects_submissions` | 1,034,221 | 816 | 179 | 1 | 6 | No (nested) | Split from bioprojects |
| `sra_biosamples_bioprojects` | 33,738,101 | 3,232 | 966 | 4 | 3 | **Yes** | SRA S3 Parquet → sra.duckdb → TSV → MongoDB |
| `packages` | 229 | <1 | <1 | 2 | 9 | No (nested) | NCBI schema XML |
| `attributes` | 960 | 2 | <1 | 2 | 7 | No (nested) | NCBI schema XML |

### Transformed Collections (created by MongoDB aggregation pipelines)

| Collection | Rows | Data (MB) | Storage (MB) | Indexes | Fields | Exported? |
|---|---:|---:|---:|---:|---:|---|
| `biosamples_flattened` | 51,711,888 | 50,465 | 6,740 | 6 | 39 | **Yes** |
| `biosamples_attributes` | 756,112,544 | 136,839 | 21,880 | 7 | 5-7 | **Yes** |
| `biosamples_ids` | 128,154,531 | 12,976 | 2,816 | 1 | 5 | **Yes** |
| `biosamples_links` | 30,598,841 | 4,195 | 645 | 1 | 5 | **Yes** |
| `bioprojects_flattened` | 1,034,221 | 920 | 383 | 1 | 17 | **Yes** |
| `content_pairs_aggregated` | 66,378,489 | 7,176 | 1,345 | 1 | 4 | **Yes** |
| `env_triads` | 7,722,600 | 3,069 | 316 | 2 | 5 | No (nested) |
| `env_triads_flattened` | 20,721,046 | 4,362 | 491 | 6 | 10 | **Yes** |
| `env_triad_component_labels` | 60,015 | 30 | 9 | 7 | 5 | No (mixed) |
| `env_triad_component_curies_uc` | 6,950 | 1 | 1 | 4 | 6 | No (flat but small/specialized) |
| `biosamples_env_triad_value_counts_gt_1` | 82,653 | 37 | 11 | 5 | 9 | No (mixed) |
| `measurement_results_skip_filtered` | 1,344,001 | 388 | 47 | 1 | 12 | **Yes** |
| `measurement_evidence_percentages` | 811 | <1 | <1 | 5 | 11 | **Yes** |
| `harmonized_name_usage_stats` | 810 | <1 | <1 | 5 | 4 | **Yes** |
| `harmonized_name_dimensional_stats` | 354 | <1 | <1 | 2 | 13 | **Yes** |
| `mixed_content_counts` | 595 | <1 | <1 | 3 | 3 | **Yes** |
| `attribute_harmonized_pairings` | 96,377 | 7 | 3 | 5 | 4 | **Yes** |
| `ncbi_attributes_flattened` | 960 | 1 | <1 | 4 | 7 | **Yes** |
| `ncbi_packages_flattened` | 229 | <1 | <1 | 4 | 4 | **Yes** |
| `unit_assertion_counts` | 230 | <1 | <1 | 4 | 4 | **Yes** |
| `global_mixs_slots` | 788 | <1 | <1 | 4 | 14 | No (nested) |
| `global_nmdc_slots` | 846 | 1 | <1 | 5 | 16 | No (nested) |
| `nmdc_range_slot_usage_report` | 55 | <1 | <1 | 5 | 14 | No (nested) |

### What's NOT in DuckDB/Parquet (and why)

- **`biosamples`** (raw): Deeply nested XML structure with embedded documents and arrays
- **`bioprojects`**, **`bioprojects_submissions`**: Nested project structures
- **`packages`**, **`attributes`**: Nested schema definitions (flat versions ARE exported)
- **`env_triads`**: Pre-flattened version with nested annotation objects
- **`env_triad_component_labels`**, **`biosamples_env_triad_value_counts_gt_1`**: Mixed structure (flat base + enrichment arrays)
- **`global_mixs_slots`**, **`global_nmdc_slots`**, **`nmdc_range_slot_usage_report`**: Nested YAML-derived schema data

## DuckDB Tables (17 flat collections)

File: `local/ncbi_duckdb_export/ncbi_metadata_flat_20260208.duckdb` (14 GB)
Symlink: `ncbi_metadata_flat_latest.duckdb`

| Table | Rows | Cols | Parquet (MB) | Notes |
|---|---:|---:|---:|---|
| `biosamples_flattened` | 51,711,888 | 180 | 1,363 | Wide sparse table; 180 columns across all 51.7M docs |
| `biosamples_attributes` | 756,112,544 | 7 | 1,690 | Largest table; EAV of all attributes |
| `biosamples_ids` | 128,154,531 | 6 | 455 | Cross-database identifiers |
| `content_pairs_aggregated` | 66,378,489 | 3 | 198 | Unique (harmonized_name, content) pairs |
| `sra_biosamples_bioprojects` | 33,738,101 | 2 | 286 | BioSample↔BioProject linkage |
| `biosamples_links` | 30,598,841 | 5 | 78 | External cross-references |
| `env_triads_flattened` | 20,721,046 | 9 | 24 | Environmental context (3 rows/sample) |
| `measurement_results_skip_filtered` | 1,344,001 | 11 | 7 | Parsed numeric measurements |
| `bioprojects_flattened` | 1,034,221 | 16 | 169 | All bioprojects, flattened |
| `attribute_harmonized_pairings` | 96,377 | 3 | 1 | Submitter→harmonized name map |
| `measurement_evidence_percentages` | 811 | 10 | <1 | Per-field measurement assessment |
| `harmonized_name_usage_stats` | 810 | 3 | <1 | Sample/project counts per field |
| `ncbi_attributes_flattened` | 960 | 6 | <1 | NCBI attribute definitions |
| `mixed_content_counts` | 595 | 2 | <1 | Fields with mixed content types |
| `harmonized_name_dimensional_stats` | 354 | 12 | <1 | Measurement characteristics by field |
| `unit_assertion_counts` | 230 | 3 | <1 | Unit usage tabulations |
| `ncbi_packages_flattened` | 229 | 10 | <1 | NCBI package definitions |

### Resolved: `biosamples_flattened` Date Parsing Fix

During the initial Feb 2026 export, `biosamples_flattened` silently failed because DuckDB auto-detected date columns (e.g., `collection_date`) as DATE type, then choked on malformed values like `"08-2012"` at row 2.4M. The Makefile loop had no error handling, so it deleted the 50GB JSON and continued.

**Fixes applied**:
1. Added `dateformat='DISABLED', timestampformat='DISABLED'` to all `read_json` calls — prevents DATE/TIMESTAMP inference, keeps all date-like columns as VARCHAR (correct for messy NCBI data)
2. Added per-step error handling in `make-database` loop — preserves JSON on failure, reports failed collections at end
3. Table successfully bolted into existing DuckDB via manual `duckdb` command + `export-parquet`

**Note**: `biosamples_flattened` has 180 columns in DuckDB (vs 39 in any single MongoDB document) because `union_by_name=true` collects all sparse fields across 51.7M docs. MongoDB's `findOne()` only shows fields present in one document.

## Parquet Files

Directory: `local/ncbi_duckdb_export/parquet/` (2.9 GB total, ZSTD compressed)

One `.parquet` file per DuckDB table. Same 17 tables (once `biosamples_flattened` is re-exported).

## Other DuckDB Files

| File | Size | Tables | Role |
|---|---:|---:|---|
| `local/sra.duckdb` | 670 MB | 1 (`sra_biosamples_bioprojects`) | **SRA pipeline intermediate** — created during `sra_metadata.Makefile`, upstream of MongoDB. Column names differ: `biosample`/`bioproject` vs `biosample_accession`/`bioproject_accession` in main DuckDB. Not redundant — it's part of the SRA build pipeline and enables ad-hoc queries against raw SRA parquet shards. |

## Pipeline Order of Creation

| Step | Makefile | Duration (51.7M) | Produces |
|---|---|---:|---|
| 1 | `ncbi_metadata.Makefile` | ~overnight | `biosamples`, `bioprojects`, `bioprojects_submissions` |
| 2 | `ncbi_metadata.Makefile` (flatten) | ~6 hours | `biosamples_flattened`, `biosamples_attributes`, `biosamples_ids`, `biosamples_links`, `bioprojects_flattened` |
| 3 | `sra_metadata.Makefile` | ~15 min | `sra.duckdb` → TSV → `sra_biosamples_bioprojects` |
| 4 | `ncbi_schema.Makefile` | ~10 sec | `attributes`, `packages`, `ncbi_attributes_flattened`, `ncbi_packages_flattened` |
| 5 | `env_triads.Makefile` | ~10 hours | `env_triads`, `env_triads_flattened`, `env_triad_component_labels`, etc. |
| 6 | `measurement_discovery.Makefile` | ~24 hours | `content_pairs_aggregated`, `measurement_results_skip_filtered`, stats collections |
| 7 | `ncbi_to_duckdb.Makefile` | ~6-8 hours | DuckDB file (17 tables) + Parquet files (17 files) |
| | **Total** | **~3-4 days** | |

## What to Share

| Audience | Format | Size | How |
|---|---|---:|---|
| Analysts who want to query | DuckDB | 14 GB | Single file download from NERSC portal |
| Data engineers / pipeline consumers | Parquet | 2.9 GB | Per-table files from NERSC portal |
| R / Python notebook users | Parquet | 2.9 GB | `read_parquet()` in DuckDB, pandas, or arrow |
| Collaborators who need everything | DuckDB + Parquet | 17 GB | Both on NERSC portal |

**Do NOT share**: MongoDB dumps, raw XML, SRA parquet shards, intermediate JSON, `sra.duckdb`.

## Querying Each Format

### DuckDB (recommended for interactive use)
```bash
duckdb local/ncbi_duckdb_export/ncbi_metadata_flat_latest.duckdb
```
```sql
-- All tables available, cross-table joins work
SELECT bf.accession, bf.organism_name, bf.geo_loc_name
FROM biosamples_flattened bf
JOIN sra_biosamples_bioprojects sbp ON bf.accession = sbp.biosample_accession
WHERE sbp.bioproject_accession = 'PRJNA12345';
```

### Parquet (no DuckDB file needed)
```sql
-- DuckDB can query Parquet directly
SELECT * FROM read_parquet('parquet/biosamples_flattened.parquet')
WHERE organism_name LIKE '%Pseudomonas%' LIMIT 10;

-- Cross-file joins
SELECT bf.accession, etf.env_broad_scale
FROM read_parquet('parquet/biosamples_flattened.parquet') bf
JOIN read_parquet('parquet/env_triads_flattened.parquet') etf ON bf.accession = etf.accession;
```
```python
# Python
import pandas as pd
df = pd.read_parquet('biosamples_flattened.parquet')

# R
library(arrow)
df <- read_parquet("biosamples_flattened.parquet")
```

### MongoDB (server required)
```bash
mongosh mongodb://localhost:27017/ncbi_metadata
```
```javascript
// Only format with nested collections (raw biosamples, env_triads, schema slots)
db.biosamples.findOne({accession: "SAMN12345678"})
db.biosamples_flattened.find({organism_name: /Pseudomonas/}).limit(5)

// MongoDB-only collections (not in DuckDB/Parquet):
db.env_triads.findOne()           // pre-flattened nested triads
db.global_mixs_slots.findOne()    // MIxS schema properties
db.biosamples.findOne()           // raw XML structure
```

### Recreating Deleted JSON (if ever needed)
```bash
mongoexport --db ncbi_metadata --collection biosamples_flattened --type=json --out biosamples_flattened.json
# Warning: 51.7M docs × 39 fields = very large JSON. Prefer DuckDB/Parquet.
```

## NERSC Documentation Status

The NERSC portal documentation at `September-2025-Biosample-DuckDB-documentation.html` describes the **old 3M-subset** (triad-complete, 2017+ collection dates). Key differences from the current full-corpus export:

| Aspect | NERSC Sep 2025 | Current Feb 2026 |
|---|---|---|
| Scope | 3M triad-complete subset | **Full 51.7M corpus** |
| `biosamples_flattened` | 3,037,277 | **51,711,888** |
| `biosamples_attributes` | 52,518,729 | **756,112,544** |
| `bioprojects_flattened` | not present | **1,034,221** (new) |
| `env_triads_flattened` | 9,262,719 | **20,721,046** |
| `sra_biosamples_bioprojects` | 31,809,491 | **33,738,101** |
| `content_pairs_aggregated` | 2,331,732 | **66,378,489** |
| `measurement_results_skip_filtered` | 87,466 | **1,344,001** |

The NERSC documentation's table descriptions, column semantics, data lineage, and usage guidance remain accurate. Row counts and scope need updating when the new export is uploaded.

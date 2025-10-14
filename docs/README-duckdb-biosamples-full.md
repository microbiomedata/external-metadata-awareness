# Biosample Flattening Project – DuckDB Outputs

## Table of Contents
- [Overview](#overview)  
- [Hosting and Access](#hosting-and-access)  
- [Scope and Filtering](#scope-and-filtering)  
- [Current DuckDB Offerings](#current-duckdb-offerings)  
  - [NCBI Outputs](#ncbi-outputs)  
  - [GOLD Outputs](#gold-outputs)  
  - [NMDC Outputs](#nmdc-outputs)  
- [Key Tables (NCBI Subset)](#key-tables-ncbi-subset)  
- [Lineage and Grain](#lineage-and-grain)  
- [Omitted XML Paths](#omitted-xml-paths)  
- [Why DuckDB Now](#why-duckdb-now)  
- [Strengths](#strengths)  
- [Limitations](#limitations)  
- [Comparison to Past Outputs](#comparison-to-past-outputs)  
- [Historical Systems (Repos × Engines × Timeline)](#historical-systems-repos--engines--timeline)  
- [Validation Checklist](#validation-checklist)  
- [Known Discrepancies](#known-discrepancies)  
- [Future Directions](#future-directions)  

---

## Overview
This project flattens and enriches biosample metadata from **NCBI**, **GOLD**, and **NMDC**, producing portable **DuckDB databases**.

> ⚠️ **Documentation freshness**: Some older markdown (e.g. Claude Code journaling) may be outdated or contradictory. Always **defer to the most recent docs** and confirm counts with the current DuckDB exports. Older portals are kept for provenance only.

---

## Hosting and Access
- ✅ **Active, authoritative portal**:  
  https://portal.nersc.gov/cfs/m3408/biosamples_duckdb/  

- ⚠️ **Historical portal (for provenance only)**:  
  https://portal.nersc.gov/project/m3513/biosample  

---

## Scope and Filtering
- **NCBI BioSamples** total: ~48 million.  
- **DuckDB subset**:  
  - 3,037,277 rows in `biosamples_flattened` (current authoritative count)  
  - Earlier materialization (session data) reported 4,559,870 — see [Known Discrepancies](#known-discrepancies)  
- Filtered because samples must:  
  - Have `collection_date ≥ 2017-01-01`  
  - Contain all three MIxS **environmental triads**:  
    - `env_broad_scale`  
    - `env_local_scale`  
    - `env_medium`  

- **Rationale**: Matches the 2017–2024 window of the [Google Earth Satellite Embedding V1 Annual](https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_SATELLITE_EMBEDDING_V1_ANNUAL).

---

## Current DuckDB Offerings

### NCBI Outputs
- **Biosamples subset**: 3.0M triad-complete samples  
- **Attributes**: 52.5M raw rows (`biosamples_attributes`)  
- **Derived**: normalized environmental triads, parsed measurements, aggregated content pairs, harmonization stats

### GOLD Outputs
Two complementary DuckDBs are offered:

| Build | Entity Coverage | Field Richness | Processing Lineage | Typical Use |
|-------|----------------|----------------|--------------------|-------------|
| **API-based** | Studies, Projects, Biosamples (no isolates) | ~50+ biosample fields, full triads (e.g. latitude/longitude, env triads, sequencing depth) | GOLD API → MongoDB → DuckDB | Rich biosample analyses |
| **Excel-based** | All entity types (incl. isolates) | ~15 fields per entity (e.g. study_id, project_id, organism_name, basic metadata) | Bulk Excel export → flatten → DuckDB | Broad coverage, lightweight schema |

> 💡 **When to choose**: API build for **depth**; Excel build for **breadth**. Use API when you need triads and rich biosample fields; Excel when you need isolates or all entities but can tolerate fewer columns.

### NMDC Outputs
- **Source**: NMDC **Runtime API** (data source only; not a transformation repo).  
- **Underlying engine**: NMDC production MongoDB.  
- **Flattened collections**: includes `biosample_set`, workflow metadata, and annotations.  
- **Modeling**: aligns with **NMDC-schema (LinkML)**; slots map cleanly into DuckDB columns.  
- **Purpose**: serves as schema-driven reference against noisier NCBI/GOLD.

---

## Key Tables (NCBI Subset)

> Note: **SQL queries are intentionally omitted for now**. This section focuses on table shape, usage, and caveats.

### `biosamples_flattened` — 3,037,277 rows
- **Grain**: 1 row per BioSample accession  
- **Canonicality**: Canonical (authoritative for sample counts)  
- **Parent source**: Derived from NCBI XML parsing  
- **Safe joins**: join on `accession`  
- **Anti-patterns**: don’t count samples using `env_triads_flattened` or `biosamples_attributes`  
- **Examples**: `collection_date`, `geo_loc_name`, `env_broad_scale`, `tax_id`

### `biosamples_attributes` — 52,518,729 rows
- **Grain**: 1 row per attribute-value pair  
- **Canonicality**: Canonical (raw long form)  
- **Parent source**: Flattened directly from XML paths  
- **Safe joins**: join on `accession`  
- **Anti-patterns**: treating every row as a measurement  
- **Examples**:  
  - `attribute_name="isolation source"`, `content="soil"`  
  - `attribute_name="altitude"`, `content="300 m"`  

### `env_triads_flattened` — 9,262,719 rows
- **Grain**: 1 row per triad component  
- **Canonicality**: Derived  
- **Parent source**: `biosamples_flattened` (triad fields exploded and normalized)  
- **Safe joins**: join back on `accession`  
- **Anti-patterns**: counting samples here  
- **Examples**:  
  - `env_broad_scale="marine biome"`  
  - `env_medium="seawater"`  

### `measurement_results_skip_filtered` — 87,466 rows
- **Grain**: 1 row per parsed measurement  
- **Canonicality**: Derived  
- **Parent source**: `biosamples_attributes`  
- **Safe joins**: `(accession, harmonized_name)`  
- **Anti-patterns**: assuming this is complete (skip list deliberately excludes non-measurements)  
- **Known parsing pitfalls**: PSU mis-parses; parentheses around units; ambiguous chemistry tokens  

### `sra_biosamples_bioprojects` — 31,809,491 rows
- **Grain**: 1 row per relation  
- **Canonicality**: Canonical  
- **Purpose**: links SRA ↔ BioSample ↔ BioProject  
- **Safe joins**: join on `biosample_accession`  
- **Anti-patterns**: counting rows as samples without deduplication

### `biosamples_ids` — 7,871,449 rows
- **Grain**: 1 row per ID record  
- **Canonicality**: Canonical  
- **Examples**:  
  - `db="SRA"`, `is_primary=true`  
  - `label="BioSample: SAMN12345678"`

### `biosamples_links` — 2,335,376 rows
- **Grain**: 1 row per link  
- **Canonicality**: Canonical  
- **Purpose**: cross-database references and provenance  

### `content_pairs_aggregated` — 2,331,732 rows
- **Grain**: 1 row per unique (harmonized_name, content) pair  
- **Canonicality**: Derived  
- **Purpose**: drives skip lists and normalization targets  
- **Limitation**: expensive at scale; best used for QA  

### `attribute_harmonized_pairings` — 20,937 rows
- **Purpose**: maps submitter-provided field names to harmonized names  
- **Use**: reconciliation, QA  

### `ncbi_attributes_flattened` — 960 rows
- **Purpose**: dictionary of attributes from NCBI  
- **Use**: schema reference  

### `ncbi_packages_flattened` — 229 rows
- **Purpose**: package definitions (MIGS, MIMS, etc.)  
- **Use**: interpret package-level field expectations  

### `harmonized_name_usage_stats` — 695 rows
- **Purpose**: counts of biosamples per harmonized field  
- **Use**: field prioritization  

### `measurement_evidence_percentages` — 695 rows
- **Purpose**: percent of measurement-like evidence per field  
- **Use**: validates which fields reliably yield numerics  

### `mixed_content_counts` — 440 rows
- **Purpose**: identifies fields with mixed semantics (numbers + free text)  
- **Use**: flags curation hot spots  

### `harmonized_name_dimensional_stats` — 432 rows
- **Purpose**: distributional stats per field  
- **Use**: feature selection, QA  

### `unit_assertion_counts` — 13 rows
- **Purpose**: sanity check on inferred units  
- **Use**: validation of unit parsing

---

## Lineage and Grain

### Data Flow
```
biosamples_flattened ──→ env_triads_flattened
       │
       └─→ biosamples_attributes ──→ measurement_results_skip_filtered
                         │
                         └─→ content_pairs_aggregated
```
Summaries (e.g., `harmonized_name_*`, `mixed_content_counts`) derive from these.

### Analytics vs Normalization
This design is **intentionally denormalized** for analytics. Think of it as a **star-schema/lakehouse**: fact tables at different grains plus conformed dimensions. It is *not* 3NF OLTP.  

**Implication**: duplication across tables is deliberate. Correct use requires respecting row grain and join rules.

---

## Omitted XML Paths
Flattening does **not** include every XML path.  

- **Excluded categories**:  
  - Administrative-only metadata  
  - Empty placeholder nodes  
  - Redundant container/wrapper paths  

- **Included categories**:  
  - Scientific attributes  
  - Environmental triads  
  - Measurements  
  - Taxonomy  
  - Geospatial & temporal fields  

See the **NERSC README** for the authoritative inclusion/exclusion specification.

---

## Why DuckDB Now
- **Portable** `.duckdb` files  
- **Performant** on tens of millions of rows  
- **Consistent** schemas across NCBI/GOLD/NMDC  
- **Adopted** externally — already in use by other groups  

---

## Strengths
- Triad-complete subset aligned with satellite embeddings  
- Parsed measurements and normalized triads  
- Portable, schema-stable exports  
- Cross-database harmonization  

---

## Limitations
- Schema instability → record version/date for every export  
- Quantulum3 parsing pitfalls (PSU, parentheses, chemistry tokens)  
- Subset bias: 3M of 48M NCBI samples included  
- Computational constraints: full-corpus aggregates (e.g. `content_pairs_aggregated` at 45M scale) may be impractical  

---

## Comparison to Past Outputs
- **2019–2020**: XML DB experiments (`biosample-xmldb-sqldb`, `biosample-basex`) — overlapping efforts, different XML DB engines  
- **2020–2021**: Early MongoDB pipelines (`sample-annotator`, `biosample-analysis`)  
- **2022–2023**: External Metadata Awareness (MongoDB, SQLite, early DuckDB trials; scaled to 40M+)  
- **2024–2025**: Consolidated DuckDB distributions across NCBI, GOLD, NMDC  

---

## Historical Systems (Repos × Engines × Timeline)

| Repo | Owner | DB/Tech | Role | Notes | Dates (verify) | Contributors (verify) |
|------|-------|---------|------|-------|----------------|------------------------|
| turbomam/biosample-xmldb-sqldb | turbomam | XML→SQL | NCBI XML relational prototype | Overlaps with basex era | … | … |
| turbomam/biosample-basex | turbomam | BaseX (XML DB) | XML-native store | Overlaps with xmldb-sqldb | … | … |
| INCATools/biosample-analysis | INCATools | Python/OAK | Analysis notebooks, cross-repo | … | … | … |
| microbiomedata/sample-annotator | microbiomedata | MongoDB | Early flattening pipelines | Came before xmldb/basex | … | … |
| microbiomedata/external-metadata-awareness | microbiomedata | MongoDB + SQLite + DuckDB | Large-scale flattening, 40M+ corpus | … | … | … |
| contextualizer-ai/to-duckdb | contextualizer-ai | DuckDB | Universal migration tooling | … | … | … |
| gold-tools | (owner TBD) | MongoDB + DuckDB | GOLD API ingestion | … | … | … |
| microbiomedata/nmdc-runtime | microbiomedata | API/MongoDB (source only) | NMDC data source | Not a transform repo | … | … |
| INCATools/ontology-access-kit | INCATools | Python lib | Used for ontology lookups in some phases | … | … | … |
| turbomam/berkeley-biosample-analysis | turbomam | Python/analysis | Personal repo for exploratory analyses | … | … | … |

---

## Validation Checklist
1. **Version banner** (add to README header):  
   `Export: YYYY-MM-DD • Build: vX.Y • Code commit: <hash>`  
2. **DuckDB table counts**  
   ```bash
   duckdb -c "SELECT table_name, row_count FROM duckdb_tables()" file.duckdb
   ```
3. **NERSC manifest**  
   ```bash
   ls -lh /global/cfs/cdirs/m3408/biosamples_duckdb
   ```
4. **MongoDB collection counts**  
   ```bash
   db.collection.stats().count
   ```
5. **GitHub repo timelines & contributors**  
   ```bash
   git log --reverse --format="%ad %h %s" | head -1
   git log -1 --format="%ad %h %s"
   git shortlog -sne --all | head -20
   ```

---

## Known Discrepancies
- Earlier docs rounded to “~3M samples”; recent sessions report **4,559,870** materialized. Current DuckDB authoritative count is **3,037,277**.  
  → Always validate against the current export.  
- GOLD builds differ: API vs Excel. See [GOLD Outputs](#gold-outputs).  
- Schema names shift — always record export date/version.  

---

## Future Directions
- Replace/supplement Quantulum3 for unit parsing  
- Extend beyond triad-complete subset  
- Stabilize schema naming/versioning  
- Integrate geospatial embeddings at scale  

---

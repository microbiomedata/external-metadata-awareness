# Environmental Triad Value Set Lifecycle

This document provides step-by-step instructions for creating and maintaining NMDC environmental triad value sets. For the architectural decision and rationale, see [ADR-0015: Environmental Triad Value Sets](https://github.com/microbiomedata/issues/blob/main/decisions/0015-env-triad-value-sets.md).

## Overview

The environmental triad value set workflow spans two repositories and Google Sheets:

1. **external-metadata-awareness** (this repo): Process NCBI BioSample database and generate voting sheets
2. **Google Sheets**: Upload voting sheets, gather votes from domain experts
3. **submission-schema**: Download voted sheets, simplify them, inject LinkML enumerations

```
┌─────────────────────────────────────┐
│     external-metadata-awareness     │
├─────────────────────────────────────┤
│ 1. NCBI BioSample XML → MongoDB     │
│ 2. MongoDB → flattened collections  │
│ 3. MongoDB → DuckDB export          │
│ 4. Generate voting sheet TSVs       │
└──────────────────┬──────────────────┘
                   │ upload TSVs
                   ▼
┌─────────────────────────────────────┐
│          Google Sheets              │
├─────────────────────────────────────┤
│ 5. Share with domain experts        │
│ 6. Experts add +1/-1 vote columns   │
│ 7. Aggregate votes                  │
└──────────────────┬──────────────────┘
                   │ download voted sheets
                   ▼
┌─────────────────────────────────────┐
│        submission-schema            │
├─────────────────────────────────────┤
│ 8. Simplify TSVs (id + label only)  │
│ 9. Generate LinkML enumerations     │
│ 10. Inject into schema              │
│ 11. Build and publish to GH Pages   │
└─────────────────────────────────────┘
```

---

## Part 1: Building the NCBI BioSample DuckDB

The voting sheet generation requires a DuckDB database derived from the [NCBI BioSample database](https://www.ncbi.nlm.nih.gov/biosample/). You can either download a pre-built version from NERSC or build it from scratch.

### Option A: Download Pre-Built DuckDB from NERSC

Pre-built DuckDB files are available from NERSC, though they may not reflect the latest NCBI data and the directory structure has evolved over time. Check file dates and READMEs carefully.

- **Portal**: https://portal.nersc.gov/cfs/m3408/biosamples_duckdb/
- **Required tables**: `biosamples_flattened`, `env_triads_flattened`
- **Documentation**: [README-duckdb-biosamples-full.md](./README-duckdb-biosamples-full.md)

```bash
mkdir -p local
# Check portal for current filename and date
wget -P local/ https://portal.nersc.gov/cfs/m3408/biosamples_duckdb/ncbi_biosamples_YYYY-MM-DD.duckdb
```

For the most current data, build from scratch (Option B).

### Option B: Build DuckDB from Scratch

Building from scratch requires MongoDB and significant compute resources (~32GB RAM recommended).

> **Technical Reference**: For detailed documentation of the MongoDB annotation pipeline (OAK/OLS/BioPortal annotation, collection schemas, script details), see [env-triad-data-pipeline.md](./env-triad-data-pipeline.md).

#### Prerequisites

- MongoDB (local or remote; see authentication note below)
- ~50GB disk space for XML and intermediate files
- ~32GB RAM for processing
- BioPortal API key (see setup below)

**BioPortal API key**: Required for ontology lookups. Get a free key at https://bioportal.bioontology.org/account and add to `local/.env`:
```
BIOPORTAL_API_KEY=your-key-here
```

**MongoDB authentication**: For authenticated MongoDB instances, use a URI with credentials:
```
MONGO_URI="mongodb://username:password@host:port/ncbi_metadata?authMechanism=SCRAM-SHA-256&authSource=admin"
```
You can also store credentials in `local/.env` and reference via `ENV_FILE=local/.env` in Make commands.

#### Step 1: Download and Load NCBI BioSample Database into MongoDB

The NCBI BioSample database is distributed as a single XML file from NCBI's FTP server.

```bash
cd external-metadata-awareness

# Download NCBI BioSample XML (~3GB compressed, ~30GB uncompressed)
# Source: https://ftp.ncbi.nlm.nih.gov/biosample/biosample_set.xml.gz
make -f Makefiles/ncbi_metadata.Makefile downloads/biosample_set.xml.gz
make -f Makefiles/ncbi_metadata.Makefile local/biosample_set.xml

# Extract last biosample ID for progress tracking
make -f Makefiles/ncbi_metadata.Makefile local/biosample-last-id-val.txt

# Load into MongoDB (~10 hours for full dataset)
make -f Makefiles/ncbi_metadata.Makefile load-biosamples-into-mongo \
    MONGO_URI="mongodb://localhost:27017/ncbi_metadata"
```

#### Step 2: Flatten Biosamples in MongoDB

```bash
# Flatten biosamples collection (~30 minutes for 45M samples)
make -f Makefiles/env_triads.Makefile biosamples-flattened \
    MONGO_URI="mongodb://localhost:27017/ncbi_metadata"
```

This creates the `biosamples_flattened` collection with denormalized environmental context fields.

#### Step 3: Process Environmental Triad Values

```bash
# Extract and annotate env triad values (~2 hours total)
make -f Makefiles/env_triads.Makefile env-triad-value-counts \
    MONGO_URI="mongodb://localhost:27017/ncbi_metadata" \
    ENV_FILE=local/.env
```

This creates:
- `biosamples_env_triad_value_counts_gt_1`
- `env_triad_component_labels`
- `env_triad_component_curies_uc`
- `env_triads`

#### Step 4: Flatten Environmental Triads

```bash
# Create env_triads_flattened collection
make -f Makefiles/env_triads.Makefile env-triads-flattened \
    MONGO_URI="mongodb://localhost:27017/ncbi_metadata"
```

#### Step 5: Create Additional Flattened Collections

```bash
# Flatten biosample IDs, links, and attributes
make -f Makefiles/ncbi_metadata.Makefile flatten_biosamples_ids \
    MONGO_URI="mongodb://localhost:27017/ncbi_metadata"

make -f Makefiles/ncbi_metadata.Makefile flatten_biosamples_links \
    MONGO_URI="mongodb://localhost:27017/ncbi_metadata"

make -f Makefiles/ncbi_metadata.Makefile flatten_biosample_attributes \
    MONGO_URI="mongodb://localhost:27017/ncbi_metadata"
```

#### Step 6: Export to DuckDB

```bash
# Export all flat collections to DuckDB
make -f Makefiles/ncbi_to_duckdb.Makefile make-database \
    MONGO_URI="mongodb://localhost:27017/ncbi_metadata"

# Verify the export
make -f Makefiles/ncbi_to_duckdb.Makefile show-summary
```

Output: `local/ncbi_duckdb_export/ncbi_metadata_flat_YYYYMMDD.duckdb`

### DuckDB Tables Reference

The voting sheet generation requires these tables:

| Table | Rows (approx) | Purpose |
|-------|---------------|---------|
| `biosamples_flattened` | 3M+ | One row per biosample with env fields |
| `env_triads_flattened` | 9M+ | One row per triad component |

See [README-duckdb-biosamples-full.md](./README-duckdb-biosamples-full.md) for complete table documentation.

---

## Part 2: Voting Sheet Generation

### Software Prerequisites

```bash
cd external-metadata-awareness
poetry install
```

### 2.1 Configure the Environment

**File location**: `notebooks/environmental_context_value_sets/voting_sheets_configurations.yaml`

Each configuration defines how to generate a voting sheet for one environment/slot combination.

#### Configuration Variables Reference

**Output Settings**

| Variable | Description | Example |
|----------|-------------|---------|
| `output_file_name` | Path where the TSV voting sheet will be written | `"voting_sheets_output/soil_env_broad_scale_voting_sheet.tsv"` |

**Semantic Anchors**

| Variable | Description | Example |
|----------|-------------|---------|
| `semantic_anchors` | List of ENVO parent class CURIEs used to seed candidate terms. All descendants of these classes are considered. | `["ENVO:00000428"]` (biome) |

Common semantic anchors by slot:
- `env_broad_scale`: `ENVO:00000428` (biome)
- `env_local_scale`: `ENVO:01000813` (astronomical body part), `ENVO:01000355` (vegetation layer)
- `env_medium`: `ENVO:00010483` (environmental material)

**Data Source Selectors**

| Variable | Description | Example |
|----------|-------------|---------|
| `gold_context_selectors` | MIxS predicates to extract from GOLD biosample data | `["mixs:env_broad", "mixs:env_local", "mixs:env_medium"]` |
| `ncbi_context_selector` | NCBI BioSample attribute name to query | `"env_broad_scale"`, `"env_local_scale"`, `"env_medium"` |
| `nmdc_context_selector` | NMDC biosample slot to query | `"env_broad_scale_id"`, `"env_local_scale_id"`, `"env_medium_id"` |

**Package/Environment Filters**

Each data source uses a different filtering mechanism:

| Variable | Applied To | Description | Example |
|----------|------------|-------------|---------|
| `first_where` | **GOLD ontology** | SQL WHERE clause for goldterms.db (SemanticSQL) | `"lower(s1.value) like '%soil%'"` |
| `ncbi_package_selector` | **NCBI** | Package suffix matched via `LIKE '%...'` | `"soil.6.0"`, `"built.6.0"` |
| `nmdc_package_selector` | **NMDC** | Exact match on `env_package.has_raw_value` | `"soil"`, `"water"` |

**Comparison Settings** (for tracking changes between schema versions)

| Variable | Description | Example |
|----------|-------------|---------|
| `CONTEXT_ENUM` | Name of existing enum in submission-schema to compare against | `"EnvBroadScaleSoilEnum"` |
| `previous_submission_schema_url` | Raw GitHub URL of previous schema version | `"https://raw.githubusercontent.com/microbiomedata/submission-schema/v10.7.0/..."` |
| `comparison_enum_column_name` | Column name in output for comparison data | `"EnvBroadScaleSoilEnum_10_7"` |

For new value sets with no prior version, set `CONTEXT_ENUM: ""` (empty string).

#### Example Configuration

```yaml
soil_env_medium:
  output_file_name: "voting_sheets_output/soil_env_medium_voting_sheet.tsv"
  semantic_anchors:
    - "ENVO:00010483"  # environmental material
  gold_context_selectors:
    - "mixs:env_broad"
    - "mixs:env_local"
    - "mixs:env_medium"
  ncbi_context_selector: "env_medium"
  nmdc_context_selector: "env_medium_id"
  first_where: "lower(s1.value) like '%soil%'"
  ncbi_package_selector: "soil.6.0"
  nmdc_package_selector: "soil"
  CONTEXT_ENUM: "EnvMediumSoilEnum"
  previous_submission_schema_url: "https://raw.githubusercontent.com/microbiomedata/submission-schema/refs/tags/v11.1.0/src/nmdc_submission_schema/schema/nmdc_submission_schema.yaml"
  comparison_enum_column_name: "EnvMediumSoilEnum_11_1"
```

#### Adding a New Environment Configuration

```yaml
air_env_broad_scale:
  output_file_name: "voting_sheets_output/air_env_broad_scale_voting_sheet.tsv"
  semantic_anchors:
    - "ENVO:00000428"  # biome
  gold_context_selectors:
    - "mixs:env_broad"
    - "mixs:env_local"
    - "mixs:env_medium"
  ncbi_context_selector: "env_broad_scale"
  nmdc_context_selector: "env_broad_scale_id"
  first_where: "lower(s1.value) like '%air%'"
  ncbi_package_selector: "air.6.0"
  nmdc_package_selector: "air"
  CONTEXT_ENUM: ""  # empty - no existing enum
  previous_submission_schema_url: "https://raw.githubusercontent.com/microbiomedata/submission-schema/refs/tags/v11.1.0/src/nmdc_submission_schema/schema/nmdc_submission_schema.yaml"
  comparison_enum_column_name: "no_comparison_enum"
```

### 2.2 Data Sources

The voting sheet notebook pulls candidate terms from three data sources:

**NCBI BioSamples (DuckDB)**

The DuckDB file contains flattened NCBI BioSample data. The notebook queries for terms actually used in biosamples matching the configured package selector.

> **Schema Note**: The notebook currently requires the **old schema** with `attributes` and `links` tables (e.g., `ncbi_biosamples_2024-09-23.duckdb`). Newer "flat" schema files have different table names and won't work without notebook modifications. See [Known Issues](#known-issues).

**NMDC Biosamples (Runtime API)**

Live data from the NMDC Runtime API (`https://api.microbiomedata.org/nmdcschema/`). No configuration needed—the notebook fetches directly from the public API and caches results locally in `all_nmdc_biosamples.json`.

**GOLD Data (Two Sources)**

The notebook downloads two GOLD resources:

| Source | URL | Format | Purpose |
|--------|-----|--------|---------|
| Biosample Data | `https://gold.jgi.doe.gov/download?mode=site_excel` | Excel | Actual biosample records |
| GOLD Ontology | `https://s3.amazonaws.com/bbop-sqlite/goldterms.db.gz` | SQLite | Ontology terms for `first_where` filtering |

**Manual Curation Files**

The notebook uses one manually curated override file:

| File | Purpose |
|------|---------|
| `mam-env-package-overrides.tsv` | Manual overrides for NMDC biosample env_package predictions when automated inference fails or is incorrect |

Note: Some one-off notebooks in submission-schema (e.g., `soil/discover_excludable_soils.ipynb` for soil env_medium) used additional curated exclusion files. These are not part of the main voting sheet workflow.

### 2.3 Run the Voting Sheet Generator

**Always run the notebook interactively.** While CLI execution via `jupyter nbconvert --execute` may be possible, it is untested and not recommended.

```bash
cd external-metadata-awareness
poetry run jupyter notebook notebooks/environmental_context_value_sets/generate_voting_sheet.ipynb
```

**Required notebook edits before running:**

1. **Set configuration name**: Find the cell with `selected_configuration = "..."` and change it to your config name:
   ```python
   selected_configuration = "soil_env_medium"  # or your config
   ```

2. **Set DuckDB file path**: Find the cell that sets `ncbi_uncompressed_file_path` and update it:
   ```python
   ncbi_uncompressed_file_path = "../../local/ncbi_biosamples_2024-09-23.duckdb"
   ```
   Note: Path is relative to the notebook location in `notebooks/environmental_context_value_sets/`

3. **Run all cells**: Kernel → Restart & Run All, or run cells sequentially with Shift+Enter

**What the notebook does:**
1. Queries ENVO via OAK using configured semantic anchors
2. Extracts terms from DuckDB (NCBI), NMDC API, and GOLD based on empirical usage
3. Enriches with ontology metadata (obsolete status, hierarchy position)
4. Adds boolean classification columns (biome, env_mat, etc.)
5. Outputs TSV to `voting_sheets_output/[config]_voting_sheet.tsv`

### 2.4 Voting Sheet Output

Output files: `voting_sheets_output/[environment]_env_[slot]_voting_sheet.tsv`

The output contains ~28 columns. Key columns include:

| Column | Description |
|--------|-------------|
| `curie` | Ontology term CURIE (e.g., ENVO:00000428) |
| `label` | Human-readable term label |
| `envo_native` | Whether term is native to ENVO (vs. imported) |
| `obsolete` | Whether term is obsolete |
| `biome`, `terrestrial_biome`, `aquatic_biome` | Classification flags for env_broad_scale |
| `abp` | Astronomical body part flag for env_local_scale |
| `env_mat`, `soil`, `liquid water` | Classification flags for env_medium |
| `goldterms_mappings` | GOLD ontology mappings (non-empty = mapped) |
| `nmdc_biosamples_count` | Usage count in NMDC |
| `ncbi_bioprojects_count` | Usage count across NCBI BioProjects |
| `ancestors_in_enum_count` | Number of this term's ancestors already in the enum (helps identify redundant broad terms) |
| `descendants_in_enum_count` | Number of this term's descendants already in the enum (helps identify redundant specific terms) |
| `[EnumName]_[version]` | Comparison column (e.g., `EnvBroadScaleSoilEnum_11_1`) showing whether term was in previous schema version—useful for tracking additions/removals |

---

## Part 3: Expert Voting

### 3.1 Upload to Google Sheets

1. Create a new Google Sheet (or add tab to existing workbook)
2. File → Import → Upload the TSV file
3. Apply filters to reduce candidate terms (see below)
4. Add voting columns
5. Share with domain experts
6. **Share with service account** (required for later download):
   ```
   env-context-voting-sheets@env-context-voting-sheets.iam.gserviceaccount.com
   ```

### 3.2 Filter Voting Sheet Rows

Before voting, filter to remove irrelevant terms:

**Standard Filters (All Environments)**

| Column | Filter | Rationale |
|--------|--------|-----------|
| `obsolete` | `= False` | Never include deprecated terms |
| `envo_native` | `= True` | Prefer ENVO terms (exceptions: plant-associated may include PO/UBERON) |

**Slot-Specific Filters**

| Slot | Primary Filter | Additional Exclusions |
|------|----------------|----------------------|
| `env_broad_scale` | `biome = True` | Can narrow to `terrestrial_biome` or `aquatic_biome` |
| `env_local_scale` | `abp = True` (astronomical body part) | `biome = False`, `env_mat = False` |
| `env_medium` | `env_mat = True` (environmental material) | - |

**Prioritization Columns**

| Column | Meaning |
|--------|---------|
| `ncbi_bioprojects_count` | Number of NCBI BioProjects using this term |
| `nmdc_biosamples_count` | Number of NMDC biosamples using this term |
| `goldterms_mappings` | Non-empty = mapped in GOLD |

### 3.3 Voting Process

Add voting columns for each expert:

| Column | Values | Purpose |
|--------|--------|---------|
| `[INITIALS]_vote` | +1, 0, -1 | Include, neutral, exclude |
| `[INITIALS]_comment` | Text | Optional notes |

After voting, add aggregate column:

| Column | Calculation |
|--------|-------------|
| `vote_sum` | `=SUM(vote columns)` |

### 3.4 Inclusion Criteria

Terms are included if: `vote_sum >= 1`

### 3.5 Inter-Annotator Agreement (IAA)

**Current recommendation**: Skip IAA. Per CJM (Chris Mungall), just use `vote_sum >= 1` for filtering.

If IAA is needed (e.g., for analyzing voter agreement patterns), the formula is:

```
IAA = (number of agreeing voter pairs) / (total voter pairs)
```

Example with 5 voters (10 pairs = C(5,2)):
- All agree → 10/10 = **1.0**
- 4 agree, 1 differs → 6/10 = **0.6**
- Complete disagreement → **0.0**

**Single-voter scenarios**: IAA is meaningless with one voter. Just use the vote column directly as `vote_sum`.

> **Note**: An `iaa.py` script was planned but does not currently exist in this repo. If IAA calculation is needed, it would take vote columns from a downloaded CSV and compute pairwise agreement.

### 3.6 Google Sheets Voting Workbook Inventory

The canonical sheet IDs are those referenced in the [microbiomedata/submission-schema](https://github.com/microbiomedata/submission-schema) repository's `post_google_sheets_*.ipynb` notebooks. Many additional copies exist in Google Drive from earlier voting rounds — those are historical and not actively used.

#### Canonical Sheets (referenced in submission-schema notebooks)

| Environment | Slot | Sheet ID | Notes |
|-------------|------|----------|-------|
| plant_associated | env_broad_scale | `1MvXbYlBkJrgU02Ydh8UxlZjCbOQq3LjwpfaWjaRFKF0` | |
| plant_associated | env_local_scale | `1YvNu1DDQz56rjRHGf8jl8krHliGs1yleF5Ent5S0dIs` | |
| plant_associated | env_medium | `1gBgwdjSF7tBwZAa6HBxkmj2iAI0KFiQaTVV2y0yv-1A` | |
| water | env_broad_scale | `1lMjVxyADmZM1rZI7Qo99RnN6V5K8B8GjAevVoKENViw` | |
| water | env_local_scale | `1nD0ZaJooi6KAmRG4KiGbaCJ6Q6gEc93_dU35NXawcp0` | |
| water | env_medium | `1jMhQ6QK_50jK1MoJq8_raEfrW1FgYQJbB5r1D2SjFQ0` | |
| sediment | env_broad_scale | `1T0i2MkSBqY48dsjwVYwtI4nvy1RuEN864ouE-HwIe00` | |
| sediment | env_local_scale | `1t7ZMU-xc5813hXelA6xSwJdrVsoKHhBuGmcfZJ1mJUk` | |
| sediment | env_medium | `1jTSoWT4QxEPXGapkemj1EBJkUSGFs4OKvPhiglNz5gY` | |
| soil | env_local_scale | `1epul_bXtEOlmIZYNRhngulI3-HaHhe_tU_BPUia5isQ` | |
| soil | env_broad_scale | — | Procedural (ENVO query, no voting sheet) |
| soil | env_medium | — | Procedural (ENVO query, no voting sheet) |

To open any sheet: `https://docs.google.com/spreadsheets/d/{Sheet ID}`

#### Sheets Not Yet Referenced in Submission-Schema Notebooks

| Environment | Slot | Sheet ID | Notes |
|-------------|------|----------|-------|
| built | env_medium | `1gJXHl2_yGNKoGliYt8Af2K047d77MDFffEJTWtk0vr0` | Ready for voting |

#### Other Resources

| Name | ID |
|------|-----|
| Environmental context value set provenance | `1O7uNLG7GOJRiJ6rKUahObdyIGyUT-eO60q4h4oI-Sd4` |

All sheets must be shared with the service account: `env-context-voting-sheets@env-context-voting-sheets.iam.gserviceaccount.com`

---

## Part 4: Enum Injection (submission-schema)

After voting is complete in Google Sheets, switch to the **submission-schema** repository to process the results.

### 4.1 Process Voted Sheets

**Current state**: Processing is handled by one-off Jupyter notebooks in `notebooks/environmental_context_value_sets/[environment]/env_[slot]/`. Each notebook pulls from Google Sheets and generates a simplified TSV.

> **Note**: The existing notebooks use inconsistent approaches—some aggregate votes with `vote_sum >= 1`, others use simple boolean columns like `include_in_enum`, and soil env_medium/env_broad_scale use programmatic ancestry selection without voting. Future work should standardize this.

**To process a voted sheet:**

1. Open/create a notebook in the appropriate directory:
   ```
   notebooks/environmental_context_value_sets/[environment]/env_[slot]/
   ```

2. Pull data from the Google Sheet (requires service account credentials)

3. Filter to included terms based on voting results

4. Output a TSV with just `id` and `label` columns:
   ```
   post_google_sheets_[environment]_env_[slot].tsv
   ```

Required columns in the final TSV:

| Column | Description |
|--------|-------------|
| `id` | Term CURIE |
| `label` | Term label |

### 4.2 Update Enum Mappings (for new environments)

Edit `tools/enums.py`:

```python
ENUM_FILE_MAPPINGS = {
    "EnvBroadScaleSoilEnum": "soil/env_broad_scale/post_google_sheets_soil_env_broad_scale.tsv",
    # ... add new mappings
}
```

### 4.3 Generate and Inject Enumerations

```bash
make ingest-triad
```

### 4.4 Validate and Build

```bash
make lint
make test
make all
```

### 4.5 Create PR

```bash
git add .
git commit -m "Update environmental triad value sets for [environment]"
git push origin your-branch
gh pr create
```

---

## Adding a New Environment

1. **Configure**: Add to `voting_sheets_configurations.yaml`
2. **Generate**: Run voting sheet notebook
3. **Vote**: Create Google Sheets, conduct voting
4. **Process**: Place post-voting TSVs in submission-schema
5. **Map**: Add enum mappings to `tools/enums.py`
6. **Inject**: Run `make ingest-triad`
7. **Validate and PR**

---

## Updating Existing Value Sets

**Full voting cycle** (for significant changes):
- Regenerate voting sheet with latest DuckDB data
- Conduct new voting round
- Process and inject

**Incremental update** (for small corrections):
- Edit post-voting TSV directly
- Re-run enum injection
- Document rationale in commit

---

## Known Issues

### DuckDB Schema Mismatch

The `generate_voting_sheet.ipynb` notebook expects the **old DuckDB schema** with `attributes` and `links` tables. Newer "flat" schema files (e.g., `ncbi_metadata_flat_*.duckdb`) have different table names and will fail with:
```
Table with name ATTRIBUTES does not exist!
```

**Workaround**: Use the old schema file `ncbi_biosamples_2024-09-23.duckdb` from:
```
https://portal.nersc.gov/project/m3408/biosamples_duckdb/old/2024-09-23/
```

**Long-term fix**: Update notebook to use new schema (tracked as TODO).

### Empty double_curie_frame Error

For some environments (especially built environment), the notebook fails with:
```
Columns must be same length as key
```

This happens when `double_curie_frame` is empty (no disputed CURIEs in the data).

**Workaround**: Add guards in the notebook:

1. Find cell with `extracted_prefix`, replace with:
   ```python
   if len(double_curie_frame) > 0:
       double_curie_frame[['extracted_prefix', 'extracted_local_id']] = double_curie_frame['extracted_curie'].str.split(':', expand=True)
   else:
       double_curie_frame['extracted_prefix'] = pd.Series(dtype=str)
       double_curie_frame['extracted_local_id'] = pd.Series(dtype=str)
   ```

2. Before the `dragless_curie_list` cell, add:
   ```python
   ncbi_frame["drag_evidence"] = False
   ```

---

## Troubleshooting

### MongoDB Connection (Part 1 only)

MongoDB is only required if building the DuckDB from scratch (Option B in Part 1).

```bash
# Test connection
mongosh "mongodb://localhost:27017/ncbi_metadata" --eval "db.biosamples.countDocuments()"
```

### OAK Adapter Issues

```bash
# Test ENVO access
poetry run runoak -i sqlite:obo:envo info ENVO:00000428

# Clear cache if stale
rm -rf ~/.data/oaklib/
```

### DuckDB Verification

```bash
# Check table counts
duckdb local/ncbi_biosamples_2024-09-23.duckdb -c "SHOW TABLES;"
```

---

## File Reference

### external-metadata-awareness

| Path | Purpose |
|------|---------|
| `Makefiles/ncbi_metadata.Makefile` | NCBI XML download and MongoDB loading |
| `Makefiles/env_triads.Makefile` | MongoDB flattening and env triad processing |
| `Makefiles/ncbi_to_duckdb.Makefile` | MongoDB to DuckDB export |
| `voting_sheets_configurations.yaml` | Environment configuration |
| `notebooks/environmental_context_value_sets/generate_voting_sheet.ipynb` | Voting sheet generator |

### submission-schema

| Path | Purpose |
|------|---------|
| `notebooks/environmental_context_value_sets/[env]/[slot]/*.tsv` | Post-voting term lists |
| `tools/enums.py` | Enum file mappings |
| `src/nmdc_submission_schema/schema/nmdc_submission_schema.yaml` | Schema with enumerations |

---

## Related Documentation

- [ADR-0015: Environmental Triad Value Sets](https://github.com/microbiomedata/issues/blob/main/decisions/0015-env-triad-value-sets.md)
- [README-duckdb-biosamples-full.md](./README-duckdb-biosamples-full.md)
- [env-triad-curation](https://github.com/microbiomedata/env-triad-curation)

---

## Superseded Documentation

This document consolidates and replaces:
- `docs/ENV_TRIAD_WORKFLOW.md`
- `docs/nmdc-env-triad-valueset-lifecycle.md`
- `docs/nmdc-env-triad-complete-documentation.md`

**Note**: `docs/env-triad-data-pipeline.md` (technical reference for the MongoDB annotation pipeline) is a separate document with different scope—it covers the data processing that produces the source data for voting sheets.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-01-26 | Initial consolidated version |

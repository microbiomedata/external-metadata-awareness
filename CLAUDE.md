# External Metadata Awareness Commands and Guidelines

Quick reference for AI assistants working on this codebase.

---

## Quick Navigation
- 🚀 **New Contributors**: See [GETTING_STARTED.md](GETTING_STARTED.md)
- 🗺️ **Current Priorities**: See [PRIORITY_ROADMAP.md](PRIORITY_ROADMAP.md)
- 🏗️ **Architecture & Data**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- 💻 **Development Guide**: See [DEVELOPMENT.md](DEVELOPMENT.md)
- 🌍 **Environmental Triad Workflow**: See [ENV_TRIAD_WORKFLOW.md](ENV_TRIAD_WORKFLOW.md)
- 📋 **Active Work**: Tracking issues [#222](https://github.com/microbiomedata/external-metadata-awareness/issues/222) (Biosample Normalization) and [#223](https://github.com/microbiomedata/external-metadata-awareness/issues/223) (Infrastructure)

---

## Build & Run Commands

### Basic Commands
```bash
# Poetry scripts
poetry run python external_metadata_awareness/script_name.py
poetry run script-alias  # See pyproject.toml [tool.poetry.scripts]

# Makefiles
make -f Makefiles/target.Makefile target_name

# Notebooks
poetry run jupyter notebook
```

### Common CLI Aliases
```bash
# MongoDB connection testing
poetry run mongo-connect --uri mongodb://localhost:27017/ncbi_metadata --connect

# Normalize biosample data
poetry run normalize-satisfying-biosamples \
  --input-file local/satisfying_biosamples.csv \
  --output-file local/satisfying_biosamples_normalized.csv

# Run MongoDB JavaScript
poetry run mongo-js-executor \
  --mongo-uri mongodb://localhost:27017/ncbi_metadata \
  --js-file mongo-js/flatten_env_triads_multi_component.js

# Environmental triad processing
poetry run env-triad-values-splitter --input file.tsv --output out.tsv
poetry run env-triad-oak-annotator --collection env_triads_flattened
```

---

## Key Concepts

### Environmental Triads
Every biosample has three environmental context fields:
- **env_broad_scale**: Broad biome (e.g., "temperate grassland biome [ENVO:01000193]")
- **env_local_scale**: Local environment (e.g., "agricultural field [ENVO:00000114]")
- **env_medium**: Sample material (e.g., "soil [ENVO:00001998]")

These MUST be ontology terms (preferably from ENVO - Environmental Ontology).

### Harmonized Attributes
NCBI biosamples use different attribute names for the same concept:
- "temperature", "temp", "Temperature", "growth temperature" → harmonized to single canonical name
- Enables cross-dataset analysis and measurement discovery

### Measurement Discovery
Identifying which biosample attributes are measurements:
- Numeric values detected using quantulum3 parser
- Unit assertions validated
- UCUM (Unified Code for Units of Measure) mapping
- Skip list (224 harmonized_names) excludes non-measurement fields
- See: `measurement_discovery_efficient.py`

**Quick Commands**:
```bash
# Test the pipeline (1-2 minutes)
make -f Makefiles/measurement_discovery.Makefile test-measurement-discovery

# Focus on common measurements (2-3 hours)
make -f Makefiles/measurement_discovery.Makefile run-measurement-discovery-common

# Full production run (4-8 hours)
make -f Makefiles/measurement_discovery.Makefile run-measurement-discovery
```

**Performance Tips**:
- Use `--limit 50000` for quick validation (testing mode)
- Use `--min-count 10` to focus on common values (faster processing)
- Use `--save-aggregation` to save all 64M aggregation pairs (adds ~10-15 min)
- Script uses streaming + batching to avoid OOM on 64M+ pairs (Issue #262)

**Output Collections**:
- `content_pairs_aggregated`: All (harmonized_name, content, biosample_count) pairs
- `measurement_results_skip_filtered`: Parsed quantities with units

### CURIE Extraction
Converting text to ontology identifiers:
- **Asserted CURIEs**: Direct regex extraction (e.g., "ENVO:00001998")
- **NER CURIEs**: OAK text annotation (e.g., "soil" → ENVO:00001998)
- **BioPortal mapping**: Additional ontology term resolution

---

## Primary Workflows

### 1. Environmental Context Voting Sheets
Generate standardized environmental context value sets for submission-schema.

**Quick Start**:
1. Start Jupyter: `poetry run jupyter notebook`
2. Open: `notebooks/environmental_context_value_sets/generate_voting_sheet.ipynb`
3. Ensure DuckDB file exists: `ncbi_biosamples_*.duckdb`
4. Run all cells → generates TSV files in `voting_sheets_output/`

**Complete Workflow**: See **[ENV_TRIAD_WORKFLOW.md](ENV_TRIAD_WORKFLOW.md)** for the full end-to-end process across external-metadata-awareness, submission-schema, and envo repositories.

### 2. NCBI Biosample Processing
Download, parse, and analyze 44M+ NCBI biosamples.

**Main Makefile**: `Makefiles/ncbi_metadata.Makefile`

**Key Targets**:
```bash
# Download biosample XML (~3GB)
make -f Makefiles/ncbi_metadata.Makefile download_biosamples

# Load to MongoDB
make -f Makefiles/ncbi_metadata.Makefile load_biosamples

# Flatten attributes
make -f Makefiles/ncbi_metadata.Makefile flatten_biosample_attributes

# Full pipeline
make -f Makefiles/ncbi_metadata.Makefile duck-all
```

### 3. MongoDB → DuckDB Export
Export MongoDB collections to DuckDB for SQL analysis and sharing.

**Makefile**: `Makefiles/ncbi_to_duckdb.Makefile`

**Common Tasks**:
```bash
# Export all flat collections to DuckDB
make -f Makefiles/ncbi_to_duckdb.Makefile make-database

# Export satisfying biosamples to CSV
make -f Makefiles/ncbi_to_duckdb.Makefile export-satisfying-biosamples

# Normalize dates and coordinates
make -f Makefiles/ncbi_to_duckdb.Makefile normalize-satisfying-biosamples

# Show database summary
make -f Makefiles/ncbi_to_duckdb.Makefile show-summary
```

**Latest Exports**: https://portal.nersc.gov/project/m3408/biosamples_duckdb/

---

## Data Sources & Locations

### NCBI Data
- **BioSamples**: `ftp.ncbi.nlm.nih.gov/biosample/biosample_set.xml.gz` (~3GB, 44M samples)
- **BioProjects**: `ftp.ncbi.nlm.nih.gov/bioproject/bioproject.xml` (~3GB, 893K projects)
- **Packages**: `ncbi.nlm.nih.gov/biosample/docs/packages/?format=xml`

### BigQuery
- **SRA Metadata**: `nih-sra-datastore.sra.metadata` (35M+ records)
- Access via Google BigQuery client with application default credentials

### Other Sources
- **GOLD**: `gold.jgi.doe.gov/download?mode=site_excel`
- **Ontologies**: Via OAK (`sqlite:obo:envo`, `sqlite:obo:po`)
- **BioPortal**: `data.bioontology.org` (requires API key in .env)

---

## MongoDB Quick Reference

### Databases
- **ncbi_metadata**: Primary database (44M biosamples, 893K bioprojects, env triads)
- **gold_metadata**: GOLD data (217K biosamples, 221K projects)
- **nmdc**: NMDC data (9K biosamples, workflow executions)
- **biosamples**: SRA metadata (35M records)

### Key Collections
- `biosamples`: Raw NCBI BioSample XML
- `biosample_harmonized_attributes`: Flattened attributes
- `env_triads_flattened`: Environmental context values
- `sra_biosamples_bioprojects`: SRA↔Biosample↔BioProject relationships
- `bioprojects`, `bioprojects_submissions`: BioProject data

**See**: [ARCHITECTURE.md - MongoDB Infrastructure](ARCHITECTURE.md#mongodb-infrastructure) for complete collection list and stats.

### Connection Patterns
**Current** (inconsistent - see [Issue #176](https://github.com/microbiomedata/external-metadata-awareness/issues/176)):
- URI-style: `mongodb://localhost:27017/ncbi_metadata`
- Component-based: `--mongo-host localhost --mongo-port 27017`
- Utility: `mongodb_connection.py` (not consistently used)

**Target**: All scripts use `mongodb_connection.py` utility with URI-style connections.

---

## Important Gotchas

### MongoDB
- `make purge`: Drops ENTIRE `ncbi_metadata` database (dangerous!)
- Most scripts append data (don't clear collections first)
- Oversized documents (>16MB) saved to `local/oversize/`
- Indexes critical for performance on 44M+ document collections

### Dates & Coordinates
- Timezone info discarded during normalization (see [Issue #221](https://github.com/microbiomedata/external-metadata-awareness/issues/221))
- Year-only dates imputed to `YYYY-01-01`
- Coordinate formats vary wildly (DMS, decimal degrees, N/S/E/W)
- See: `normalize_satisfying_biosamples.py`

### Code Style
- **Don't use print()** - Use logging ([Issue #203](https://github.com/microbiomedata/external-metadata-awareness/issues/203))
- **Don't commit to main** - Use feature branches and PRs
- **Don't commit large files** - Use `local/` directory (gitignored)
- See: [DEVELOPMENT.md](DEVELOPMENT.md) for full style guide

---

## Repository Priorities (2025-10-02)

See [PRIORITY_ROADMAP.md](PRIORITY_ROADMAP.md) for comprehensive framework.

### Active Work
- 🎯 [#222](https://github.com/microbiomedata/external-metadata-awareness/issues/222): Complete biosample normalization (#216-221)
- 🏗️ [#223](https://github.com/microbiomedata/external-metadata-awareness/issues/223): Infrastructure improvements (#176, #203, #202)
- ⚡ Quick wins: Add progress bars ([#159](https://github.com/microbiomedata/external-metadata-awareness/issues/159)), update docs ([#204](https://github.com/microbiomedata/external-metadata-awareness/issues/204), [#42](https://github.com/microbiomedata/external-metadata-awareness/issues/42))

### Recently Closed (2025-10-02)
- ✅ #214-215: Biosample date/coordinate normalization tool
- ✅ #18, #40, #25: Stale issues closed with context

### Issue Health
- **43 open issues** (all have context as of 2025-10-02)
- **2 tracking issues** for coordination
- **6 priority categories** (Immediate, Infrastructure, Features, Research, Documentation, Stale)

---

## For More Detail

### Primary Documentation (Root Directory)
These are the authoritative, actively maintained docs:
- **[GETTING_STARTED.md](GETTING_STARTED.md)**: Quick start guide for new contributors
- **[ARCHITECTURE.md](ARCHITECTURE.md)**: Database systems, data flow, infrastructure patterns
- **[DEVELOPMENT.md](DEVELOPMENT.md)**: Code style, testing, git workflow, debugging
- **[PRIORITY_ROADMAP.md](PRIORITY_ROADMAP.md)**: Issue categorization and work priorities

### Workflow READMEs
- **Voting Sheets**: `notebooks/environmental_context_value_sets/voting-sheet-generation-readme.md`
- **Study Analysis**: Various READMEs in `notebooks/studies_exploration/`

### Historical Analysis & Session Notes
Additional context in `claude-mds/` (35+ files) and `unorganized/` directories:
- Session summaries and analysis reports
- Deep-dive investigations on specific topics
- May be outdated or superseded by docs above
- Useful for historical context, not day-to-day reference
- See [#224](https://github.com/microbiomedata/external-metadata-awareness/issues/224) for future consolidation

### Issue Tracking
- **Browse**: https://github.com/microbiomedata/external-metadata-awareness/issues
- **Tracking Issues**: [#222](https://github.com/microbiomedata/external-metadata-awareness/issues/222), [#223](https://github.com/microbiomedata/external-metadata-awareness/issues/223)
- **Documentation Cleanup**: [#224](https://github.com/microbiomedata/external-metadata-awareness/issues/224) (future session)

---

## Questions or Contributions?

Open an issue or submit a PR. All issues receive context and responses.

**Welcome to the external-metadata-awareness repository!**

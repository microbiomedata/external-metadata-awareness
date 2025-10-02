# Getting Started with External Metadata Awareness

Welcome! This repository analyzes and standardizes environmental metadata from NCBI BioSamples, GOLD, and NMDC for microbiome research.

---

## Quick Start

### 1. Prerequisites
- **Python**: 3.10 or higher
- **Poetry**: For dependency management
- **MongoDB**: localhost:27017 (or remote with credentials)
- **System**: macOS or Linux (tested on macOS)

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/microbiomedata/external-metadata-awareness.git
cd external-metadata-awareness

# Install dependencies with Poetry
poetry install

# Verify installation
poetry run python --version
```

### 3. Your First Command
```bash
# Test MongoDB connection
poetry run mongo-connect --uri mongodb://localhost:27017/ncbi_metadata --connect

# Or just see what the command would do
poetry run mongo-connect --uri mongodb://localhost:27017/ncbi_metadata --verbose
```

---

## What This Repository Does

### Primary Workflows

1. **Environmental Context Voting Sheets** 🗳️
   - Generate standardized environmental context value sets
   - Location: `notebooks/environmental_context_value_sets/`
   - See: [Voting Sheet README](notebooks/environmental_context_value_sets/voting-sheet-generation-readme.md)

2. **NCBI Biosample Processing** 🧬
   - Download and parse 45M+ NCBI biosamples
   - Extract environmental triads (env_broad_scale, env_local_scale, env_medium)
   - Normalize dates and coordinates
   - Location: Scripts in `external_metadata_awareness/`, Makefiles in `Makefiles/`

3. **MongoDB → DuckDB Pipeline** 🗄️
   - Export MongoDB collections to DuckDB for analysis
   - Latest exports at: https://portal.nersc.gov/project/m3408/biosamples_duckdb/
   - See: `Makefiles/ncbi_to_duckdb.Makefile`

4. **Measurement Discovery** 📊
   - Identify measurement attributes in biosamples
   - Map to UCUM units
   - Location: `external_metadata_awareness/measurement_discovery_efficient.py`

---

## Repository Structure

```
external-metadata-awareness/
├── external_metadata_awareness/    # Python scripts (54 files)
│   ├── normalize_satisfying_biosamples.py
│   ├── mongodb_connection.py       # MongoDB utilities
│   ├── measurement_discovery_efficient.py
│   └── ...
├── Makefiles/                      # Automation workflows
│   ├── ncbi_metadata.Makefile      # Main biosample processing
│   ├── ncbi_to_duckdb.Makefile     # MongoDB → DuckDB exports
│   ├── env_triads.Makefile         # Environmental triad processing
│   └── ...
├── notebooks/                      # Jupyter notebooks
│   ├── environmental_context_value_sets/  # Voting sheet generation
│   ├── studies_exploration/        # One-off analyses
│   └── mixs_preferred_unts/        # Unit mapping work
├── mongo-js/                       # MongoDB JavaScript scripts
├── local/                          # Generated data (gitignored)
├── CLAUDE.md                       # Comprehensive documentation
├── PRIORITY_ROADMAP.md             # Current priorities
└── pyproject.toml                  # Dependencies and CLI aliases
```

---

## Common Tasks

### Run Voting Sheet Generation
```bash
# Start Jupyter notebook
poetry run jupyter notebook

# Open: notebooks/environmental_context_value_sets/generate_voting_sheet.ipynb
# Run all cells
```

### Normalize Biosample Data
```bash
# Export satisfying biosamples from DuckDB
make -f Makefiles/ncbi_to_duckdb.Makefile export-satisfying-biosamples

# Normalize dates and coordinates
make -f Makefiles/ncbi_to_duckdb.Makefile normalize-satisfying-biosamples
```

### Run MongoDB JavaScript
```bash
# Execute a MongoDB JavaScript script
poetry run mongo-js-executor \
  --mongo-uri mongodb://localhost:27017/ncbi_metadata \
  --js-file mongo-js/flatten_env_triads_multi_component.js
```

### Check Available CLI Commands
```bash
# List all Poetry-registered commands
poetry run --help

# Common commands:
# - mongo-connect: Test MongoDB connections
# - mongo-js-executor: Run MongoDB JavaScript
# - normalize-satisfying-biosamples: Normalize biosample data
# - env-triad-values-splitter: Split env triad values
# - measurement-discovery-efficient: Find measurement attributes
```

---

## Understanding the Data Flow

### From XML to Analysis

```
1. Download
   └─> wget biosample_set.xml.gz from NCBI FTP

2. Load to MongoDB
   └─> xml-to-mongo → ncbi_metadata.biosamples collection

3. Flatten & Extract
   └─> mongo-js scripts → biosamples_attributes, env_triads_flattened

4. Export to DuckDB
   └─> mongodb-biosamples-to-duckdb → ncbi_biosamples.duckdb

5. Generate Voting Sheets
   └─> generate_voting_sheet.ipynb → TSV files for review

6. Integrate with submission-schema
   └─> Voted terms → LinkML enumerations
```

---

## Key Concepts

### Environmental Triads
Every biosample has three environmental context fields:
- **env_broad_scale**: Broad biome (e.g., "temperate grassland biome")
- **env_local_scale**: Local environment (e.g., "agricultural field")
- **env_medium**: Sample material (e.g., "soil")

These must be ontology terms (preferably from ENVO).

### Harmonized Attributes
NCBI biosamples use different attribute names for the same concept:
- "temperature", "temp", "Temperature", "growth temperature" → harmonized to single name
- Harmonization enables cross-dataset analysis

### Measurement Discovery
Not all biosample attributes are measurements. We identify which ones are by:
- Checking for numeric values
- Detecting unit assertions
- Validating against UCUM unit standards

---

## Current Priorities (2025-10-02)

See [PRIORITY_ROADMAP.md](PRIORITY_ROADMAP.md) for full details.

**Active Work**:
1. Complete biosample date/coordinate normalization ([#222](https://github.com/microbiomedata/external-metadata-awareness/issues/222))
2. Infrastructure improvements: MongoDB connections, logging, quality checks ([#223](https://github.com/microbiomedata/external-metadata-awareness/issues/223))

**Quick Wins** (good first contributions):
- [#159](https://github.com/microbiomedata/external-metadata-awareness/issues/159): Add tqdm progress bars to BioPortal mapper
- [#204](https://github.com/microbiomedata/external-metadata-awareness/issues/204): Document DuckDB + Parquet usage
- [#42](https://github.com/microbiomedata/external-metadata-awareness/issues/42): Update dependency documentation

---

## MongoDB Collections Reference

### Primary Database: `ncbi_metadata`

| Collection | Documents | Purpose |
|------------|-----------|---------|
| biosamples | 44M | Raw NCBI BioSample XML data |
| biosample_harmonized_attributes | 44M | Flattened attributes with harmonization |
| env_triads_flattened | ~200K | Environmental context values extracted |
| bioprojects | 893K | NCBI BioProject metadata |
| sra_biosamples_bioprojects | 29M | SRA → Biosample → BioProject relationships |

See [CLAUDE.md - MongoDB Infrastructure](CLAUDE.md#mongodb-infrastructure) for complete collection list.

---

## Getting Help

### Documentation
- **CLAUDE.md**: Comprehensive reference for commands, workflows, data sources
- **PRIORITY_ROADMAP.md**: Current priorities and issue categorization
- **Notebook READMEs**: Specific workflow documentation

### Issues
- Browse [open issues](https://github.com/microbiomedata/external-metadata-awareness/issues)
- All issues now have context (updated 2025-10-02)
- Check [tracking issues](https://github.com/microbiomedata/external-metadata-awareness/labels/tracking) for multi-issue themes

### Code Style
- Python ≥ 3.10 with type hints
- Google-style docstrings
- Click for CLI commands
- Snake case for variables/functions
- PascalCase for classes
- See [CLAUDE.md - Code Style Guidelines](CLAUDE.md#code-style-guidelines)

---

## What NOT to Do

❌ **Don't commit to main** - Use feature branches and PRs
❌ **Don't commit large files** - Files > 100MB go in `local/` (gitignored)
❌ **Don't commit credentials** - Use `.env` files (gitignored)
❌ **Don't use print()** - Use logging (see [#203](https://github.com/microbiomedata/external-metadata-awareness/issues/203))
❌ **Don't add dependencies** without updating `pyproject.toml` via Poetry

---

## Next Steps

### For New Contributors
1. ✅ Read this guide
2. ✅ Read [PRIORITY_ROADMAP.md](PRIORITY_ROADMAP.md)
3. ✅ Pick a "Quick Win" issue
4. ✅ Fork, branch, code, PR

### For Domain Experts
1. ✅ Review [voting sheet documentation](notebooks/environmental_context_value_sets/voting-sheet-generation-readme.md)
2. ✅ Participate in environmental context term voting (Google Sheets)
3. ✅ Provide feedback on term granularity (e.g., [#12](https://github.com/microbiomedata/external-metadata-awareness/issues/12), [#13](https://github.com/microbiomedata/external-metadata-awareness/issues/13))

### For Data Scientists
1. ✅ Download latest DuckDB: https://portal.nersc.gov/project/m3408/biosamples_duckdb/
2. ✅ Explore `notebooks/` for analysis examples
3. ✅ Check measurement discovery pipeline: `measurement_discovery_efficient.py`

---

## Questions?

Open an issue or contact the maintainers. All issues get responses and context.

**Welcome to the team! 🎉**

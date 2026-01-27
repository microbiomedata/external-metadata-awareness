# phenopacket-ingest

A Monarch Initiative ingest pipeline for phenopacket data from the [phenopacket-store](https://github.com/monarch-initiative/phenopacket-store). This pipeline downloads phenopacket data, extracts it, and transforms it into Biolink-compatible entities for inclusion in Monarch knowledge graphs.

## Overview

The phenopacket-ingest pipeline processes phenopacket data through several steps:

1. **Download**: Retrieves the latest phenopacket data from the phenopacket-store GitHub releases
2. **Extract**: Parses phenopacket data into a structured JSONL format
3. **Transform**: Converts the structured data into Biolink model entities for knowledge graph integration

## Data Sources

This ingest relies on phenopacket data from the [phenopacket-store](https://github.com/monarch-initiative/phenopacket-store) repository, which contains structured phenotypic data about rare disease cases in the GA4GH Phenopacket format.

### Source Files
- **phenopacket-store releases**: ZIP archive containing JSON phenopacket files organized by cohort
- Each phenopacket contains standardized data about an individual case including:
  - Subject information (ID, sex, age)
  - Phenotypic features (HPO terms)
  - Disease information (MONDO terms)
  - Genetic findings (variants and genes)
  - Interpretations (causality assessments)
  - Metadata (references, provenance)


## Requirements

- Python >= 3.10
- [Poetry](https://python-poetry.org/docs/#installation)
- [phenopackets library](https://github.com/phenopackets/phenopacket-schema) (optional, but recommended)
- [phenopacket-store-toolkit](https://github.com/monarch-initiative/phenopacket-store-toolkit) (optional, but recommended)

## Installation

```bash
cd phenopacket-ingest
make install
# or
poetry install
```

## Usage

### Full Pipeline

To run the complete pipeline (download, extract, transform) in one step:

```bash
poetry run phenopacket_ingest pipeline
```

### Individual Steps

For more granular control, you can run each step individually:

1. Download the data:
```bash
poetry run phenopacket_ingest download
```

2. Extract phenopacket data to JSONL format:
```bash
poetry run phenopacket_ingest extract
```

3. Transform the data to Biolink entities:
```bash
poetry run phenopacket_ingest transform
```

### Command Options

Each command has various options. To see them:

```bash
poetry run phenopacket_ingest [command] --help
```

For example:
```
poetry run phenopacket_ingest download --help
```

### Testing

The test suite covers:
- Model validation and conversion
- Transformation to Biolink entities
- Registry functionality (downloading and extraction)

Run the tests with:
```bash
make test
# or
python -m pytest
```

## Development

To contribute to this project:

1. Clone the repository
2. Install development dependencies:
   ```bash
   make install-dev
   # or
   poetry install --with dev
   ```
3. Run the tests:
   ```bash
   make test
   ```

---

> This project was generated using [monarch-initiative/cookiecutter-monarch-ingest](https://github.com/monarch-initiative/cookiecutter-monarch-ingest).
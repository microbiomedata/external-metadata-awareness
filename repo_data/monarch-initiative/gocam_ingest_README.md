# gocam_ingest

| [Documentation](https://monarch-initiative.github.io/gocam_ingest) |

A repository for transforming GOCAM models to Knowledge Graph nodes and edges.

## Requirements

- Python >= 3.10
- [Poetry](https://python-poetry.org/docs/#installation)

## Data Sources

GOCAM (Gene Ontology Causal Activity Models) data is available from the Gene Ontology Consortium through their live GO-CAM portal.

### Source Files
This ingest uses dynamic data retrieval from the GO-CAM API endpoints:
  - **Model List**: https://live-go-cam.geneontology.io/product/json/provider-to-model.json - Provides a comprehensive list of available GOCAM models with their internal IDs
  - **Model Details**: https://live-go-cam.geneontology.io/product/yaml/go-cam/[MODEL_INTERNAL_ID].yaml - Contains detailed YAML representation of each GOCAM model including molecular functions, biological processes, and causal relationships

### Nodes and Edges
The ingest transforms GOCAM models into Knowledge Graph format:
 - **Gene/Protein Nodes** - Molecular entities participating in biological processes with GO molecular function annotations
 - **Biological Process Nodes** - GO biological process terms represented in the models
 - **Molecular Function Nodes** - GO molecular function terms associated with gene products
 - **Causal Activity Edges** - Represents causal relationships between molecular activities and biological processes as defined in GOCAM models

## Installation

```bash
cd gocam_ingest
make install
# or
poetry install
```

> **Note** that the `make install` command is just a convenience wrapper around `poetry install`.

Once installed, you can check that everything is working as expected:

```bash
# Run the pytest suite
make test
# Download a few GOCAM models for testing
poetry run ingest download
poetry run ingest prepare --limit 5
# Run the Koza transform
poetry run ingest transform --row-limit 1
```

## Usage

This project uses a three-stage pipeline for processing GOCAM data:

### 1. Download GOCAM Models

The download process fetches GOCAM models from the Gene Ontology Consortium's live API:

```bash
poetry run ingest download
```

This command:
- Fetches the complete list of available models (~51,000 models) from the provider API
- Downloads each model's YAML file with a 1-second delay between requests for rate limiting
- Saves files to `data/gocam_models/` directory
- Handles 404 errors gracefully for non-existent models
- Skips already downloaded files, making the process resumable

**Note:** The complete download takes several hours due to the large number of models and rate limiting. The process can be interrupted and resumed safely.

### 2. Prepare JSON Data

Convert YAML GOCAM models to JSON format for Koza processing:

```bash
# Convert a few files for testing
poetry run ingest prepare --limit 5

# Convert all downloaded files
poetry run ingest prepare
```

This command:
- Converts YAML files from `data/gocam_models/` to JSON format
- Saves converted files to `data/gocam_models_converted_json/`
- Automatically updates the transform configuration with the file list
- Skips already converted files

### 3. Transform to Knowledge Graph

Run the Koza transform to generate nodes and edges:

```bash
# Process one file for testing
poetry run ingest transform --row-limit 1

# Process all prepared files
poetry run ingest transform
```

This command:
- Processes JSON GOCAM models using Koza framework
- Creates biolink-compliant nodes (genes, activities, molecular functions)
- Generates associations (enabled_by, has_molecular_function relationships)
- Outputs TSV files in `output/` directory

### Available Options

To see available options for any command:

```bash
poetry run ingest download --help
poetry run ingest prepare --help
poetry run ingest transform --help
```

### Testing

To run the test suite:

```bash
make test
```

To see all available make targets:

```bash
make help
```

## Transform Code and Configuration

- **Metadata**: `src/gocam_ingest/metadata.yaml` - Project metadata and descriptions
- **Transform Logic**: `src/gocam_ingest/transform.py` - Python code for processing GOCAM data
- **Transform Config**: `src/gocam_ingest/transform.yaml` - Koza configuration file
- **Dependencies**: `pyproject.toml` - Python dependencies and project configuration

For more information, see the [Koza documentation](https://koza.monarchinitiative.org).

---

> This project was generated using [monarch-initiative/cookiecutter-monarch-ingest](https://github.com/monarch-initiative/cookiecutter-monarch-ingest).
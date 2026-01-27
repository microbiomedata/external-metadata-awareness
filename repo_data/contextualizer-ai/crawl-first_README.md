# crawl-first

**Deterministic biosample enrichment for LLM-ready data preparation**

## Overview

`crawl-first` systematically follows discoverable links from NMDC biosample records to gather environmental, geospatial, weather, publication, and ontological data. This deterministic approach enables comprehensive data enrichment before downstream LLM analysis.

## Philosophy

Instead of letting LLMs make API calls or guess at missing data, `crawl-first` embodies the principle: **gather first, analyze second**. This ensures reproducible, comprehensive datasets for AI analysis.

## Features

- **Biosample enrichment**: Follows discoverable linked data sources
- **Geospatial analysis**: Coordinates, elevation, land cover, soil types
- **Weather integration**: Historical weather data for sample collection dates  
- **Publication tracking**: DOI resolution, full-text retrieval when available
- **Ontology enrichment**: ENVO term matching for environmental descriptors
- **Quality validation**: Distance/elevation comparisons between data sources
- **Interactive maps**: Generated URLs for coordinate validation
- **Comprehensive caching**: Prevents redundant API calls

## System Requirements

The following system utilities are required for development and testing:

- `curl` - API requests and data fetching
- `jq` - JSON processing in Makefile targets
- `shuf` - Random sampling of biosample IDs
- `head` - Data sampling utilities
- Standard Unix utilities: `mkdir`, `rm`, `find`, `wc`

On macOS, these are typically pre-installed. On Ubuntu/Debian:
```bash
sudo apt update && sudo apt install curl jq coreutils
```

## Installation

```bash
uv add crawl-first
```

## Usage

### Single biosample
```bash
uv run crawl-first --biosample-id nmdc:bsm-11-abc123 --email your-email@domain.com --output-file result.yaml
```

### Multiple biosamples
```bash
uv run crawl-first --input-file biosample_ids.txt --email your-email@domain.com --output-dir results/
```

### Sample from large dataset
```bash
uv run crawl-first --input-file all_biosamples.txt --sample-size 50 --email your-email@domain.com --output-dir sample_results/
```

## Output Structure

Each enriched biosample contains:
- **Asserted data**: Original NMDC biosample record
- **Inferred data**: Discovered linked information
  - Soil analysis with ENVO ontology terms
  - Land cover classification across multiple systems
  - Weather data from collection date
  - Publication metadata and full-text when available
  - Geospatial features within configurable radius
  - Coordinate validation and distance calculations

## Data Sources

- **NMDC API**: Biosample and study metadata
- **Land Use MCP**: Land cover classification systems
- **Weather MCP**: Historical meteorological data
- **OLS MCP**: Ontology term resolution
- **ARTL MCP**: Publication and full-text retrieval
- **OpenStreetMap**: Environmental feature mapping
- **Elevation APIs**: Topographic data validation

## Development

```bash
git clone https://github.com/contextualizer-ai/crawl-first.git
cd crawl-first

# Install dependencies
uv sync --dev

# Run quality checks and tests
make all

# Or run individual commands:
uv run pytest
uv run black .
uv run ruff check .
uv run mypy .
uv run deptry .
```

**Note**: Full development workflow including data fetching and testing requires the system dependencies listed above.

### MCP Configuration for Claude Integration

The repository includes Makefile targets that integrate with Claude Code for testing and automation. These targets require a properly configured `.mcp.json` file in your Claude configuration directory.

**Note**: Makefile targets like `claude-weather-test.txt` and `random-ids-test.txt` will not work without proper MCP server configuration in Claude.

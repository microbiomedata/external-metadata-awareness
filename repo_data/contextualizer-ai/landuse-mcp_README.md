# landuse-mcp

A Model Context Protocol (MCP) server for retrieving land use data for given geographical locations using the National Land Cover Database (NLCD) and other geospatial datasets.

## Features

- **Land Cover Data**: Retrieve detailed land cover classifications for any coordinate
- **Soil Type Information**: Get FAO soil type classifications for geographical points
- **Temporal Data**: Access available dates for land use data at specific locations
- **MCP Integration**: Full Model Context Protocol support for AI agents
- **Geospatial Processing**: Built on robust geospatial libraries for accurate data retrieval

## Quick Start

```bash
# Install dependencies and set up development environment
make dev

# Run the MCP server
make server

# Run tests
make test-coverage

# Demo functionality
make demo
```

## Installation

### From PyPI (Recommended)

```bash
# Install with uvx
uvx landuse-mcp
```

### From Source

```bash
# Clone the repository
git clone https://github.com/justaddcoffee/landuse-mcp.git
cd landuse-mcp

# Install in development mode
make dev
```

## Usage

### Command Line Interface

```bash
# Run the MCP server
landuse-mcp

# Or using uv
uv run landuse-mcp
```

### Python API

```python
from landuse_mcp.main import get_land_cover, get_soil_type, get_landuse_dates

# Get land cover data for Death Valley
land_cover = get_land_cover(36.5322649, -116.9325408, "2001-01-01", "2002-01-01")
print(land_cover)

# Get soil type for a location
soil_type = get_soil_type(32.95047, -87.393259)
print(soil_type)  # e.g., "Cambisols"

# Get available dates for land use data
dates = get_landuse_dates(36.5322649, -116.9325408)
print(dates)  # List of available dates
```

### Testing MCP Protocol

```bash
# Test MCP handshake
make test-mcp

# Extended MCP testing
make test-mcp-extended
```

## Integration with AI Tools

### Claude Desktop

Add this to your Claude Desktop configuration file (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "landuse-mcp": {
      "command": "uvx",
      "args": ["landuse-mcp"],
      "cwd": "/path/to/landuse-mcp"
    }
  }
}
```

### Claude Code

```bash
claude mcp add -s project landuse-mcp uvx landuse-mcp
```

### Goose

```bash
goose session --with-extension "uvx landuse-mcp"
```

## Available Tools

The MCP server provides three main tools:

1. **`get_land_cover`**: Retrieve land cover data for coordinates with temporal range
2. **`get_soil_type`**: Get FAO soil classification for a location
3. **`get_landuse_dates`**: List available dates for land use data at coordinates

## Data Sources

- **National Land Cover Database (NLCD)**: Primary source for US land cover data
- **FAO Soil Types**: Global soil classification system
- **nmdc-geoloc-tools**: Underlying geospatial processing library

## Development

### Development Setup

```bash
# Full development setup
make dev

# Install production dependencies only
make install

# Run tests with coverage
make test-coverage

# Code quality checks
make format lint mypy

# Check for unused dependencies
make deptry

# Clean build artifacts
make clean
```

### Build and Release

```bash
# Build package
make build

# Upload to TestPyPI
make upload-test

# Upload to PyPI
make upload

# Complete release workflow
make release
```

### Testing

```bash
# Run all tests
make test-coverage

# Run integration tests
make test-integration

# Test MCP protocol
make test-mcp test-mcp-extended
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `make test-coverage`
5. Run quality checks: `make format lint mypy`
6. Submit a pull request

## Requirements

- Python 3.10+
- uv (recommended)
- Dependencies managed via `pyproject.toml`

## License

MIT License - see LICENSE file for details.

## Authors

- Mark Miller
- Justin Reese  
- Charles Parker

## Citation

If you use this software in your research, please cite it as:

```bibtex
@software{landuse_mcp,
  title = {landuse-mcp: A Model Context Protocol server for land use data},
  author = {Miller, Mark and Reese, Justin and Parker, Charles},
  url = {https://github.com/justaddcoffee/landuse-mcp},
  version = {0.1.0},
  year = {2024}
}
```
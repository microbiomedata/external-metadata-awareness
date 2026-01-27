# landuse_mcp

An MCP for retrieving land use data for a given location

## Installation

You can install the package from source:

# to install rasterio 

```bash
# Install GDAL, the Geospatial Data Abstraction Library, for dealing with GeoTIFF files

# code below only works for MacOS - if you are on Linux, please refer to the rasterio
# documentation 
# for linux, try apt-get install gdal or something similar
# for Windows, not sure
# docs are [here](https://rasterio.readthedocs.io/en/stable/#)
brew install gdal
export CPLUS_INCLUDE_PATH=$(brew --prefix gdal)/include
export C_INCLUDE_PATH=$(brew --prefix gdal)/include
export GDAL_CONFIG=$(brew --prefix gdal)/bin/gdal-config
uv add rasterio
```

```bash
pip install -e .
```

Or using uv:

```bash
uv pip install -e .
```

## Usage

You can use the CLI:

```bash
landuse_mcp 
```

Or import in your Python code:

```python
from landuse_mcp.main import create_mcp

mcp = create_mcp()
mcp.run()
```

## Development

### Local Setup

```bash
# Clone the repository
git clone https://github.com/justaddcoffee/landuse-mcp.git
cd landuse-mcp

# Install development dependencies
uv pip install -e ".[dev]"
```


## License

BSD-3-Clause

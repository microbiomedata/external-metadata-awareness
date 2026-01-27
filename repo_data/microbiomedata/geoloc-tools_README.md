# GeoEngine geolocation tool
Library to request information about a location regarding the elevation, soil type, and landuse from web services host at Oak Ridge National Laboratory.

See https://modis.ornl.gov/rst/ui/#!/products/get_products for more information

## Development

### Prerequisites

- [Poetry](https://python-poetry.org/docs/#installation)
- [Poetry dynamic versioning plugin](https://github.com/mtkennerly/poetry-dynamic-versioning?tab=readme-ov-file#installation)

### Setup

Install dependencies with Poetry. This will also create a new virtual environment if necessary.

```bash
poetry install
```

### Testing

Run the test suite using the Makefile target `test`.

```bash
make test
```

### Linting

Run the linter using the Makefile target `lint`.

```bash
make lint
```

Some issues can be automatically fixed by running the Makefile target `lint-fix`.

```bash
make lint-fix
```

### Releasing

To release a new version to PyPI, create a new GitHub Release with a tag in the format `vX.Y.Z`. This will trigger a GitHub Action that will publish the new version to PyPI.

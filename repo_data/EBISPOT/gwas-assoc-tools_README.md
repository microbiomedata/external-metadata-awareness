# GWAS Association Tools

A command-line tool for genomic-wide association studies (GWAS) data validation and analysis.

## Features

- Validate:
  - Input: File path of GWAS Submission template that contains top associations
  - Output: Validation report of top associations

## Installation

Install from [PyPI](https://pypi.org/project/gwas-assoc-tools/):

```bash
pip install gwas-assoc-tools
```

## Usage

```bash
# Basic validation command
gwas-assoc validate <template excel file path>

# For help
gwas-assoc --help
gwas-assoc validate --help
```

## Development

### Setup

```bash
# Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

### Building and Installation

```bash
# Build the package (creates .whl and .tar.gz in dist/)
poetry build

# Install your new package in development mode
poetry install
```

### Testing

TODO

### Running with Real Files

```bash
# Run the CLI command through Poetry
# For failed test file
poetry run gwas-assoc validate ./tests/test_fail.xlsx   
# For successful test file
poetry run gwas-assoc validate ./tests/test_success.xlsx   


# Or after activating the shell
poetry shell
# For failed test file
gwas-assoc validate ./tests/test_fail.xlsx   
# For successful test file
gwas-assoc validate ./tests/test_success.xlsx   

```

### Dependency Management

```bash
# Add a new dependency
poetry add new-package

# Add a development dependency
poetry add --group dev pytest-mock

# Check for dependency updates
poetry update --dry-run

# Update dependencies
poetry update
```

### Code Quality

```bash
# Run formatting
poetry run black .
poetry run isort .

# Run linting
poetry run ruff check .

# Run type checking
poetry run mypy src

# Run all formatting checks
poetry run pre-commit run --all-files
```

## Documentation
Please find the Confluence page here: https://embl.atlassian.net/wiki/spaces/GOCI/pages/57606184/GWAS+Associations+Tools

## License

[License](LICENSE)

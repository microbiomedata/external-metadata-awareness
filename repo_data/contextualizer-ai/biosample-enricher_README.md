# Biosample Enricher

Infer AI-friendly metadata about biosamples from multiple sources.

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/type--checked-mypy-blue.svg)](https://mypy-lang.org/)

## Overview

Biosample Enricher is a Python package and CLI tool designed to gather and enrich metadata about biological samples from multiple data sources. It provides a unified interface for querying various biological databases and returns structured, AI-friendly metadata that can be used for downstream analysis, machine learning, or data integration tasks.

## Features

- **Multi-source data integration**: Query multiple biological databases simultaneously
- **Click-based CLI**: User-friendly command-line interface with options (not arguments)
- **Structured output**: Returns pydantic models with type validation
- **Multiple output formats**: Support for table, JSON, and CSV output formats
- **Batch processing**: Process multiple samples from input files
- **Extensible architecture**: Easy to add new data sources
- **Type safety**: Full type hints with mypy validation
- **Rich console output**: Beautiful console output with progress indicators

## Installation

### Prerequisites

- Python 3.11 or higher
- [UV package manager](https://github.com/astral-sh/uv) (recommended)

### Using UV (Recommended)

```bash
# Install from source
git clone https://github.com/contextualizer-ai/biosample-enricher.git
cd biosample-enricher
uv sync
```

### Using pip

```bash
# Install from source
git clone https://github.com/contextualizer-ai/biosample-enricher.git
cd biosample-enricher
pip install -e .
```

## Quick Start

### CLI Usage

#### Basic enrichment of a single sample

```bash
# Using UV
uv run biosample-enricher enrich --sample-id SAMN123456

# Or if installed globally
biosample-enricher enrich --sample-id SAMN123456
```

#### Specify data sources

```bash
biosample-enricher enrich --sample-id SAMN123456 --sources ncbi --sources ebi
```

#### Different output formats

```bash
# Table format (default)
biosample-enricher enrich --sample-id SAMN123456 --output-format table

# JSON format
biosample-enricher enrich --sample-id SAMN123456 --output-format json

# CSV format
biosample-enricher enrich --sample-id SAMN123456 --output-format csv
```

#### Batch processing

```bash
# Create a file with sample IDs (one per line)
echo -e "SAMN123456\\nSAMN789012\\nSAMN345678" > samples.txt

# Process all samples
biosample-enricher batch --input-file samples.txt --output-format json

# Save results to file
biosample-enricher batch --input-file samples.txt --output-file results.json
```

#### Validate sample IDs

```bash
biosample-enricher validate --sample-id SAMN123456
```

### Python API Usage

```python
from biosample_enricher import BiosampleEnricher

# Create enricher instance
with BiosampleEnricher(timeout=30.0) as enricher:
    # Enrich a single sample
    results = enricher.enrich_sample("SAMN123456")

    for result in results:
        print(f"Source: {result.source}")
        print(f"Confidence: {result.confidence}")
        print(f"Metadata: {result.metadata}")

    # Enrich multiple samples
    batch_results = enricher.enrich_multiple(
        ["SAMN123456", "SAMN789012"],
        sources=["ncbi", "ebi"]
    )

    for sample_id, metadata_list in batch_results.items():
        print(f"Sample {sample_id}: {len(metadata_list)} sources")
```

## Development

### Development Setup

```bash
# Clone the repository
git clone https://github.com/contextualizer-ai/biosample-enricher.git
cd biosample-enricher

# Complete development setup (installs deps, pre-commit hooks, etc.)
make dev-setup
```

### Available Make Commands

```bash
# Show all available commands
make help

# Development workflow
make dev-check          # Run formatting, linting, type-checking, and tests
make test               # Run tests
make test-cov           # Run tests with coverage
make lint               # Run linting
make format             # Format code
make type-check         # Run type checking

# Package management
make install            # Install in production mode
make install-dev        # Install with development dependencies
make build              # Build the package
make clean              # Clean build artifacts

# Examples
make run                # Show CLI help
make enrich-example     # Run example enrichment
make validate-example   # Run example validation
```

### Code Quality

This project maintains high code quality standards:

- **Linting**: [Ruff](https://github.com/astral-sh/ruff) for fast Python linting
- **Formatting**: Ruff formatter for consistent code style
- **Type Checking**: [MyPy](https://mypy-lang.org/) for static type checking
- **Testing**: [Pytest](https://pytest.org/) with coverage reporting
- **Pre-commit hooks**: Automated code quality checks

### Testing

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Run tests in watch mode (requires pytest-watch)
make test-watch
```

### Project Structure

```
biosample-enricher/
├── biosample_enricher/          # Main package
│   ├── __init__.py             # Package initialization
│   ├── core.py                 # Core enrichment logic
│   └── cli.py                  # Command-line interface
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── test_core.py           # Core functionality tests
│   └── test_cli.py            # CLI tests
├── pyproject.toml             # Project configuration
├── Makefile                   # Development automation
├── README.md                  # This file
└── LICENSE                    # MIT license
```

## Configuration

### Data Sources

Currently supported data sources:
- **NCBI**: National Center for Biotechnology Information
- **EBI**: European Bioinformatics Institute
- **BioSample DB**: Generic biosample database

### Output Schema

The enricher returns `BiosampleMetadata` objects with the following structure:

```python
class BiosampleMetadata(BaseModel):
    sample_id: str                    # Unique identifier for the biosample
    source: str                       # Data source name
    metadata: Dict[str, Any]          # Enriched metadata dictionary
    confidence: float                 # Confidence score (0.0-1.0)
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run the development checks (`make dev-check`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines (enforced by Ruff)
- Add type hints for all functions and methods
- Write comprehensive tests for new features
- Update documentation as needed
- Ensure all CI checks pass

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Roadmap

### Upcoming Features

- [ ] Additional data source integrations
- [ ] Caching mechanism for improved performance
- [ ] Parallel processing for batch operations
- [ ] Configuration file support
- [ ] Docker containerization
- [ ] Web API interface
- [ ] Integration with popular bioinformatics workflows

### Known Limitations

- Currently uses mock data for demonstration purposes
- Parallel processing not yet implemented
- Limited to basic metadata fields

## Support

- **Issues**: [GitHub Issues](https://github.com/contextualizer-ai/biosample-enricher/issues)
- **Discussions**: [GitHub Discussions](https://github.com/contextualizer-ai/biosample-enricher/discussions)
- **Email**: info@contextualizer.ai

## Acknowledgments

- Built with [UV](https://github.com/astral-sh/uv) for fast Python package management
- CLI powered by [Click](https://click.palletsprojects.com/)
- Console output enhanced with [Rich](https://github.com/Textualize/rich)
- Data validation with [Pydantic](https://pydantic.dev/)

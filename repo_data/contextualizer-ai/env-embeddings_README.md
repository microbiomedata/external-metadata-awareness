
# env-embeddings

Simple experiment to compare ENVO similarity to google embedding cosine similarity 

## Quick Start

### Prerequisites
- Python 3.10+
- `uv` package manager
- Google Cloud account with billing enabled

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd env-embeddings

# Install dependencies
uv sync
```

### Google Earth Engine Setup

This project uses Google Earth Engine to retrieve 64-dimensional satellite embeddings. Follow these steps for initial setup:

#### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "NEW PROJECT"
3. Name: `Environment Embeddings Project`
4. Project ID: `env-embeddings-2025` (or similar)
5. Click "CREATE"

#### 2. Enable APIs and Register Project

```bash
# Set your project as active
gcloud config set project env-embeddings-2025

# Enable required APIs
gcloud services enable earthengine.googleapis.com cloudresourcemanager.googleapis.com serviceusage.googleapis.com --project=env-embeddings-2025
```

#### 3. Register for Earth Engine Access

1. Visit: https://console.cloud.google.com/earth-engine?project=env-embeddings-2025
2. Choose "noncommercial" use
3. Complete the registration workflow
4. Wait for approval (usually a few minutes)

#### 4. Set Up Authentication

```bash
# Authenticate with Google Cloud
gcloud auth application-default login

# Grant necessary permissions to your team (replace with actual emails)
gcloud projects add-iam-policy-binding env-embeddings-2025 --member="user:YOUR_EMAIL@lbl.gov" --role="roles/editor"
gcloud projects add-iam-policy-binding env-embeddings-2025 --member="user:YOUR_EMAIL@lbl.gov" --role="roles/serviceusage.serviceUsageConsumer"
```

### Usage

#### Initialize Earth Engine (once per session)

```bash
uv run env-embeddings init-ee --project env-embeddings-2025
```

#### Get Satellite Embeddings

```bash
# Get embedding for specific coordinates and year
uv run env-embeddings embedding --lat 39.0372 --lon -121.8036 --year 2024

# With project parameter (if not initialized)
uv run env-embeddings embedding --lat 39.0372 --lon -121.8036 --year 2024 --project env-embeddings-2025
```

This returns a 64-dimensional vector representing environmental/satellite features from Google's Earth Engine satellite data.

#### Process Sample Data

```bash
# Add Google Earth Engine embeddings to your TSV file
# (Files in data/ directory can be referenced by filename only)
uv run env-embeddings add-embeddings date_and_latlon_samples_extended.tsv

# Process just a subset for testing
uv run env-embeddings add-embeddings date_and_latlon_samples_extended.tsv --max-rows 100

# Specify custom output location
uv run env-embeddings add-embeddings data/my_samples.tsv --output data/my_results.tsv

# Use different fallback year when original year has no satellite data
uv run env-embeddings add-embeddings date_and_latlon_samples_extended.tsv --fallback-year 2021
```

This command:
- Reads your TSV file with sample coordinates and dates
- Parses coordinates from `lat_lon` column (e.g., "50.936 N 6.952 E") 
- Parses years from `date` column (handles "2008-08-20", "2016", etc.)
- Retrieves 64-dimensional satellite embeddings from Google Earth Engine
- Adds a new `google_earth_embeddings` column to your data
- Uses fallback year (default 2020) when original year has no satellite coverage

#### CLI Help

```bash
# View all commands
uv run env-embeddings --help

# Get help for specific commands
uv run env-embeddings init-ee --help
uv run env-embeddings embedding --help
```

## Documentation Website

[https://contextualizerai.github.io/env-embeddings](https://contextualizerai.github.io/env-embeddings)

## Development

### Testing

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_earth_engine.py

# Run tests with verbose output
uv run pytest -v
```

### Project Structure

```
env-embeddings/
├── src/env_embeddings/
│   ├── cli.py                # CLI interface with Typer
│   ├── earth_engine.py       # Earth Engine integration
│   ├── sample_processor.py   # Sample data processing utilities
│   └── __init__.py
├── tests/
│   ├── test_earth_engine.py  # Earth Engine functionality tests
│   └── test_simple.py        # Basic tests
├── data/                     # Data files directory
│   └── date_and_latlon_samples_extended.tsv  # Sample dataset
├── docs/                     # MkDocs documentation
└── pyproject.toml           # Project configuration
```

### Dependencies

Key dependencies:
- `typer` - CLI framework
- `earthengine-api` - Google Earth Engine Python API
- `linkml-runtime` - Data modeling
- `pytest` - Testing framework

## Repository Structure

* [docs/](docs/) - mkdocs-managed documentation
* [project/](project/) - project files (these files are auto-generated, do not edit)
* [src/](src/) - source files (edit these)
  * [env_embeddings](src/env_embeddings)
* [tests/](tests/) - Python tests
  * [data/](tests/data) - Example data

## Developer Tools

There are several pre-defined command-recipes available.
They are written for the command runner [just](https://github.com/casey/just/). To list all pre-defined commands, run `just` or `just --list`.

MacOS users can do a one-time installation of `just` with `uv tool install rust-just`

See also: https://github.com/casey/just

## Credits

This project uses the template [monarch-project-copier](https://github.com/monarch-initiative/monarch-project-copier)

# ingest-metadata

Schema hosting relevant metadata for a data transformation conformant to the Biolink Model

## Website

[https://biolink.github.io/ingest-metadata](https://biolink.github.io/ingest-metadata)

## Repository Structure

* [examples/](./examples) - example data
* [project/](./project) - project files (do not edit these)
* [src/](./src) - source files (edit these)
  * [ingest_metadata](src/ingest_metadata)
    * [schema](src/ingest_metadata/schema) -- LinkML schema
      (edit this)
    * [datamodel](src/ingest_metadata/datamodel) -- generated
      Python datamodel
* [tests/](./tests) - Python tests

## Developer Documentation

### Prerequisites

This project uses [uv](https://docs.astral.sh/uv/) for dependency management. Install uv first:

```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Alternative: using pip
pip install uv
```

### Getting Started

1. Clone the repository:
```bash
git clone https://github.com/biolink/ingest-metadata.git
cd ingest-metadata
```

2. Install dependencies:
```bash
uv sync
```

3. Run tests:
```bash
make test  # or use the  `just test` command
```

### Development Commands

To run the commands, you may use good old make or the command runner [just](https://github.com/casey/just/) which is a better choice on Windows.
Use the `make` command or `duty` commands to generate project artifacts:
* `make help` or `just --list`: list all pre-defined tasks
* `make all` or `just all`: make everything
* `make deploy` or `just deploy`: deploys site
* `make install`: install dependencies with uv
* `uv sync`: install dependencies directly with uv
* `make test`: run tests

## Credits

This project was made with
[linkml-project-cookiecutter](https://github.com/linkml/linkml-project-cookiecutter).

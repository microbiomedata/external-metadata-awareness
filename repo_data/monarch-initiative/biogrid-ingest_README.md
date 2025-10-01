# biogrid-ingest

| [Documentation](https://monarch-initiative.github.io/biogrid-ingest) |

BioGRID ingest.

## Requirements

- Python >= 3.10
- [Poetry](https://python-poetry.org/docs/#installation)


## Installation

```bash
cd biogrid-ingest
make install
# or
poetry install
```

> **Note** that the `make install` command is just a convenience wrapper around `poetry install`.

Once installed, you can check that everything is working as expected:

```bash
# Run the pytest suite
make test
# Download the data and run the Koza transform
make download
make run
```

## Usage

This project is set up with a Makefile for common tasks.  
To see available options:

```bash
make help
```

### Download and Transform

Download the data for the biogrid_ingest transform:

```bash
poetry run biogrid_ingest download
```

To run the Koza transform for biogrid-ingest:

```bash
poetry run biogrid_ingest transform
```

To see available options:

```bash
poetry run biogrid_ingest download --help
# or
poetry run biogrid_ingest transform --help
```

### Testing

To run the test suite:

```bash
make test
```

---

> This project was generated using [monarch-initiative/cookiecutter-monarch-ingest](https://github.com/monarch-initiative/cookiecutter-monarch-ingest).  
> Keep this project up to date using cruft by occasionally running in the project directory:
>
> ```bash
> cruft update
> ```
>
> For more information, see the [cruft documentation](https://cruft.github.io/cruft/#updating-a-project)

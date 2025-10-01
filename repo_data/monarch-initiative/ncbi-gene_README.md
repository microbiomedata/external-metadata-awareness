# NCBI Gene

| [Documentation](https://monarch-initiative.github.io/ncbi-gene) |

The NCBI Gene integrates information from a wide range of species. A record may include nomenclature, Reference Sequences (RefSeqs), maps, pathways, variations, phenotypes, and links to genome-, phenotype-, and locus-specific resources worldwide.

### Data Sources

- [NCBI bulk downloads](https://www.ncbi.nlm.nih.gov/gene/)

### Gene Information

Genes for all NCBI species (Dog, Cow, Pig, Chicken, et alia) are loaded using the ingest file (filtered to only NCBI taxon ID).

#### Biolink Captured

- biolink:Gene
  - id
  - symbol
  - description
  - in_taxon
  - in_taxon_label
  - provided_by (["infores:ncbi-gene"])

### Citation

National Center for Biotechnology Information (NCBI)[Internet]. Bethesda (MD): National Library of Medicine (US), National Center for Biotechnology Information; [1988] – [cited 2024 Dec]. Available from: https://www.ncbi.nlm.nih.gov/

## Requirements

- Python >= 3.10
- [Poetry](https://python-poetry.org/docs/#installation)

## Installation

```bash
cd NCBI Gene
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

Download the data for the ncbi_gene transform:

```bash
poetry run ncbi_gene download
```

To run the Koza transform for NCBI Gene:

```bash
poetry run ncbi_gene transform
```

To see available options:

```bash
poetry run ncbi_gene download --help
# or
poetry run ncbi_gene transform --help
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

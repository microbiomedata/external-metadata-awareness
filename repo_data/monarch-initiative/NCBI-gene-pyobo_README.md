# ncbi-gene-pyobo

Automatic translation of NCBIGene into `obo`/`owl`/`obojson` via [pyobo](https://github.com/biopragmatics/pyobo/) and [ROBOT](http://robot.obolibrary.org). Also generates [KGX](https://github.com/biolink/kgx) `nodes.tsv` and `edges.tsv` for the same using [duckdb](https://duckdb.org).

### Setup
Create a virtual environment of your choice
```
pip install poetry
cd ncbi-gene-pyobo
poetry install
```

### Get the obo file
```shell
make obo
```
or
```shell
ncbi-gene get-obo
```

### Generate the owl file
```shell
make owl
```

<!-- ### Generate the obo-json file
```shell
make json
``` -->
### Generate KGX TSVs
```shell
make kgx
```

<!-- ### Make a release
```shell
make release
```
This creates the release-{YY-MM-DD}.tar.gz file which contains the OBO, OWL, JSON, and the KGX nodes.tsv and edges.tsv files. -->

# Acknowledgements

This [cookiecutter](https://cookiecutter.readthedocs.io/en/stable/README.html) project was developed from the [monarch-project-template](https://github.com/monarch-initiative/monarch-project-template) template and will be kept up-to-date using [cruft](https://cruft.github.io/cruft/).

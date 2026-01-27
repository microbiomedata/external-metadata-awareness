# rdf-sql-bulkloader

Bulk load of SQL table from RDF in Python

## Install

```bash
pip install rdf-sql-bulkloader
```

## Usage (Command Line)

```
rdf-sql-bulkloader load-sqlite  -o cl.db cl.owl
```

Note: currently only sqlite supported

## Usage (Programmatic)

See tests

## Core table

```
CREATE TABLE statement (
	id TEXT,
	subject TEXT,
	predicate TEXT,
	object TEXT,
	value TEXT,
	datatype TEXT,
	language TEXT,
        graph TEXT
);
```

## Prefixes

this uses the merged prefixmap from [prefixmaps](https://github.com/linkml/prefixmaps) by default

This can be overridden programmatically when instantiating a loader, e.g

Explicit map:

```python
loader = SqliteBulkloader(path=path, prefix_map={...})
```

Using pre-registered:

```python
loader = SqliteBulkloader(path=path, named_prefix_maps=["obo", "prefixcc"])
```

- TODO: add override from CLI


## Acknowledgements

This work was entirely inspired by James Overton's [rdftab.rs](https://github.com/ontodev/rdftab.rs)

This [cookiecutter](https://cookiecutter.readthedocs.io/en/stable/README.html) project was developed from the [sphintoxetry-cookiecutter](https://github.com/hrshdhgd/sphintoxetry-cookiecutter) template and will be kept up-to-date using [cruft](https://cruft.github.io/cruft/).

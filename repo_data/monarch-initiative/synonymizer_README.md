# synonymizer

The main objective of this tool is to apply custom rules for entity recognition to supplement the ontology dictionary generated from [kgx](https://github.com/biolink/kgx) for [ontoRunNER](https://github.com/monarch-initiative/ontorunner).

## Setups

`python setup.py install`

## Steps

- Get termlist files for ontologies:
  - The source here is `ontology_nodes.tsv` file derived from kgx as shown [here](https://monarch-initiative.github.io/ontorunner/static/intro.html#ontology-to-kgx-tsv)
  - From `ontoRunNER` use [`prepare-termlist`](https://monarch-initiative.github.io/ontorunner/static/intro.html#preparing-term-list) to get `ontology_termlist.tsv`

- Have a `rules.yaml` and `schema.yaml` files prepared that resemble [`synonym_rules.yaml`](https://github.com/monarch-initiative/synonymizer/blob/main/rulebook/synonym_rules.yaml) and [`schema.yaml`](https://github.com/monarch-initiative/synonymizer/blob/main/schema.yaml) in this project.

## Python
```
from synonymizer import synonymize
synonymize.run(
    rule_file = [path to rules.yaml],
    schema_file = [path to schema.yaml],
    data_folder = [location of the folder that cotains the termlist.tsv files]
    )
```

## CLI
```
python -m synonymizer.cli run 
       -r [path to rules.yaml] 
       -s [path to schema.yaml] 
       -d [location of the folder that cotains the termlist.tsv files]
```
or
```
python -m synonymizer.cli run 
       --rule [path to rules.yaml] 
       --schema [path to schema.yaml] 
       --data [location of the folder that cotains the termlist.tsv files]
```

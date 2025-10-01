# Verificado [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10557434.svg)](https://doi.org/10.5281/zenodo.10557434)

Validate ontology relationships using [Ubergraph](https://zenodo.org/record/7249759#.ZDRuZOzML1c) as source of truth. Relationships in this context may be subClassOf axioms between names classes (e.g. 'lymphocyte' subClassOf 'cell') or existential restrictions, (e.g. 'enterocyte' part_of some ‘intestinal epithelium’).

Ubergraph is an RDF triplestore with [39 OBO ontologies](https://github.com/INCATools/ubergraph#integrated-obo-ontology-triplestore) merged, precomputed OWL classification and materialised class relationship from existential property restrictions.  Validation therefore works for any directly asserted or inferred/indirect subClassOf relationship or existential restriction.


## Install

### Dependencies

This package depends on [Graphviz](https://graphviz.org/) and [OBOGraphviz](https://www.npmjs.com/package/obographviz) to represent the validation as a graph.

#### Graphviz

On macOS:

```bash
brew install graphviz
```

On Linux:

```bash
apt install graphviz
```

For another platform, please follow this instruction to [install Graphviz](https://graphviz.org/download/).

#### OBOGraphviz

Before installing OBOGraphviz, make sure you have installed Node.js version >= 14.16. Please follow this instructions to [install Node and npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm).

Then install the `obographviz` package globally:

```bash
npm install -g obographviz
```

### `verificado` package
```bash
pip install verificado
```

## Configure YAML file

In the config file, it is defined the list of relationships the validation should run on. The order is essential.

The yaml file needs to have the keys `relationships` and `filename`. Check an example below:

```yaml
relationships:
  sub_class_of: rdfs:subClassOf
  part_of: BFO:0000050
  connected_to: RO:0001025
  has_soma_location: RO:0002100
  ...

filename: path/to/filename.csv
```

The filename can be in TSV or CSV. When using CSV, double-quote if the label contains a common. It's preferred to have the following columns:

| s                   | slabel                                | user_slabel                               | o                  | olabel                                | user_olabel                               |
|---------------------|---------------------------------------|-------------------------------------------|--------------------|---------------------------------------|-------------------------------------------|
| the subject term ID | the label of the term in the column s | optional label for the term given by user | the object term ID | the label of the term in the column s | optional label for the term given by user |

However, the package can also accept TSV or CSV files representing a hierarchy. You can specify an undetermined number of levels, each level defined with an ontology term ID and the label of the term. Please check [an example](tests/test-generic.tsv) in the tests directory.

Add `to_be_parsed: true` to the yaml file when using this type of file.

```yaml
relationships:
  sub_class_of: rdfs:subClassOf
  part_of: BFO:0000050
  connected_to: RO:0001025
  has_soma_location: RO:0002100
  ...

filename: path/to/filename.csv
to_be_parsed: true
```

## Run verificado CLI

```bash
verificado validate --input path/to/config.yaml --output path/to/output.csv
```

The `output.csv` file will be in the same format as the `filename.csv`. It will return the cases where a triple (subject, relationship, object) with the relationships listed in the yaml file was not found in Ubergraph.

## List of ontologies available

To know which ontologies and their version are available in Ubergraph, use the following CLI:

```bash
verificado ontologies_version --output filename.json
```

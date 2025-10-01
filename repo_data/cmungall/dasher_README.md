# Dasher: Semantic QC Framework

Base framework for running QC checks over multiple knowledge sources. Potential examples include:

 - OBO Dashboard
 - GO Rules
 - Monarch
 - KG frameworks

See
https://docs.google.com/document/d/1ld73pVz_BIH22jRBZuV0RVDeSiuGyQpD1u_F9Yv9gg0/edit#

The core components:

 - a schema for representing both metrics themselves and the results of evaluating them
 - TODO: code for downloading sources and loading them into a database
 - TODO: code for executing these metrics on these sources
 - TODO: lightweight view layer to generate an HTML grid summary

## Schema

Browse the schema here: [http://cmungall.github.io/dasher](http://cmungall.github.io/dasher)

See the [schema/](schema/) folder

The source is in YAML (biolinkml)

Currently the main derived artefacts of interest are:

 - [JSON Schema](src/schema/semqc.schema.json)
 - [Python dataclasses](src/schema/semqc_datamodel.py)

## Download/Preparation

TODO

The idea is to use blazegraph-runner here.

Assume each source is trivially convertable to RDF

## Executing Metrics

TODO

Assumption that a number of generic mechanisms can be used:

 - OWL: Reasoning
 - Shapes/ShEx
 - JSON-Schema validation (requires JSON-LD framing)
 - SPARQL (e.g. robot checks)

Additionally, each implementation using this framework is free to add in their own procedural checks, e.g. in Python, although declarative is preferred

The code will generate json/yaml-ld conforming to the schema above

Implementing pipelines e.g Jenkins can choose to do things like fail-fast based on queries of result set

## Display

TODO

Something simple such as mustache / liquid templates over the above json-ld

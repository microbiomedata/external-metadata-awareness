# semantic-variable-registry

Global registry of semantic variables ("FAIRiables") - EXPERIMENTAL/ALPHA

This repo contains both a framework and content for making FAIR semantic variables. The idea is to compile from
a source representation to generate multiple sub-variables.

## Metamodel

 - [https://linkml.github.io/semantic-variable-registry/Core](https://linkml.github.io/semantic-variable-registry/Core)
 - [src/gsvr/schema](src/gsvr/schema)

Note: the schema imports the metamodel, until we have a way to run gen-docs with unmerged schemas then
it is best to look at the Core subset.

## Variables

see [tests/input/examples](tests/input/examples)

## Translations

- OWL
- SKOS
- LinkML
- SHACL
- SQL DDL
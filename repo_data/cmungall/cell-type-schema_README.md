# LinkML schema for cell types

EXPERIMENTAL

This is an attempt to seed a schema that can be used for cell types.

 * [src/schema/celltype.yaml](https://github.com/cmungall/cell-type-schema/blob/main/src/schema/celltype.yaml)

Why have a schema when we have a cell ontology?

The ontology doesn't provide a structure that can be used to exchange
instance-level data or how the ontology should relate to experimental
data.

Additionally, the "shape" of the ontology is described by a mix of dosdps and robot templates

This is an attempt to define a LinkML schema for cell types, starting with neuronal cell types in the Allen Neuron project

The schema should be manually defined but to bootstrap we generate a
schema from existing robot templates. The result is currently only
intended for now for me as a way to better explore the templates.

## Generation of schema from robot templates

the schema is currently entirely auto-generated from these robot templates:

https://github.com/obophenotype/brain_data_standards_ontologies/blob/master/src/templates/

See Makefile.seed

## Generation of downstream artefacts

See various folders in repo

## generation of markdown docs

https://cmungall.github.io/cell-type-schema/

## TODO ENUMS

One of the advantages of linkml is the elegant handling of semantic enums - we are not incorporating this yet.

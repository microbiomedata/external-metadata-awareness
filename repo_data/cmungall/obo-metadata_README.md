# obo-metadata

This is a demonstration project on how to create a metadata SCHEMA for OBO that can be
used for constraint checking.

The intended workflow is:

 * The core properties are [maintained in a google sheet](https://docs.google.com/spreadsheets/d/1YU_58PB-TaxlvJ5oIneUig8kB8CbmHyR30hUqfD0ZtE/edit) and synced with COGs
 * The sheet is compiled to different products including:
     1. a SCHEMA that can be used for VALIDATION
     2. OWL AnnotationProperties (omo.owl) that can be IMPORTED in different ontologies


Currently, the format of the schema is LinkML yaml. This can be used to generate different
valdation schemas

 - SHACL
 - JSON-Schema
 - LinkML itself


As a DEMO FLAGSHIP APPLICATION the
[OAK](https://incatools.github.io/ontology-access-kit/) library and
command line tool implements an efficient OMO checker that takes as input:

 1. the OMO LinkML schema
 2. a SQLite version of an ontology created using rdftab

And produces a report

## Schema

- [google sheets](https://docs.google.com/spreadsheets/d/1YU_58PB-TaxlvJ5oIneUig8kB8CbmHyR30hUqfD0ZtE/edit) (partial)
- [obo-metadata.yaml](src/linkml/obo-metadata.yaml)

## Examples

See [examples](examples)

## OBO Report

PRELIMINARY!!!

- [sheet](https://docs.google.com/spreadsheets/d/1Er8xYeKMvKKo-MGQf7w9jUgCWTOZwprDq9Td2Nuu4Po/edit#gid=488211236)
- analysis [notebooks](notebooks)

## Manifest

 * Generated docs: [cmungall.github.io/obo-metadata/](https://cmungall.github.io/obo-metadata/)
     * Example property: https://cmungall.github.io/obo-metadata/definition/
     * Example metaclass: https://cmungall.github.io/obo-metadata/Class/
 * Source: [src/linkml/](src/linkml/)
 * Analysis (v preliminary)
     * [notebooks](notebooks)
 * Derived files: [project](https://github.com/cmungall/obo-metadata/tree/main/project)
     * Schemasheets: TODO: sync w COGS [project/sheets](project/sheets)
     * JSON-Schema [project/json-schema](project/jsonschema)
     * etc


## How to validate

You will need to:

 1. Install OAK
 2. Obtain the SQLite version of the ontology(ies) to be validated
 3. Run on command line

See:

 * [howtos/validate-an-obo-ontology](https://incatools.github.io/ontology-access-kit/howtos/validate-an-obo-ontology.html)
 * In: [OAK](https://github.com/INCATools/ontology-access-kit/)


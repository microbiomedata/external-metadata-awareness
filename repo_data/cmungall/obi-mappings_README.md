# OBI mappings

This repo contains experimental AUTOMATED mappings between OBI and other ontologies and ontology-like resources

For context see:

https://github.com/obi-ontology/obi/issues/1304

In future, this may potentially be included in [mapping commons](https://github.com/mapping-commons)

## Inputs

See [downloads](downloads)

 * obi
 * bao
 * mesh
 * wikidata TODO

## Outputs

All mappings are in [SSSOM](https://github.com/mapping-commons/SSSOM), TSV rendering

Currently we use owl:equivalentClass as predicate in the mappings, but this could be skos:exactMatch. The goal is to provide precise 1:1 mappings.

IMPORTANT NOTE: we perform a dedupe step usings sssom-py, but
otherwise we leave in all lexical matches, even low confidence
ones. These are useful for getting a sense of general conceptual
overlap between two resources. In future we will use boomer to reduce
these. For now, pay attention to the confidence score column and
match_category. In general confidence <0.5 is likely to be a false
positive.

See [mappings](mappings)

## Methods

We use rdfmatch

Rules are in conf/

See Makefile

TODO: instructions on how to run with Docker

## MOTIVATION

Mappings are extremely useful for the users of ontologies. It allows users to map annotations from one system to another.

Mappings are also very useful for a gap analysis of ontologies. TODO: add unmapped

## TODO

User boomer to refine mappings

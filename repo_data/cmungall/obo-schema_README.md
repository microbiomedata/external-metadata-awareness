# Map of OBO schema

This repo includes an experimehtal schema for OBO classes

Schema: [obo-schema](http://cmungall.github.io/obo-schema)

## Basic idea

This is intended to give a high level view of how a subset of classes in OBO are structured and connect together.

IT IS MASSIVELY UNDERDOCUMENTED AND EXPERIMENTAL

It is *not* intended as a replacement for COB, which gives a biological realist view

Instead, this repo is for a "schema" in which instances are OBO classes. We have separate schema classes for:

 - [species-neutral anatomical entities](https://cmungall.github.io/obo-schema/SpeciesNeutralGrossEvolvedAnatomicalEntity.html)
 - [species-generic anatomical entities](https://cmungall.github.io/obo-schema/SpeciesGenericGrossEvolvedAnatomicalEntity.html)

This distinction would not make sense for modeling actual instances of
anatomical structures, which are always specific to an organism in a
species. However, this "metaclass" level distinction is useful for seeing how classes and ontologies are organized in OBO.

The schema is driven by biolinkml yaml

An example class:

```yaml
  species neutral gross evolved anatomical entity:
    is_a: gross evolved anatomical entity
    mixins:
      - species neutral
    slot_usage:
      subclass of:
        range: species neutral gross evolved anatomical entity  # except for root
      part of:
        range: species neutral gross evolved anatomical entity  # except for root
      develops from:
        range: species neutral gross evolved anatomical entity
      existence starts during:
        range: species neutral life stage
      existence ends during:
        range: species neutral life stage
    id_prefixes:
      - UBERON
      - PO
      - FAO
      - NCIT
```

biolinkml is single-inheritenace, but mixins can be used for "traits"
of classes. We have mixins for representing species
specific-vs-neutral, for "origin" (e.g. did the entity evolve, was it
made in a lab, is it a variant or aberrant form of something natural).

We also annotate which ID prefixes are expected for a given (meta)class

We make UML diagrams for each (meta)class but these look a bit janky. E.g.

![img](http://yuml.me/diagram/nofunky;dir:TB/class/[LifeStage],[GrossEvolvedAnatomicalEntity],[EvolvedCellType],[EvolvedAnatomicalEntity]%3Cdevelops%20from%200..*-++[EvolvedAnatomicalEntity],[EvolvedAnatomicalEntity]%3Cpart%20of%200..1-++[EvolvedAnatomicalEntity],[EvolvedAnatomicalEntity]%3Csubclass%20of%200..*-++[EvolvedAnatomicalEntity],[AnatomicalAtomicPhenotypicFeature]++-%20characteristic%20of%200..1%3E[EvolvedAnatomicalEntity],[CellularEvolvedAnatomicalEntity]++-%20part%20of%200..1%3E[EvolvedAnatomicalEntity],[GrossEvolvedAnatomicalEntity]++-%20part%20of%200..1%3E[EvolvedAnatomicalEntity],[GrossEvolvedAnatomicalEntity]++-%20subclass%20of%200..*%3E[EvolvedAnatomicalEntity],[EvolvedAnatomicalEntity]uses%20-.-%3E[Evolved],[EvolvedAnatomicalEntity]%5E-[GrossEvolvedAnatomicalEntity],[EvolvedAnatomicalEntity]%5E-[EvolvedCellType],[EvolvedAnatomicalEntity]%5E-[CellularEvolvedAnatomicalEntity],[AnatomicalEntity]%5E-[EvolvedAnatomicalEntity],[Evolved],[CellularEvolvedAnatomicalEntity],[AnatomicalEntity],[AnatomicalAtomicPhenotypicFeature])

## Relationship to DPs

TBD

## Schema

Browse the schema here: [http://cmungall.github.io/obo-schema](http://cmungall.github.io/obo-schema)

However, the markdown does not include everything in the yaml. For now it may be best to view the yaml directly.

See the [src/schema/](src/schema/) folder

The source is in YAML (biolinkml)

Currently the main derived artefacts of interest are:

 - [JSON Schema](src/schema/obo-schema.schema.json)
 - [ShEx](src/schema/obo-schema.shex)
 - [Python dataclasses](src/schema/obo-schema_datamodel.py)

With care, you also see:

 - [OWL](src/schema/obo-schema.owl.ttl) -- note this should be read as a meta-ontology by OBO people

## TODO

lots

# Organoid Registry

A registry of organs grown via in-vitro methods.

The end product is:

 * [organoid.owl](organoid.owl)

Which is both instances and grouping classes

# Methods

The ontology/KB is assembled from the following:

 * [kb/organoid-instances.ttl](kb/organoid-instances.ttl) - instances of organoids
 * [organid-core.obo](organid-core.obo) - upper ontology
 * [modules/organoid.tsv](modules/organoid.tsv) - grouping classes

See the Makefile for details.

Reasoning is used to automatically place organoids into grouping categories like 'brain organoid'

The instance model consists of triples

    _:organoidN models _:protoOrganN
    _:protoOrganN type UberonClass





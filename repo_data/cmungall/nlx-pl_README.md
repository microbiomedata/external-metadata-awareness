## Synopsis

## Description

This repo contains a collection of prolog utilities for querying and
extracting information from NeuroLex.

Prolog has a number of benefits here:

 * Fast loading of nlx triples
 * More powerful programmatic/transformative/declarative access than SPARQL

This main goal of this project is to produce an OWL version of
Neurolex that uses OBO Purls for classes, is suitable for reasoning,
uses standard OWL axiomatic constructs (e.g. neuron-N SubClassOf
soma_part_of some BrainRegion-A), removes duplication, fixes numerous
nlx issues (such as duplication of concepts).

It should also be useful for querying nlx in its standard RDF form.

## Dependencies

 * http://swi-prolog.org (tested on swipl 7)
 * unix make
 * wget
 * owltools (optional)

## Getting started

### Fetching neurolex

Type

    make nlx_stage_all.rdf

This will pull the raw triples from the neurolex rdf dump (nlx_stage_all.rdf) into a local file

### Querying neurolex

(This section assumes a minimal knowledge of prolog - to query the OWL scroll down to 'transforming nlx to OWL')

Type

    swipl -g [nlx_util]

This will start a SWIPL session, loading the nlx_util.pl prolog code,
which defines helper predicates, and also calls
'rdf_load_library(nlx)'. 

The first time this is called it will take a few minutes as there is a
lot of RDF to parse. This will create a directory RDF-Cache/ with a
fast-cached version of nlx. This cached version will automatically be
loaded on future iterations (until the RDF is re-downloaded).

Note that you will see a series of warnings. These can be ignored for
now. The reason is that the neurolex property labels clash with prolog
builtins. This will be fixed in future versions. Even though it looks
bad, it's harmless.

The following show interactive queries that can be performed in the shell:

### iterate over neurons

A unary predicate is created for every nlx class:

    ?- neuron(X).
    X = 'http://neurolex.org/wiki/Sao2128417084' ;
    X = 'http://neurolex.org/wiki/Sao383526650' ;
    X = 'http://neurolex.org/wiki/Nlx_cell_20081204' ;
    X = 'http://neurolex.org/wiki/Nifext_159' ;
    X = 'http://neurolex.org/wiki/Nifext_152' ;
    X = 'http://neurolex.org/wiki/Sao666951243' .

Other useful unary predicates:

 * regional_part_of_brain/1
 * parcellation_scheme_parcel/1

### iterate over neurons, showing labels and location

A binary predicate is created for every nlx property:
    
    ?- neuron(X),rdfs_label(X,L),located_in(X,S).
    X = 'http://neurolex.org/wiki/Sao2128417084',
    L = 'Sao2128417084',
    S = 'http://neurolex.org/wiki/Category-3ANeocortex' ;
    X = 'http://neurolex.org/wiki/Sao383526650',
    L = 'Sao383526650',
    S = 'http://neurolex.org/wiki/Category-3ACA3_stratum_pyramidale' ;
    X = 'http://neurolex.org/wiki/Nlx_cell_20081204',
    L = 'Nlx cell 20081204',
    S = 'http://neurolex.org/wiki/Category-3ACA2' ;
    X = 'http://neurolex.org/wiki/Nifext_159',
    L = 'Nifext 159',
    S = 'http://neurolex.org/wiki/Category-3ASubiculum' .

the capabilities here are similar to SPARQL. However, it is easier to
mix in programmatic features, plus whatever rules you like, defined in
prolog.

Other useful binary predicates:

 * located_in/2
 * species/2

## Transforming Nlx to OWL

The primary purpose of this codebase is to provide a "reason-able"
version of Nlx in OWL. This is not straightforward due to various
oddities in the RDF representation of neurolex (see Notes, below).

Type

    make nlx-owl.ttl

This is the same as:

    swipl -g [nlx_util],nlx2owl,halt

(no spaces after commas)

This is a work in progress. Gradually mapping more nlx predicates.

### OWL Modules

OWLTools is required for making modules. http://code.google.com/p/owltools

See the Makefile for pre-defined modules. It should be easy to add
more.

Neuron module:

    make nlx-neuron.owl

Nervous system part module (combo of parcels, parts of nervous system, and cell layers):

    make nlx-ns-part.owl

## Notes

(rough notes follow)

The neurolex triplestore has dual representations of everything.

E.g. for http://uri.neuinfo.org/nif/nifstd/sao2128417084

    Sao2128417084 type 'Neuron'
        rdfs:label Sao2128417084
        nlxp:label 'Neocortex pyramidal cell'
        located_in Neocortex
            inv(sameAs) ...
        AxonMyelination 'myelinated'
        Id sao2128417084
        sameAs  Neocortex_pyramidal_cell
                     type owl:Class
                     label 'Neocortex pyramidal cell'
                     AxonMyelination 'myelinated'

We rely on the Id field to unify everything.

Need to be careful - sometimes spaces are randomly inserted, e.g.

'CHEBI: 10093'

nlx_util.pl has some hacky code for handling this.
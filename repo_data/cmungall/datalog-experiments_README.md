# Datalog experiments

## Relation Graph

Currently testing an implementation of relation-graph in datalog.

See:

 * [src/relation_graph.dl](src/relation_graph.dl)

This is a datalog program using the souffle framework. It takes as
input triples as a TSV. Half of the DL program is mapping a subset of
RDF to OWL (we assume pre-reasoning using robot etc, the goal here is
to build something that provides all inferred subclass/existentials as
owlstar-style triples.

## Current results

|Reasoner|Ontology|Time|
|---|---|---|
|DATALOG|uberon|443.295|
|OWL|uberon|524.126|
|DATALOG|pato|1.986|
|OWL|pato|60.802|
|DATALOG|ro|0.065|
|OWL|ro|6.593|
|DATALOG|mondo|196.747|
|OWL|mondo|1208.941|
|DATALOG|hp|91.252|
|OWL|hp|671.6|
|DATALOG|mp|157.588|
|OWL|mp|1105.9|
|DATALOG|go|104.101|
|OWL|go|1115.936|
|DATALOG|chebi|460.024|
|OWL|chebi|563.541|
|DATALOG|obi|1.802|
|OWL|obi|108.82|
|DATALOG|zfa|5.261|
|OWL|zfa|68.149|
|DATALOG|envo|6.481|
|OWL|envo|104.404|

using relation-graph

the analysis needs thoroughly checked...

## EL classifier

There is a classifier for a subset of EL but it does not appear to be performant:

 * [src/el_classifier.dl](src/el_classifier.dl)


## Connectivity Reasoning

The datalog framework makes it easy to extend inference to include edge weights etc

the following is for edges where all weights are one, but easy to extend

```prolog
.decl edge(x:symbol, y:symbol)
.input edge
.decl path(x:symbol, y:symbol, d:number)
.output path
path(x, y, 1) :- edge(x, y).
path(x, y, d+1) :- path(x, z, d), edge(z, y).
```

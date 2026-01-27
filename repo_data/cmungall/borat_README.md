# BORAT: Bayesian Ontology Rules and Abduction Toolkit

A library for probabilistic reasoning over OWL and rule-based
ontologies.

Given

 1. A set of logical axioms `A` which are taken to be true (`Pr=1.0`)
 2. A set of hypothetical axioms `H` which are pairs of `<Axiom,Probability`.

Find the most likely consistent set of choices from `H`, when
inference is taken into consideration. We assume probability zero for
incoherent ontologies.

Currently only a subset of OWL is supported

```
Axiom ::= AtomicAxiom | "not(" AtomicAxiom ")"
AtomicAxiom ::= "subClassOf(" Cls "," Cls ")"
AtomicAxiom ::= "disjointWith(" Cls "," Cls ")"
AtomicAxiom ::= "equivalentTo(" Cls "," Cls ")"
```

## Examples

See [tests](tests) folder for now

## RDF Encoding

A probabilistic ontology can be encoded in either of two ways:

 * Using q-quads or trig, and adding a triple indicating probability of named graph
 * Using OWL reification

Non-weighted logical axioms are encoded in the usual way; any axiom
that does not conform to either of the above criteria is treated as
`Pr=1`.

See [tests/data/simple.trig](tests/data/simple.trig)

## History

See https://github.com/monarch-initiative/kboom

## TODO

 * add CLI
 * kboom subset
 * add abduction hooks
 * dot export

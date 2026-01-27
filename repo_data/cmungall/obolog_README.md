## Obolog specification (abandoned)

This repo contains the 2009 proposed Obolog specification. Obolog was
intended as a subset of Common Logic aimed at providing simple,
intuitive language constructs for building ontologies with full
semantic rigor.

The intent was to map OBO Format to Obolog and to use OBO Format tools
for working with "atomic Obolog" and databases for working with
annotations and instance data, with datalog reasoning over both, and
the ability to use more expressive reasoning over smaller corpi as
required.

This work has been superseded, with OWL and RDF as the main supported
languages for working with ontologies and semantic data. This
repository has been placed on GitHub primarily for logic geek
archaeologists.

The specification can be found here:

 * [spec/obolog-spec.pdf](spec/obolog-spec.pdf)

Note the specification is partially derived from First Order Logic
specifications provided as `.kif` files. As a result it's fairly dense
with formulae and lacking in prose. See the Makefile for how this was
constructed, and the underlying kif files are in this folder.

The core semantics are specified directly in KIF here:

 * [obolog.kif](obolog.kif)

(The KIF is trivially transformable to Common Logic CLIF syntax)

## Website

An accompanying website provides an HTML rendering of the KIF specification:

 * [https://cmungall.github.io/obolog/obolog](https://cmungall.github.io/obolog/obolog)

## Datalog Translation

A translation of a subset of the KIF to datalog is provided here:

 * [obolog-horn.kif](obolog-horn.kif) (KIF syntax)
 * [obolog-horn-m.pro](obolog-horn-m.pro) (Prolog syntax)

## RO Obolog

The RO 2005 paper was translated to OBOFormat1.3 with obolog semantics

I seem to have lost the original files. Partial restoration here:

 * [https://cmungall.github.io/obolog/ro/ro](https://cmungall.github.io/obolog/ro/ro)

See also:

 * https://github.com/BFO-ontology/BFO/tree/master/src/ontology/fol-mungall
    * [ro-core-type-type](https://github.com/BFO-ontology/BFO/blob/master/src/ontology/fol-mungall/fol-src/ro-core-type-type-src.clif)
    * [ro-core-instance-instance](https://github.com/BFO-ontology/BFO/blob/master/src/ontology/fol-mungall/fol-src/ro-core-instance-instance-src.clif)

## Presentations

 * [obo-and-common-logic](https://www.slideshare.net/cmungall/obo-and-common-logic)


## Theorem Proving

 * obolog.lisp -- FOL semantics, specified in syntax that should be KIF compatible
 * obolog-theorem-prover.lisp -- SNARK wrapper
 * obolog-theorem-prover.sh -- runs theorem prover
 * ro.obolog -- OBO-RO automatically converted to obolog format


### Notes

For practical reasoning purposes SNARK seems to be incredibly
slow. Even for the proofs added, using RO can slow things down
hugely. For testing it is best to trim the database down to the bare
minimum # of facts

At the moment there are only 2 proofs - one for universal-level
relations (called "links" in obo-ese for now) and one for
instance-level relations

             

ROGE-ENGINE
===========

Rhino ontology generation engine.

Description
-----------

This is an ontology generation framework implemented in
Rhino/javascript on top of OWLTools and the OWLAPI.

It can be configured for a wide variery of patterns. So far the
ontology conifguration is for phenotype ontologies

Quickstart
----------

* install OWLTools
* copy pato.owl and caro.owl to ontologies/ directory
* owlrhino  -f generators/run-phenotype.js

open the resulting ontology (out/t.owl) in Protege and classify using Elk

See also
--------

https://github.com/cmungall/shoge

Whilst Shoge is in some ways superior and allows high-level
declarative grammars for ontology generation, it is harder to use
since it is entirely prolog. ROGE makes use of the Manchester OWLAPI.

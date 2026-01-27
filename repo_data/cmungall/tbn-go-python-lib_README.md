Library for working with OWL, with an emphasis on the subset of OWL
required by users of GO and OBO ontologies, plus convenience methods.

Currently what is supported is:

 * The "OBO Basic" subset of OWL
 * Individuals and connections between them (LEGO/Noctua models)

It is not intended for performing advanced processing of all OWL axiom
types. For that we recommend:

 * jython + the OWLAPI. See LINK TO DAVID'S EXAMPLES HERE
 * FuXi

To see the capabilities of this library, see the tests/ directory

Some typical use cases this library is intended to address:

 * produce basic ontology reports (e.g. table of IDs plus labels)
 * Translate ontology representation to a networkx graph using a subset of relations (ObjectProperties)
 * Analyze LEGO models

What it won't do:

 * parse GAFs
 * complex OWL processing

PACKAGE NAMES, APIS ETC ALL SUBJECT TO CHANGE!!

Proposed Refactor:

Use the following set of packages:

 * ontol
    * Ontology.py
    * OWLParser
    * NetworkExporter => rename
    * reasoner
       * BasicReasoner
 * lego
    * Lego
 * assoc



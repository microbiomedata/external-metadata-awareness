# YOM is a YAML Ontology Metalanguage

YOM is a YAML format for a superset of OWL that extends the language
with a __MetaClass__ construct. A MetaClass is analogous to specification
for a design pattern. We use the same YAML schema as
[DOSDPs](https://github.com/dosumis/dead_simple_owl_design_patterns).

OWL Classes *implement* MetaClasses. A MetaClass can *generate*
classes (or axioms for a class), or it can *generate/test* if an
existing OWL class (or its axioms) implement the MetaClass.

## Example

Consider anatomical classes such as

 * mucosa of esophagus
 * mucosa of small intestine
 * mucosa of large intestine
 * submucosa of esophagus
 * submucosa of small intestine
 * submucosa of large intestine
 * lamina propria of esophagus

As can be seen there is considerable repetition. This is also true of
the logical and annotation axioms for each class.

These all implement a MetaClass "mucosal layer", specified in YAML as:

```
id: uberon-patterns:mucosal_layers
a: MetaClass

relations:
  part of: BFO_0000050

name: 
  text: "%s of %s"
  vars: 
    - layer
    - segment

def: 
  text: "A %s that lines the %s."
  vars:
    - layer
    - segment

equivalentTo: 
  text: "% that 'part of' some %s"

  vars:
    - layer
    - segment
```

An OWLClass can be represented using the following yom-object, here written using YAML syntax:

```
id: UBERON:1234
implements: uberon-patterns:mucosal_layers
layer: mucosa
segment: intestine
```

(note that tabular formats are also possible too)

Note the use of human-readable shortforms: these are mapped to IRIs via a JSON-LD context

An OWLGenerator will generate/compile the following axioms:

```
Class: UBERON:1234
Annotations:
  rdfs:label "mucosa of intestine"
EquivalentTo: 'mucosa' and 'part of' some 'intestine'
```

(but actual URIs would be used here)

An OWL Reasoner can then be used to classify this

Note that the YAML source is not restricted to filling in template
values. Arbitrary axioms can be added:

```
id: UBERON:1234
implements: uberon-patterns:mucosal_layers
layer: mucosa
segment: intestine
annotations:
 - property: seeAlso
   value: NCIt:nnnn
comments:
 - comment: The intestinal mucosa of the gerbil is very interesting
   source: doi:1.1.1.1/gerbil-journal
```

Note that one of the goals is to make an easy to author format like
.obo, but to reduce repetition.

## Parsing/Reverse Translation

Not implemented yet

## Superlanguage vs Layering

Currently yom-lang is conceived of as a superlanguage: Anything in OWL
can be said in yom-lang, but not everything in yom-lang can be said in
OWL.

However, it should be possible to layer YOM Ontology Objects into OWL
using annotations.

For example, the following yom-object

```
id: UBERON:1234
implements: uberon-patterns:mucosal_layers
layer: mucosa
segment: intestine
```

Could be represented as the following OWL source:

```
Class: UBERON:1234
Annotations:
  implements uberon-patterns:mucosal_layers,
  layer mucosa,
  segment intestine
```

YOML metaclasses could also be used, but due to creation of blank
nodes via nesting this would be an awkward way to work with them, and
pose no advantages over YAML.

## Using this

Currently no command line interface is implemented: everything is via
java code. See unit tests for examples.


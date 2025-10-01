# ENVO variable Parser

Prolog grammar for parsing complex compositional variables into expressions

## Results

IN PROGRESS.

See [target/parse.txt](target/parse.txt) for very early results.

So far we are just doing a basic syntactic parse to generate a tree. This tree can then be mapped to OWL.

## Workflow

Type:

`make`

(todo: docker environment)

See [Makefile](Makefile) for full details.

Briefly:

first the xml is downloaded, then converted to OWL. (this derived product is checked in to the repo, so you do not need to do this part).

Labels are extracted and these are parsed using a [prolog DCG](prolog/grammar.pl)

Next step is to transform this to OWL expressions

## TODO

 - align with http://www.met.reading.ac.uk/~jonathan/CF_metadata/14.1/lexicon
    - adequate treatment of scalars, vectors, tensors, functions
 - generate OWL equivalence axioms
 - use UO in ontology conversion
 - use PATO (flux etc) as terminals
 - use ENVO material entity for 'in' and 'into'
 - use ENVO process for wind etc
 - Dockerify

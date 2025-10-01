# Scowl scripts

This is an experiment.. may be abandoned if a better way of doing this comes along

The main motivation for this is replacing https://github.com/cmungall/obo-scripts

See MOSS doc for more details

## Instructions

You will need ammonite

### Examples

Extract SubClassOf axioms

    amm -p predef.sc sc-filter-subClassOf.sc test/data/cob.owl target/foo.owl

Same way to do this, but passing lambda on the command line:

    amm -p predef.sc -c 'saveOntology(ontFilter("test/data/cob.owl", a => { a match { case a @ SubClassOf(_,_,_) => true; case _ => false}}), "target/foo.owl")'

Another way, that allows passing in of the text directly with minimal boilerplate:

    ./sc-ont-grep.py -i test/data/cob.owl -o target/foo.owl 'case a @ SubClassOf(_,_,_) => true; case _ => false'


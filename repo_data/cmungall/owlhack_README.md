owlhack
=======

A perl convenience wrapper for OWL ontologies.

Current status: experimental and highly incomplete.

Currently this module relies on
[OWLTools](http://code.google.com/p/owltools) for I/O. Ontologies are
serialized as JSON (standard yet to be fully specified) using the
owltools command line runner.

Example
-------

    # Create an ontology object from an OWL document
    # note: this converts to .ojs behind-the-scenes
    my $ont = OWL->load("pizza.owl"); 

    # Iterate through all SubClass axioms writing Sub-Super pairs
    foreach my $axiom ($ont->getAxioms('SubClassOf')) {
       print $axiom->getSubClass . "\t" . $axiom->getSuperClass . "\n";
    }

Scripts
-------

See the bin/ directory

Not all scripts are complete. 

Requirements
------------

Currently the goals are to keep this fairly minimal (no Moose!)

 * JSON
 * OWLTools

See INSTALL.md

Documentation
-------------

Documentation is likely to remain minimal. You're best looking at
examples in the bin/ directory, or reading the .pm files
themselves. Beware: AUTOLOAD trickery ahead!

Some familiarity with the OWL API might help. Then again, it might
hinder..

If you're not comfortable with that, then this library probably isn't
for you!


Why use this?
-------------

In many ways you would be better off using the OWLAPI (there are many
JVM scripting languages to choose from - e.g. clojure, groovy,
rhino/js). If you're here you're probably a dyed in the wool perl
hacker.

Even then there are other options available. There are various
RDF-level libraries on CPAN, but you likely need something OWL
level. Onto-Perl is great, but isn't really an OWL API.

OWL::DirectSematics looks great, but last time I tried looked it was
quite slow, as it has to read in the entire RDF graph and apply the
RDF to OWL mappings.

owlhack is best for structural processing and transformations. At the
moment there is no interface to reasoning. The idea is that you can do
the reasoning steps out of band, but this isn't really ideal.

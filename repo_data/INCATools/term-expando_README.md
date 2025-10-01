term-expando
============

Dumb python library and CLI for performing expansion of IDs and
controlled terms in TSVs and other documents.

For example, given a TSV with an identifier column, insert an extra
column with the corresponding label from the identifier.

Another example: expand an ID with the reflexive transitive ancestors
in an ontology graph; the resulting document is optimized for lookups
by ontology term (the "golr closure pattern")

It is also possible to a weak form of concept recognition: provide a
lookup table of name or synonym -> ID, and use this to expand a column
with names.

Expansions can come from pre-made lookup tables, or an ontology can be
used as source.

See the tests folder for more information

The data model is deliberately simple. There can be any number of
named lookup tables. A lookup table is a mapping between a string and
a list of strings. The list of strings is stored internally as a
pipe-separated string. The lookup tables can be loaded from a TSV, or
constructed from an ontology (requires obojson).

Command Line
============

Help:

.. code-block:: sh

    expando --help


Currently there are two main commands: tsv and text, for expanding a
tsv doc and a general text doc

Expand a GPAD file, using a gene product ID (non-CURIE) to name lookup table:    

.. code-block:: sh

    expando -t tests/data/gp2name.tsv -l tests/data/go-small.json  -e id2name tsv -x  tests/data/pombase-small.gpad

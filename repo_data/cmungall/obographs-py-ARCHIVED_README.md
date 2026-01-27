
## A python library for OBO graphs

The entire functionality so far only consists of a (trivial) mapping
between [obographs](https://github.com/geneontology/obographs) and the python
[networkx](https://networkx.github.io/) library.

E.g. [tests/nucleus.json](tests/nucleus.json) to [examples/nucleus.png](examples/nucleus.png) (using a the networkx draw function)

## Intended uses

This is intended to be composed with other APIs, Services and command line tools.

For example, convert an ontology to obographs-json, load it using this library, and perform networkx operations (e.g. [centrality](https://networkx.github.io/documentation/development/reference/algorithms.centrality.html) ).

Or, fetch a bbop-graph from SciGraph or Golr and render for visualization

Jupyter notebooks for the above...

## Extensions

The idea is to keep this relatively lean, not tend towards a kitchen
sink, and instead allow this to be composed with other libraries. The
networkx library serves as a general graph API.

We may add functionality that is useful for general ontology work - e.g. indexing by synonyms, etc


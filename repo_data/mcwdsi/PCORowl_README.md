![DOI badge](https://zenodo.org/badge/DOI/10.5281/zenodo.1241209.svg)

This repository stores the configuration for the PCORowl Stardog virtual graph.

=======
# PCORowl
Modelling the PCORnet CDM in an OWL Ontology

The stardog-config directory contains files used in mapping the relational
PCORnet data to a graph data structure using the Stardog 4.0+ virtual graphs.

Usage:
stardog/bin/stardog-admin virtual add PCORowl.properties PCORowl.ttl -vfr2rml

Explanation:
PCORowl.properties specifies database connection settings.
PCORowl.ttl is a mapping of the PCORnet data into a graph structure. 
-v for verbose
-f for format, r2rml.

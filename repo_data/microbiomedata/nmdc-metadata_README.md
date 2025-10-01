
> [!WARNING] 
> This repository is deprecated.
> Please consider putting issues in:
> - [NMDC Schema](https://github.com/microbiomedata/nmdc-schema) for schema changes/issues.
> - [NMDC Ontology](https://github.com/microbiomedata/nmdc-ontology) for issues related to producing terms or term subsets.
> - [NMDC Runtime](https://github.com/microbiomedata/nmdc-runtime) for isseus related to ETL issues.

# Metadata management for the [National Microbiome Data Collaborative](https://microbiomedata.org/)
[![Build Status](https://travis-ci.org/microbiomedata/nmdc-metadata.svg?branch=master)](https://travis-ci.org/microbiomedata/nmdc-metadata)
![Deploy Documentation](https://github.com/microbiomedata/nmdc-metadata/workflows/Deploy%20Documentation/badge.svg?branch=master)
![GitHub last commit](https://img.shields.io/github/last-commit/microbiomedata/nmdc-metadata?branch=master&kill_cache=1)
![GitHub issues](https://img.shields.io/github/issues/microbiomedata/nmdc-metadata?branch=master&kill_cache=1)
![GitHub closed issues](https://img.shields.io/github/issues-closed-raw/microbiomedata/nmdc-metadata?branch=master&kill_cache=1)
![GitHub pull requests](https://img.shields.io/github/issues-pr-raw/microbiomedata/nmdc-metadata?branch=master&kill_cache=1)

The purpose of this repository is to manage metadata for the [National Microbiome Data Collaborative (NMDC)](https://microbiomedata.org/). The [NMDC](https://microbiomedata.org/) is a multi-organizational effort to enable integrated microbiome data across diverse areas in medicine, agriculture, bioenergy, and the environment. This integrated platform facilitates comprehensive discovery of and access to multidisciplinary microbiome data in order to unlock new possibilities with microbiome data science. 

Tasks managed by the repository are:
* Generating the [schema](https://github.com/microbiomedata/nmdc-metadata/tree/master/schema)
* Deploying the [documentation](https://microbiomedata.github.io/nmdc-metadata/) 
* [Integrating](./metadata-translation/notebooks) metadata from multiple environmental data repositories

## Background

The NMDC [Introduction to metadata and ontologies](https://microbiomedata.org/introduction-to-metadata-and-ontologies/) primer describes the context for this project.

## Schema

See the [slides](https://microbiomedata.github.io/nmdc-metadata/docs/schema-slides) describing the schema

The [NMDC schema](./schema) is used during the [translation process](./metadata-translation/notebooks) to specify how metadata elements are related.

![img](https://raw.githubusercontent.com/microbiomedata/nmdc-metadata/master/schema/nmdc_schema_uml.png)

The schema is also available as:

 * [JSON Schema](schema/nmdc.schema.json)
 * [Protobuf](schema/nmdc.proto)
 * [GraphQL](schema/nmdc.graphql)
 * [OWL](schema/nmdc.owl)
 * [ShEx](schema/nmdc.shex)

## Documentation
[Documentation](https://microbiomedata.github.io/nmdc-metadata/) for the [NMDC schema](./schema) can be browsed here:
* https://microbiomedata.github.io/nmdc-metadata/

## NMDC data
A zipped file of the NMDC can be downloaded [here](metadata-translation/src/data/nmdc_database.json.zip) (JSON format).

## Mapping resource
We use [SSSOM](https://github.com/OBOFoundry/SSSOM) to map fields in primary data sources to standard terms. The mapping between the GOLD data and MIxS terms this [SSSOM file](schema/mappings/gold-to-mixs.sssom.tsv).

## Standardization of characteristics
Entities in the schema are annotated with characteristics. When possible, we use standard terminologies and ontologies to define these characteristics. These standards include:
* [Minimum Information about any (x) Sequence (MIxS)](https://gensc.org/mixs/)
* The [Environment Ontology (ENVO)](https://github.com/EnvironmentOntology/envo)
 
We are actively involved in updating the [MIxS](https://gensc.org/mixs/) standards ([mixs-ng](https://github.com/GenomicsStandardsConsortium/mixs-ng)) and creating an RDF version of [MIxS](https://gensc.org/mixs/) ([mixs-rdf](https://github.com/GenomicsStandardsConsortium/mixs-rdf)).

See also our analysis of [MIxS descriptors](https://docs.google.com/document/d/141BWGbWdTuCQ_QoqdsO_BvHW37wJuLU9xZnvnHTEtNU/edit)

## Metadata sources
At present, we ingest metadata from the [Joint Genome Institute (JGI)](https://jgi.doe.gov/) and the [Environmental Molecular Sciences Lab (EMSL)](https://www.pnnl.gov/environmental-molecular-sciences-laboratory).  

The [NMDC schema](./schema) and [translation process](./metadata-translation/notebooks) will be modified as more metadata sources become available.

## Metadata integration

We use [Jupyter notebooks](https://github.com/microbiomedata/nmdc-metadata/tree/master/metadata-translation/notebooks) to integrate the metadata sources. This allows us to iterate quickly in a transparent and interactive manner as new metadata sources become available. 

Development of more comprehensive ETL pipeline will progress as the metadata sources and schema become more concrete.

## Identifiers

See [identifiers](docs/identifiers.md) documentation

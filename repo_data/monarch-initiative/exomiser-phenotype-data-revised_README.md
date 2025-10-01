# Exomiser Data Pipeline - Revised

Exomiser relies on Monarch as a source for phenotypic similarity flat files (tables). There are various pieces
that influence the resulting similarity tables, such as ontologies, algorithms and other. As we are converging on 
an entirely new way of doing phenotype similarity, we need to ensure that Exomiser inputs look as expected. Furthermore
the Exomiser phenotype data pipeline is currently a string of manually concatenated workflows executed by
the Exomiser team, which is unnecessarily complicated.

The goals of this project are:

1. Document the current Exomiser phenotype data pipeline to identify all its dependencies
2. Streamline the current Exomiser phenotype data pipeline into a single, executable workflow
3. Implement that workflow as an independent data pipeline that is kept current without the need of human intervention
4. Analysing the effect of using a lattice based classification model (uPheno 2, phenotypes across species are considered analogous, not equivalent) over an equivalence-based one (uPheno 1, phenotypes across species are considered equivalent)

## Developer instructions

- Run `sh odk.sh make all` to create data directories for pipelines
- The last_build_source directory contains the last generated phenodigm score tables used by Exomiser (as of early 2019, but at least a year older)

## Important links:

- [Current Exomiser docs on phenotype data pipeline](https://github.com/exomiser/Exomiser/tree/master/exomiser-data-phenotype)
- [Analysis of the various dependencies of the data pipeline](docs/data-dependencies.md)
- [Some notes on the old pipeline](docs/original-pipeline.md), with a bit of analysis
- [Internal notes on the current data pipeline](docs/meeting-notes.md)

# Exomiser Phenotype Data Dependency Audit

Repository: [https://github.com/exomiser/Exomiser/tree/master/exomiser-data-phenotype](https://github.com/exomiser/Exomiser/tree/master/exomiser-data-phenotype)

## People involved in this process:

* Nicolas Matentzoglu (ontologies, phenodigm, @matentzn)
* Jules Jacobsen (external data dependencies)
* Damian Smedley (Exomiser lead)
* David Osumi-Sutherland (ontologies, @dosumis)
* Chris Mungall (overall, @cmungall)


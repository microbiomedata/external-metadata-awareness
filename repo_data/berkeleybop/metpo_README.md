
![Build Status](https://github.com/berkeleybop/metpo/actions/workflows/qc.yml/badge.svg)
# METPO

Microbial ecophysiological trait and phenotype ontology

More information can be found at http://obofoundry.org/ontology/metpo

## Versions

### Stable release versions

The latest version of the ontology can always be found at:

http://purl.obolibrary.org/obo/metpo.owl

(note this will not show up until the request has been approved by obofoundry.org)

### Editors' version

Editors of this ontology should use the edit version, [src/ontology/metpo-edit.owl](src/ontology/metpo-edit.owl)

## Contact

Please use this GitHub repository's [Issue tracker](https://github.com/berkeleybop/metpo/issues) to request new terms/classes or report errors or specific concerns related to the ontology.

## Acknowledgements

This ontology repository was created using the [Ontology Development Kit (ODK)](https://github.com/INCATools/ontology-development-kit).

----

## Input:
- https://docs.google.com/spreadsheets/d/1_Lr-9_5QHi8QLvRyTZFSciUhzGKD4DbUObyTpJ16_RU/edit?gid=0#gid=0

## Notes
- https://github.com/berkeleybop/group-meetings/issues/155#issuecomment-2715444097

----

METPO is intended to drive mining knowldge out of papers form journals like IJSEM 
and expressing the findings with classes and predicates from METPO or the Biolink model, 
which would then become part of KG-Microbe.

We strive to keep our class heirachies pure. Reuse of terms from OBO foundry ontologies
and the use of logical axioms are hihg but secondary priorities.

## Repository Structure

This repository contains two main components:

### Ontology Development (`src/ontology/`)
The core METPO ontology is built using the Ontology Development Kit (ODK). The root Python code and Makefiles are **not involved** in ontology releases.

#### Building the Ontology

To rebuild the ontology from source (requires Docker):

```bash
cd src/ontology
make squeaky-clean          # Clean all generated files
./run.sh make all          # Full build with Docker wrapper
```

The build process:
- Fetches the latest CSV data from Google Sheets
- Generates robot template output
- Builds all ontology format files (OWL, OBO, JSON)

#### Creating a Release

To prepare a new release:

```bash
cd src/ontology
./run.sh prepare_release   # Copies files to project root
```

**Manual steps after prepare_release:**
- Review generated files in project root
- Git add, commit, and push changes
- Create GitHub release
- Monitor third-party systems (Bioportal, etc.)

#### Third-Party System Monitoring

After releases, monitor integration with:
- OBO Foundry
- Bioportal 
- Other ontology repositories

*Documentation needed: Detailed monitoring procedures and third-party system integration.*

### Literature Mining Pipeline (`literature_mining/`)
The literature mining component uses OntoGPT to extract knowledge from research papers (especially IJSEM) and annotates the extracted data using METPO ontology files. This pipeline is **separate from ontology maintenance** and its outputs are intended for integration into KG-Microbe.

The literature mining workflow uses:
- METPO ontology files as knowledge annotators
- OntoGPT for information extraction from abstracts
- Custom templates for structured data extraction

Final destination: KG-Microbe knowledge graph 

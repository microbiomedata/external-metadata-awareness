# go-ingest

| [Documentation](https://monarch-initiative.github.io/go-ingest) |

modularized go ingest

## Requirements

- Python >= 3.10
- [Poetry](https://python-poetry.org/docs/#installation)

## Setting Up a New Project

Upon creating a new project from the `cookiecutter-monarch-ingest` template, you can install and test the project:

```bash
cd go-ingest
make install
make test
```

There are a few additional steps to complete before the project is ready for use.

#### GitHub Repository

1. Create a new repository on GitHub.
1. Enable GitHub Actions to read and write to the repository (required to deploy the project to GitHub Pages).
   - in GitHub, go to Settings -> Action -> General -> Workflow permissions and choose read and write permissions
1. Initialize the local repository and push the code to GitHub. For example:

   ```bash
   cd go-ingest
   git init
   git remote add origin https://github.com/<username>/<repository>.git
   git add -A && git commit -m "Initial commit"
   git push -u origin main
   ```

#### Transform Code and Configuration

1. Edit the `download.yaml`, `transform.py`, `transform.yaml`, and `metadata.yaml` files to suit your needs.
   - For more information, see the [Koza documentation](https://koza.monarchinitiative.org) and [kghub-downloader](https://github.com/monarch-initiative/kghub-downloader).
1. Add any additional dependencies to the `pyproject.toml` file.
1. Adjust the contents of the `tests` directory to test the functionality of your transform.

#### Documentation

1. Update this `README.md` file with any additional information about the project.
1. Add any appropriate documentation to the `docs` directory.

> **Note:** After the GitHub Actions for deploying documentation runs, the documentation will be automatically deployed to GitHub Pages.  
> However, you will need to go to the repository settings and set the GitHub Pages source to the `gh-pages` branch, using the `/docs` directory.

#### GitHub Actions

This project is set up with several GitHub Actions workflows.  
You should not need to modify these workflows unless you want to change the behavior.  
The workflows are located in the `.github/workflows` directory:

- `test.yaml`: Run the pytest suite.
- `create-release.yaml`: Create a new release once a week, or manually.
- `deploy-docs.yaml`: Deploy the documentation to GitHub Pages (on pushes to main).
- `update-docs.yaml`: After a release, update the documentation with node/edge reports.


Once you have completed these steps, you can remove the [Setting Up a New Project](#setting-up-a-new-project) section from this `README.md` file.

## Installation

```bash
cd go-ingest
make install
# or
poetry install
```

> **Note** that the `make install` command is just a convenience wrapper around `poetry install`.

Once installed, you can check that everything is working as expected:

```bash
# Run the pytest suite
make test
# Download the data and run the Koza transform
make download
make run
```

## Usage

This project is set up with a Makefile for common tasks.  
To see available options:

```bash
make help
```

### Download and Transform

Download the data for the go_ingest transform:

```bash
poetry run go_ingest download
```

To run the Koza transform for go-ingest:

```bash
poetry run go_ingest transform
```

To see available options:

```bash
poetry run go_ingest download --help
# or
poetry run go_ingest transform --help
```

### Testing

To run the test suite:

```bash
make test
```

## Gene Ontology (GO) Annotation Database

The Gene Ontology Annotation Database compiles high-quality [Gene Ontology (GO)](http://www.geneontology.org/) annotations to proteins in the [UniProt Knowledgebase (UniProtKB)](https://www.uniprot.org/), RNA molecules from [RNACentral](http://rnacentral.org/) and protein complexes from the [Complex Portal](https://www.ebi.ac.uk/complexportal/home).

Manual annotation is the direct assignment of GO terms to proteins, ncRNA and protein complexes by curators from evidence extracted during the review of published scientific literature, with an appropriate evidence code assigned to give an assessment of the strength of the evidence.  GOA files contain a mixture of manual annotation supplied by members of the Gene Ontology Consortium and computationally assigned GO terms describing gene products. Annotation type is clearly indicated by associated evidence codes and there are links to the source data.

## [GO Annotations](#go_annotation)

There is a ReadMe.txt file that explains the different annotation files available.  The ingested Gene Annotation File (GAF) is a 17 column tab-delimited file. The file format conforms to the specifications demanded by the GO Consortium and therefore GO IDs and not GO term names are shown.

__**Biolink captured**__

##### Subject Concept Node (Gene)

* **biolink:Gene**
  * id (NCBIGene Entrez ID)

##### Object Concept Node (Gene Ontology Terms)

* **biolink:MolecularActivity**
  * id (GO ID)

* **biolink:BiologicalProcess**
  * id (GO ID)

* **biolink:CellularComponent**
  * id (GO ID)

##### Additional Gene Ontology Term Concept Nodes for possible use?

* **biolink:Pathway**
  * id (GO ID)

* **biolink:PhysiologicalProcess**
  * id (GO ID)

__**Associations**__

* **biolink:FunctionalAssociation**
    * id (random uuid)
    * subject (gene.id)
    * predicate (related_to)
    * object (go_term.id)
    * negated
    * has_evidence
    * publications
    * aggregating_knowledge_source (["infores:monarchinitiative"])
    * primary_knowledge_source

OR

* **biolink:MacromolecularMachineToMolecularActivityAssociation**:
    * id (random uuid)
    * subject (gene.id)
    * predicate (related_to)
    * object (go_term.id)
    * negated
    * has_evidence
    * publications
    * aggregating_knowledge_source (["infores:monarchinitiative"])
    * primary_knowledge_source
    
* **biolink:MacromolecularMachineToBiologicalProcessAssociation**:
    * id (random uuid)
    * subject (gene.id)
    * predicate (participates_in)
    * object (go_term.id)
    * negated
    * has_evidence
    * publications
    * aggregating_knowledge_source (["infores:monarchinitiative"])
    * primary_knowledge_source

* **biolink:MacromolecularMachineToCellularComponentAssociation**:
    * id (random uuid)
    * subject (gene.id)
    * predicate (located_in)
    * object (go_term.id)
    * negated
    * has_evidence
    * publications
    * aggregating_knowledge_source (["infores:monarchinitiative"])
    * primary_knowledge_source

__**Possible Additional Gene to Gene Ontology Term Association?**__

* **biolink:GeneToGoTermAssociation**:
    * id (random uuid)
    * subject (gene.id)
    * predicate (related_to)
    * object (go_term.id)
    * negated
    * has_evidence
    * publications
    * aggregating_knowledge_source (["infores:monarchinitiative"])
    * primary_knowledge_source

## Citation

Ashburner et al. Gene ontology: tool for the unification of biology. Nat Genet. 2000 May;25(1):25-9.  The Gene Ontology Consortium. The Gene Ontology knowledgebase in 2023. Genetics. 2023 May 4;224(1):iyad031

---

> This project was generated using [monarch-initiative/cookiecutter-monarch-ingest](https://github.com/monarch-initiative/cookiecutter-monarch-ingest).  
> Keep this project up to date using cruft by occasionally running in the project directory:
>
> ```bash
> cruft update
> ```
>
> For more information, see the [cruft documentation](https://cruft.github.io/cruft/#updating-a-project)

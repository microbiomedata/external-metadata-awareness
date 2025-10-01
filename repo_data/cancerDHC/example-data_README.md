# Example data for the CCDH project

[![nbviewer](https://raw.githubusercontent.com/jupyter/design/master/logos/Badges/nbviewer_badge.svg)](https://nbviewer.jupyter.org/github/cancerDHC/example-data/)

This repository is intended to act as a store of example data files from across
the [NCI Cancer Research Data Commons](https://datascience.cancer.gov/data-commons)
nodes in a number of formats. Each directory represents a single dataset downloaded
from a node, and contains a [Jupyter Notebook](https://jupyter.org/) documenting how
they were downloaded. [CCDH](https://datacommons.cancer.gov/center-cancer-data-harmonization)
will use this example data to build and test the CRDC-H data model.

## GDC Head and Mouth Dataset and conversion to CRDC-H

[Our first example](https://nbviewer.jupyter.org/github/cancerDHC/example-data/blob/main/GDC%20to%20CCDH%20conversion.ipynb) is based on a [dataset of 560 cases](./head-and-mouth/gdc-head-and-mouth.json) that we [downloaded from the GDC Public API](https://nbviewer.jupyter.org/github/cancerDHC/example-data/blob/main/head-and-mouth/Head%20and%20Mouth%20Cancer%20Datasets.ipynb). In a Jupyter Notebook, we describe how we can load this data into Python Data Classes and then export it as YAML, JSON-LD or Turtle. This is not yet intended to be a comprehensive transform of all the retrieved GDC case, but to showcase the features made available through the Python Data Classes that are part of the [artifacts generated from the CRDC model](https://github.com/cancerDHC/ccdhmodel/). The [JSON-LD](./head-and-mouth/diagnoses.jsonld) and [Turtle](./head-and-mouth/diagnoses.ttl) exports of the data are also available.

This example is based on [CRDC-H model v1.0-pre1](https://github.com/cancerDHC/ccdhmodel/releases/tag/v1.0-pre1) of the CCDH model, which is included in this repository. We will continue to update this as the model develops, but may be out of sync with the latest version of the model until we have the time to update it.

## Using Jupyter Notebooks

Many of the processes in this repository are documented in
[Jupyter Notebook format](https://nbformat.readthedocs.io/) files,
which have an `.ipynb` extension. These files can be viewed directly in
GitHub (see
*[CDA example for subject 09CO022](./cptac2-subject-09CO022/CDA%20example%20for%20subject%2009CO022.ipynb)*
as an example). You can also run it in the [Jupyter Notebook viewer](https://nbviewer.jupyter.org/) (see
*[CDA example for subject 09CO022](https://nbviewer.jupyter.org/github/cancerDHC/example-data/blob/0a983991cbc274a7fbf3121aa8ae10047549fa1a/cptac2-subject-09CO022/CDA%20example%20for%20subject%2009CO022.ipynb)*
as an example).

If you would like to execute this file, you will need to
[install Jupyter Notebook](https://jupyter.org/install.html) (also available on [Homebrew for Mac](https://formulae.brew.sh/formula/jupyterlab#default)). You can then download
the `.ipynb` file and open it in Jupyter Notebook on your computer by running:

```bash
$ jupyter notebook cptac2-subject-09CO022/CDA\ example\ for\ subject\ 09CO022.ipynb
```

This repository uses [Poetry](https://python-poetry.org/) for dependency management.
You can therefore also [install Poetry](https://python-poetry.org/docs/#installation),
then run:

```bash
$ poetry install
$ poetry run jupyter notebook
```

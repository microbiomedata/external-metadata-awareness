### HPO survey analysis
A library for analyzing surveys using the HPO


#### What's Included?
- phenom: a python library with modules for querying monarch remote services, working with ontologies,
and performing semantic similarity and distance computations
- Jupyter notebooks demoing various tasks
- Scripts for generating synthetic patient data, clustering, and evaluation

#### Getting Started

##### virtualenv

    virtualenv venv -p /usr/bin/python3.7
    source venv/bin/activate
    pip install -r requirements.txt
    export PYTHONPATH=.:$PYTHONPATH


##### Running notebooks with docker

    docker build . --tag hpo-subset:latest
    docker run --rm -it -p 8888:8888 --hostname localhost -v $PWD/notebooks/:/hpo-subset/notebooks/ hpo-subset jupyter notebook notebooks --ip=0.0.0.0 --allow-root --no-browser
    Copy the URL and replace "(localhost or 127.0.0.1)" with either "localhost" or "127.0.0.1" (without quotes)


#### Features
- Implementations of common semantic similarity algorithms
- Disease and/or phenotype class enrichment (fisher exact)
- Clustering phenotype profiles
- Utilities for generating derived profiles from hpo rare disease annotations
- Simulate patient data


#### Example Surveys of Interest
- Phenotypr: http://body.phenotypr.com/phenotypr/
- GenomeConnect: https://www.genomeconnect.org/

# Monarch OLS

# WARNING THIS REPO IS NO LONGER USED, NOR UPDATED

See https://github.com/monarch-initiative/ontotools-docker instead.

This repository contains the configuration of a bespoke Ontology Lookup Service for the Monarch Initiative. 

### To launch local in [OLS](https://www.ebi.ac.uk/ols/index) via [Docker](https://www.docker.com/)

```
make docker-build
make docker-run
```

OLS should now be running at http://localhost:8080


## Monarch Internal Documentation:

An overview of the process can be found [here](https://docs.google.com/presentation/d/1jYUHItpTRja1GVYbN3UBtajhr0WYG2atZexQGRx-9z4/edit?usp=sharing)

There are 2 relevant Jenkins jobs:
* [build-monarch-ols](https://ci.monarchinitiative.org/view/docker/job/build-monarch-ols) is responsible for preprocessing the ontologies, building the OLS docker image and publishing it to dockerhub.
* [deploy-ols-m2](https://ci.monarchinitiative.org/view/docker/job/deploy-ols-m2/) is responsible for pulling the latest monarch ols image from [dockerhub](docker pull monarchinitiative/monarch-ols) and deploying it on monarch2.

As an aside:
* [hpo-pipeline-dev2](https://ci.monarchinitiative.org/view/pipelines/job/hpo-pipeline-dev2/) is responsible for generating the HPO daily snapshot.


## Adding an ontology:

1. Add ontology metadata to ols/ols-config.yaml
1. Add ontology id to Makefile

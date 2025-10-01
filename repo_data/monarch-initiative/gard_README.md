# GARD Ingest
Ingestion of GARD into OWL and SemanticSQL.

## Prerequisites
Python is a dev dependency. It's not needed to run the docker containers, but needed for local development situations 
/ debugging.
1. Python 3.9+
2. Docker
3. Docker images  
  One or both of the following, depending on if you want to run the stable build `latest` or `dev`:
    - a. `docker pull obolibrary/odkfull:latest`
    - b. `docker pull obolibrary/odkfull:dev`

## Installation
Run: `sh run.sh make install`

## Running
Run: `sh run.sh make all`

You may also periodically want to update the input files, which can be done via `sh run.sh make update-inputs`.

# ICD11 Foundation Ingest

## Pre-reqs
- Docker
- Docker images  
  One or both of the following, depending on if you want to run the stable build `latest` or `dev`:
  - a. `docker pull obolibrary/odkfull:latest`
  - b. `docker pull obolibrary/odkfull:dev`

## Local development setup
`pip install -r requirements.txt`

## Running
`sh run.sh make all`

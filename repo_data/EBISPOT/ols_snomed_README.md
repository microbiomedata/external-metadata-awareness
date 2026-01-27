# SNOMED CT International Edition - OLS

This repository contains the configuration of an instance of the Ontology Lookup Service (OLS) loaded with SNOMED CT. 

### To launch local in [OLS](https://www.ebi.ac.uk/ols/index) via [Docker](https://www.docker.com/)

```
make docker-build
docker run -p 8080:8080 -t ebispot/ols-snomed
```

OLS should now be running at http://localhost:8080

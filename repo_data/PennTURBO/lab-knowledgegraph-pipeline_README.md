[![Pipeline CI](https://github.com/PennTURBO/lab-knowledgegraph-pipeline/actions/workflows/python-package.yml/badge.svg?branch=main)](https://github.com/PennTURBO/lab-knowledgegraph-pipeline/actions/workflows/python-package.yml) [![Coverage](https://github.com/PennTURBO/lab-knowledgegraph-pipeline/blob/badges/.badges/main/coverage.svg)](https://github.com/PennTURBO/lab-knowledgegraph-pipeline/actions/workflows/python-package.yml)


# TURBO Lab Knowledge Graph Pipeline

## Key Files

* *app.py* High level application code. 
* *ehr2rdf.py*
* *queries.sql*
* *labs.json*
* *Dockerfile*
* *docker-compose.yml*

## Current output:

Single example:

Input
```
[
    {
        "obi"       : "OBI_0000418",
        "loinc"     : "2345-7"     ,
        "skos"      : "exactMatch" ,
        "obo"       : "CHEBI_17234",
        "obo_label" : "glucose",
        "wild_card" : "both"
    }
]
```

Output
```
@prefix loinc: <https://loinc.org/> .
@prefix obo: <http://purl.obolibrary.org/obo/> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix turbo: <http://graphBuilder.org/> .

turbo:CaboodleLabComponentLOINC-basedMapping a turbo:LOINC-basedMapping .

turbo:CaboodleLabComponentNameLOINC-labelMapping_1 a turbo:CaboodleLabComponentNameLOINC-labelMapping ;
    turbo:basedOnOBIMeasurand obo:CHEBI_17234 ;
    turbo:basedOnOBIMeasurandLabel "glucose" ;
    turbo:hasCaboodleLabComponent turbo:CaboodleLabComponent_7903,
        turbo:CaboodleLabComponent_8653 ;
    turbo:hasLoincCode loinc:2345-7 ;
    turbo:hasOBIassay obo:OBI_0000418 .

turbo:CaboodleLabComponentNameOBOlabel-basedMapping a turbo:OBOlabel-basedMapping .

turbo:CaboodleLabComponentNameOBOsynonym-basedMapping a turbo:OBOsynonym-basedMapping .

turbo:CaboodleLabComponentNameLOINC-labelMapping a turbo:LOINC-labelMapping .

turbo:CaboodleLabComponent_7903 a turbo:CaboodleLabComponent ;
    turbo:hasLabComponentCommonName "GLUCOSE" .

turbo:CaboodleLabComponent_8653 a turbo:CaboodleLabComponent ;
    turbo:hasLabComponentCommonName "GLUCOSE" .

turbo:LOINC-basedMapping a turbo:LabTestMapping .

turbo:LOINC-labelMapping a turbo:LabTestMapping .

turbo:OBOlabel-basedMapping a turbo:LabTestMapping .

turbo:OBOsynonym-basedMapping a turbo:LabTestMapping .

obo:OBI_0000418 skos:exactMatch loinc:2345-7 .

```


Synonym example
Note json includes loinc but this is unused for synonyms

Input
```
    {   "obi"       : "OBI_2100133",
        "loinc"     : "2823-3"     ,
        "skos"      : "closeMatch" ,
        "obo"       : "CHEBI_29103",
        "obo_label" : "potassium(1+)",
        "wild_card" : "both",
        "synonym" : "potassium",
        "GOsynonymType" : "hasBroadSynonym",
  "_comment" : "actual label is potassium(1+)"
    }
```

Output
```
@prefix go: <http://www.geneontology.org/formats/oboInOwl#> .
@prefix loinc: <https://loinc.org/> .
@prefix obo: <http://purl.obolibrary.org/obo/> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix turbo: <http://graphBuilder.org/> .

turbo:CaboodleLabComponentLOINC-basedMapping a turbo:LOINC-basedMapping .

turbo:CaboodleLabComponentNameLOINC-labelMapping_1 a turbo:CaboodleLabComponentNameLOINC-labelMapping ;
    turbo:basedOnOBIMeasurand obo:CHEBI_29103 ;
    turbo:basedOnOBIMeasurandLabel "potassium(1+)" ;
    turbo:hasLoincCode loinc:2823-3 ;
    turbo:hasOBIassay obo:OBI_2100133 .

turbo:CaboodleLabComponentNameOBOlabel-basedMapping a turbo:OBOlabel-basedMapping .

turbo:CaboodleLabComponentNameOBOsynonym-basedMapping_2 a turbo:CaboodleLabComponentNameOBOsynonym-basedMapping ;
    turbo:basedOnOBIMeasurand obo:CHEBI_29103 ;
    turbo:basedOnOBIMeasurandSynonym "potassium" ;
    turbo:hasCaboodleLabComponent turbo:CaboodleLabComponent_625,
        turbo:CaboodleLabComponent_626 ;
    turbo:hasOBIassay obo:OBI_2100133 .

turbo:CaboodleLabComponentNameLOINC-labelMapping a turbo:LOINC-labelMapping .

turbo:CaboodleLabComponentNameOBOsynonym-basedMapping a turbo:OBOsynonym-basedMapping .

turbo:CaboodleLabComponent_625 a turbo:CaboodleLabComponent ;
    turbo:hasLabComponentCommonName "POTASSIUM URINE" .

turbo:CaboodleLabComponent_626 a turbo:CaboodleLabComponent ;
    turbo:hasLabComponentCommonName "URINE 24 HOUR POTASSIUM" .

turbo:LOINC-basedMapping a turbo:LabTestMapping .

turbo:LOINC-labelMapping a turbo:LabTestMapping .

turbo:OBOlabel-basedMapping a turbo:LabTestMapping .

turbo:OBOsynonym-basedMapping a turbo:LabTestMapping .

obo:CHEBI_29103 go:hasBroadSynonym "potassium" .

obo:OBI_2100133 skos:closeMatch loinc:2823-3 .
```

Synonym example without LOINC in JSON
Note json does not include loinc but this is unused for synonyms

Input
```
[
  {   "obi"       : "OBI_2100002",
      "obo"       : "CHEBI_29101",
      "obo_label" : "sodium(1+)",
      "wild_card" : "both",
      "synonym" : "sodium",
      "GOsynonymType" : "hasBroadSynonym"
   }
]
```

Output
```
@prefix go: <http://www.geneontology.org/formats/oboInOwl#> .
@prefix obo: <http://purl.obolibrary.org/obo/> .
@prefix turbo: <http://graphBuilder.org/> .

turbo:CaboodleLabComponentLOINC-basedMapping a turbo:LOINC-basedMapping .

turbo:CaboodleLabComponentNameLOINC-labelMapping a turbo:LOINC-labelMapping .

turbo:CaboodleLabComponentNameOBOlabel-basedMapping_1 a turbo:CaboodleLabComponentNameOBOlabel-basedMapping ;
    turbo:basedOnOBIMeasurand obo:CHEBI_29101 ;
    turbo:basedOnOBIMeasurandLabel "sodium(1+)" ;
    turbo:hasOBIassay obo:OBI_2100002 .

turbo:CaboodleLabComponentNameOBOsynonym-basedMapping_2 a turbo:CaboodleLabComponentNameOBOsynonym-basedMapping ;
    turbo:basedOnOBIMeasurand obo:CHEBI_29101 ;
    turbo:basedOnOBIMeasurandSynonym "sodium" ;
    turbo:hasCaboodleLabComponent turbo:CaboodleLabComponent_380,
        turbo:CaboodleLabComponent_46 ;
    turbo:hasOBIassay obo:OBI_2100002 .

turbo:CaboodleLabComponentNameOBOlabel-basedMapping a turbo:OBOlabel-basedMapping .

turbo:CaboodleLabComponentNameOBOsynonym-basedMapping a turbo:OBOsynonym-basedMapping .

turbo:CaboodleLabComponent_380 a turbo:CaboodleLabComponent ;
    turbo:hasLabComponentCommonName "SODIUM ACID URATE" .

turbo:CaboodleLabComponent_46 a turbo:CaboodleLabComponent ;
    turbo:hasLabComponentCommonName "TXP DD SODIUM" .

turbo:LOINC-basedMapping a turbo:LabTestMapping .

turbo:LOINC-labelMapping a turbo:LabTestMapping .

turbo:OBOlabel-basedMapping a turbo:LabTestMapping .

turbo:OBOsynonym-basedMapping a turbo:LabTestMapping .

obo:CHEBI_29101 go:hasBroadSynonym "sodium" .
```

## Instructions to run

Edit .env-template and save as .env.

Connect to VPN

docker-compose build

docker-compose up

## Tests

### Unit Test Runner
Unit tests can be run from `docker-compose-unit.yml`:

```
docker-compose -f docker-compose-unit.yml up
```

### Integration Test Runner
The integraton tests can be run from `docker-compose-integration.yml`. This will start up a Postgres container populated with test data and a test runner container.
```
docker-compose -f .\docker-compose-integration.yml up --abort-on-container-exit
```
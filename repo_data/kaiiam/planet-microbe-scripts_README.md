# Planet Microbe Scripts

This repository contains scripts and example mapping tables for generating Frictionless 
Data tabular data package schemas and loading data packages into the Postgres database.

## Creating Data Package Templates

This command generates a tabular data package JSON template for the OSD data set: 
```
cat example_ontology_mappings/OSD.tsv | ./scripts/schema_tsv_to_json.py > example_data_packages/osd/datapackage.json
```

The JSON was then hand-edited to add missing information and correct names, types, and units.

For more information on FD Table Schemas see http://frictionlessdata.io/specs/table-schema/ 

## Validating Data Packages

Make sure you have a Python 3 virtual environment setup:
```
virtualenv -p $(which python3) python3
source python3/bin/activate
pip install datapackage 
```

Alternatively create a conda environment:
```
conda create --name planet_microbe
conda activate planet_microbe
conda install -c conda-forge datapackage
```

Run the validation script:
```
scripts/validate_datapackage.py [-r resource] <path_to_datapackage.json>
```

## Loading Data Packages

Make sure you have a database and schema:
```
createdb planetmicrobe -U planetmicrobe
psql -d planetmicrobe -U postgres -c "CREATE EXTENSION postgis;"
psql -d planetmicrobe -U planetmicrobe -f scripts/postgres.sql
```

Install Data Packages:
```
git clone git@github.com:hurwitzlab/planet-microbe-datapackages.git ..
```

Create Python virtual environment:
```
virtualenv -p $(which python3) python3
source python3/bin/activate
pip install simplejson datapackage psycopg2 shapely pint biopython
```

Run the load script:
```
scripts/load_datapackage_postgres2.py -d planetmicrobe -u planetmicrobe -p <password> <path_to_datapackage.json> 
```

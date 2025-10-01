This repository holds the scripts and programs used in the Intonate project for transforming deidentified ehr data from Penn specific schemas (the cohort of patients in the ms registry will have a different schema from the cohort of patients not in the ms schema) to a schema that can be consumed by the Apheris node (currently a custom intonate cdm, in the future this may be OMOP).

The etl scripts are currently being written using the [DBT](https://www.getdbt.com) tool, based on mappings being done with the [Rabbit-in-a-Hat](https://www.ohdsi.org/software-tools/) tool.


etl pileline folder naming convention:
   - etl-"souce schema"-"destination schema" 

### Directory Overview:

- **etl-registry_cohort-intonate_cdm** - Contains DBT etl scripts and supporting rabbit-in-a-hat mappings to transform the Penn cohort of patients in the ms registry to the intonate CDM.
- **etl-phase2_cohort-intonate_cdm** - Contains DBT etl scripts for the phase 2 data, which includes registry and non-registry patients.
- **etl-cdm_data_export** - Program for transforming a database in CDM format to csv files ready to be uploaded to the Apharis node. Also produces supplemntary QC reports. Provided by the Roche team, original source created by the hyve for the Intonate project [here](https://github.com/thehyve/INTONATE-data-export).
- **utility** - Contains helper scripts and programs.

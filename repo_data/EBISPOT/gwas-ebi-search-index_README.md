# GWAS<>EBI Search Index

Description: 
This script creates a JSON file containing data on studies in the GWAS Catalog. This file is the source of GWAS data added into the EBI Search Index. Any Covid related studies, based on EFO annotation, are then also added to the Covid Data Portal. 
For more details on running this script, see [GWAS EBI Search Index](https://www.ebi.ac.uk/seqdb/confluence/display/GOCI/EBI+Search+Index+Script)

Usage: 
`./wrapper.sh -d DATABASE_ALIAS -o DATA_DIRECTORY -l ./logs/ -e EMAIL_RECIPIENT`

Dependencies:
This script uses dependencies maintained within the "gwas-utils" virtual environment. For making updates and testing, this virtual environment can be sourced following the information found on the [GWAS EBI Search Index](https://www.ebi.ac.uk/seqdb/confluence/display/GOCI/EBI+Search+Index+Script) Confluence page.


This script is run during the Data Release "GWAS Data File Export" stage. The EBI Search Index maintainers automatically load new data from this script when it is generated.
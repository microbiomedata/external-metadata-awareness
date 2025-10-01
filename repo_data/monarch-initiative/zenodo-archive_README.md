# Zenodo Archive

This repository contains some simple Python code for interacting with the Zenodo API.
Key functionality includes:  
- Creating a deposit with certain metadata
- Uploading files to the deposit
- ? Publishing the deposit to Zenodo

### Overview - Archiving Monarch Initiative Data

1. Download data from GCS and compress to single files:
```
mkdir monarch-latest
gsutil -m cp -r gs://data-public-monarchingest/latest/* monarch-latest
tar -czvf monarch-latest.tar.gz monarch-latest

mkdir hpo-latest
gsutil -m cp -r gs://data-public-monarchingest/hpo/* hpo-latest
tar -czvf hpo-latest.tar.gz hpo-latest

mkdir upheno2-latest
gsutil -m cp -r gs://data-public-monarchingest/upheno2/* upheno2-latest
tar -czvf upheno2-latest.tar.gz upheno2-latest
```
1. Create Zenodo deposit for each tar.gz

1. Upload file to deposit 

1. Confirm files/metata and publish deposit
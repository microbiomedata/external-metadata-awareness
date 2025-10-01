# Equiv

This is the repo for the identifier equivalency tool needed for Data Commons Helium A1.M2.T1, but will likely be used in Monarch as well. 

## Key Assumptions

This tool measures equivalency of data sets that have been returned as query results.

We are starting with TopMED, GTEx, and AGR.

All three of these data sets will be mapped to DATS.

Search results will be presented in JSON

## Data Set Notes

TopMED: integration of whole-genome sequencing (WGS) and other –omics (e.g., metabolic profiles, protein and RNA expression patterns) data with molecular, behavioral, imaging, environmental, and clinical data.

GTEx: gene expressions in tissues

AGR: Go and model organism databases

## File Descriptions

search_results.json

This is the "made up" example data. The user searched commons using "lung tissue" and got back three results, one from each of the three data sets mentioned above.

search_results_1.json

This is DATS metadata created by Team Sodium for some TopMED data files.

service.py

This is the code that takes as input the search results and give as output a list of tuples. Each tuple represents a relationship between two data sets, either "equivalent" or "related".

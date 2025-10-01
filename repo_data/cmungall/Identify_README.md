This project aims to augment metadata for a particular sample. It uses the MODIS and DAYMET API's available from the ORNL DACC
https://daac.ornl.gov/

To run, clone the repo into a directory. pip install required packages.   Command line arguments required:
1. path to input file
2. Cutoff for for geospatial precision. Example usage:

python identify.py Point_layer_0_only_1_row.csv 2




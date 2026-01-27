# uniprot2s3

This repository performs the API calls necessary to download Uniprot data to s3. 

## Microbial subset from kg-microbe

The first step will download the `exclusion_branches.tsv` and `ncbitaxon_removed_subset.json` to the `data/raw` directory. The `ncbitaxon_removed_subset.json` file is used to query only the set of microbes from the kg-microbe repository in UniProt. 

To run, execute the `make all` command.

## Human only subset

Switch to the `human_query` branch, and execute the `make uniprot-download` command. 

## Custom subset of organisms

Switch to the `build_custom_microbial_sets` branch. Upload a txt file containing all NCBITaxon IDs in the desired subset to the `data/raw` directory (an example called `wallen_etal_microbes.txt` is saved). If the name is changed, update the ORGANISM_RESOURCE variable in main.py to the correct filename. 

To run, execute the `make uniprot-download` command.

# Acknowledgements

This [cookiecutter](https://cookiecutter.readthedocs.io/en/stable/README.html) project was developed from the [monarch-project-template](https://github.com/monarch-initiative/monarch-project-template) template and will be kept up-to-date using [cruft](https://cruft.github.io/cruft/).

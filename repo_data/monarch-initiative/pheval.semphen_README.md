# pheval_semphen

semsimian + phenio.db for phenopacket disease prioritization<br>
Example of how to run using pheval<br>
 - Download http://data.monarchinitiative.org/monarch-kg/latest/phenio.db.gz<br>
 - Edit config file located in test_configs so that the path_to_phenio references the path to the file we just downloaded
 - pheval run -i test_configs/ -t path/to/phenopackets/ -r "semphenphevalrunner" -o test_output/
<br><br>

Example of how to run just using python executable<br>
 - Download http://data.monarchinitiative.org/monarch-kg/latest/phenio.db.gz<br>
 - python src/pheval_semphen/semphen.py -i path/to/phenopacket(s) -o path/to/results/directory -p path/to/phenio.db file

# Acknowledgements

This [cookiecutter](https://cookiecutter.readthedocs.io/en/stable/README.html) project was developed from the [monarch-project-template](https://github.com/monarch-initiative/monarch-project-template) template and will be kept up-to-date using [cruft](https://cruft.github.io/cruft/).

# pheval_kghg

monarch knowledge graph phenotype<-->disease nodes and edges + hyper geometric tests for phenopacket disease prioritization<br>
Example of how to run using pheval<br>
 - Download and upack monarch knowledge graph https://data.monarchinitiative.org/monarch-kg/latest/monarch-kg.tar.gz
 - Edit config file located in test_configs so that the path_to_nodes and path_to_edges fields reference the path to the monarch kg nodes and edges files respectively
 - pheval run -i test_configs/ -t path/to/phenopackets/ -r "kghgphevalrunner" -o test_output/
<br><br>

Example of how to run just using python executable (or pip installed executable)<br>
 - Download and upack monarch knowledge graph https://data.monarchinitiative.org/monarch-kg/latest/monarch-kg.tar.gz
 - python src/pheval_kghg/kghg.py -i path/to/phenopacket(s) -o path/to/results/directory -n path/to/monarch-kg_nodes.tsv -e path/to/monarch-kg_edges.tsv
 - pheval-kghg rank-associations -i path/to/phenopacket(s) -o path/to/results/directory -n path/to/monarch-kg_nodes.tsv -e path/to/monarch-kg_edges.tsv

# Acknowledgements

This [cookiecutter](https://cookiecutter.readthedocs.io/en/stable/README.html) project was developed from the [monarch-project-template](https://github.com/monarch-initiative/monarch-project-template) template and will be kept up-to-date using [cruft](https://cruft.github.io/cruft/).

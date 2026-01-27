This repository contains the code and files accompanying a paper submission to SWAT4LS 2016, http://ceur-ws.org/Vol-1795/paper23.pdf

A news article from EBI metagenomics is available at http://www.ebi.ac.uk/about/news/service-news/metagenomics-go-slim-2016

This code allows semi-automated generation of Gene Ontology (GO) slims, by using as input a list of GO terms and their associated count in an existing dataset. It then allows to visualize them in the GO hierarchy, thereby facilitating selection of appropriate GO terms for slim by data owners/domain experts.

After the GO slims terms have been selected, a script is run to validate which annotations would be inclued or lost with those terms. Finally, a mapper script built on map2slim allows to pass the original input file of GO terms ID and will return their projection onto GO slims terms.

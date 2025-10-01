# Monarch Data Boutique
In the Monarch Initiative project, we often come across small, highly-specific data sources that house interesting 
phenotypic data related to animal models of disease, that may require some additional 
curation to better integrate into the Monarch suite of genotype-phenotype data.
With this additional structured data, we will be able to computationally link more
sources together, for a broader representation of animal models of disease.

This repository houses Monarch-curated data, that which our team has curated directly. (It is exclusive of the disease-phenotype
associations found in [hpo-annotation-data](https://github.com/monarch-initiative/hpo-annotation-data)).  

## License
These datasets are under the [CC-BY 4.0](http://creativecommons.org/licenses/by/4.0/) License, and are bound by a date of data embargo from first deposition.  There, this data is freely available for your use and re-use, but we ask you to refrain from publishing using the data until 6-months from date of initial deposition unless you consult with our team first. Please contact info@monarchinitiative.org with questions.

## Datasets
The curated data is grouped into datasets that are curated distinctly from one another. The following is a description of each.
### OMIA disease-phenotype data
* The OMIA resource curates gene and breed-disease associations, as well as captures free-text phenotype information for each disease.  We have taken these descriptions and annotated the diseases with phenotypic features using the [Uberon](http://uberon.org), [Uberpheno](https://github.com/obophenotype/upheno), [Mammalian Phenotype] (https://github.com/obophenotype/mammalian-phenotype-ontology), and [Human Phenotype] (https://github.com/obophenotype/human-phenotype-ontology/issues), and [Bio Attribute](https://github.com/obophenotype/bio-attribute-ontology) ontologies. 
* This data was captured using the [Phenote](http://www.phenote.org/) curation tool, using the configuration as indicated in the [OMIA-disease-phenotype/omia_phenotypes.cfg](https://github.com/monarch-initiative/data-boutique/blob/master/OMIA-disease-phenotype/omia_phenotypes.cfg).
* We would encourage your own annotations be deposited here; please contact us if you would like to contribute additional animal-disease-phenotype associtations. 

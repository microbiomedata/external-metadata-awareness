Type 2 Diabetes Mellitus - DIAB Ontology
========================================

### About DIAB

The Type2Diabetes (T2D) Ontology (DIAB) was developed as part of the [BioMedBridges](http://www.biomedbridges.eu/) WP7-Phenobridge that aims to bridge the gap between the phenotype information available from mouse model studies and from human clinical data in the field of obesity and diabetes, enabling a new level of interspecies analysis of disease datasets. DIAB ontologically reuses classes from the [Human Phenotype Ontology (HP)](http://human-phenotype-ontology.github.io/), and [Mammalian Phenotype Ontology (MP)](http://www.informatics.jax.org/searches/MP_form.shtml), and creates complimentary classes under DIAB namespace to appropriately represent the T2D disease-phenotype associations with [OBAN](https://github.com/EBISPOT/OBAN) association model.

# 



![](https://github.com/EBISPOT/T2D/blob/master/img/overview_DIAB.png)




### DIAB Construction

DIAB describes T2D in relations to its disease stages and phenotypes, retrieving the candidate class relations from published literature. Text mining in this process is accomplished by Europe PMC [*Whatizit* pipeline](http://www.ebi.ac.uk/webservices/whatizit/info.jsf), aided by a phenotype dictionary composed of terms from the [Human Phenotype Ontology (HP)](http://human-phenotype-ontology.github.io/), and [Mammalian Phenotype Ontology (MP)](http://www.informatics.jax.org/searches/MP_form.shtml). The journals of interest by MeSH headings associated with T2D are mined for candidate phenotypes that are linked to T2D. Type 1 Diabetes Mellitus appears in the ontology even though DIAB is a T2D-focused ontology as some phenotypes are common to both types, creating a linkage in the ontology. The candidate phenotypes are manually verified by expert clinicians before getting asserted programmatically into DIAB with the [OWL API](http://owlapi.sourceforge.net/). Summary of this process is provided in the diagram below.

![](https://github.com/EBISPOT/T2D/blob/master/img/process_DIAB.png)

The core [DIAB ontology](https://github.com/EBISPOT/T2D/blob/master/ontology/Diabetes_Ontology_V33.owl) represents the general T2D's association to the phenotypes via *cause of* and *symptom of*. However, the knowledgebase of disease having phenotype is specific to the clinical evidence in different studies. This presents a challenge of ontological knowledge representation that is attached to probability. The DIAB disease-phenotype association is modeled by the [Ontology of Biomedical Annotation (OBAN)](https://github.com/EBISPOT/OBAN) in this study. The T2D disease-phenotype knowledgebase can be downloaded from [here](https://github.com/EBISPOT/T2D/tree/master/ontology).


### Publications

* Drashtti Vasant, Frauke Neff, Philipp Gormanns, Nathalie Conte, Andreas Fritsche, Harald Staiger, Jee-Hyub Kim, James Malone, Michael Raess, Matin Hrabe de Angelis, Peter Robinson, and Helen Parkinson ["DIAB: An Ontology for Type 2 Diabetes Stages and Associated Phenotypes"](http://phenoday2015.bio-lark.org/pdf/6.pdf)


### Accessibility
* [DIAB on Github](https://github.com/EBISPOT/T2D/)
* [DIAB on BioPortal](https://bioportal.bioontology.org/ontologies/DIAB)



### Contact us
Submit your questions via [T2D issue tracker](https://github.com/EBISPOT/T2D/issues)


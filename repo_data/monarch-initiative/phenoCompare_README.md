[![Codacy Badge](https://api.codacy.com/project/badge/Grade/6c8062374ad441b499011250c449e723)](https://www.codacy.com/app/peter.robinson/phenoCompare?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=monarch-initiative/phenoCompare&amp;utm_campaign=Badge_Grade)
# phenoCompare
Phenotype Compare

We start with a set of case records including HPO terms, and a list of GPI pathway genes labeled
early or late depending on which part of the pathway is affected by that gene. Patients are separated
into corresponding early and late groups according to which gene is responsible for disease in each
case. For each HPO term appearing in any patient record, the software counts the number of early and
late patients annotated with that term. These counts are propagated upward in the HPO hierarchy so that
a patient annotated with term T is included in the count for any term that subsumes T (is an ancestor
of T in the ontology). We calculate the chi-squared statistic to identify HPO terms whose prevalence is
significantly different between the early and late groups of patients. To be considered for hypothesis
testing, the HPO term must reach an expected value of at least 5 in each cell of its contingency table
(early/late patient group vs. has/does not have HPO term). We apply a Bonferroni correction for multiple
comparisons to achieve &alpha; &le; 0.05. This analysis covers not only those terms explicitly referenced in
case records, but also their supertypes referenced implicitly through the structure of the ontology.

phenoCompare has four command line arguments:<p>
-o&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;directory containing _hp.obo_ file<br>
-g&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_txt_ file containing lists of early, late GPI pathway genes<br>
-p&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;_tsv_ file of patient records<br>
-r&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;directory for result files<p>

example usage:
```
java -jar target/phenoCompare-1.0.0.jar \
> -o src/main/resources -g src/main/resources/gpiGenesTwoGroups.txt \
> -p src/main/resources/gpi_variants2018July06.tsv -r resultsTodaysDate
```
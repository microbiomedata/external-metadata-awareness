This a TEMPORARY repository for experimenting with a merge of the
diabetes subset of the Orphanet rare disease classification with DO.

Please see the commit history for an explanation of the steps
involved.

## Explanation of what we did

 * Made our own local copy of DO
 * Extracted the rare diabetes subset of Orphanet from EFO and added it to DO (HumanDOplus.obo)
 * Made a subset of the resulting ontology (diabetes-subset.owl)
 * added an import directive to HPO
 * Added has_phenotype associations between DOIDs and HPs to diabetes-subset.owl
 * Added has_secondary_complication associations between DOIDs and HPs to diabetes-subset.owl
 * Added new candidate HP terms in the DOCJM namespace (also in the diabetes-subset.owl file)

## Modeling

Disease-phenotype associations are made using relationships between
the DO class and HP class. These are OWL axioms of the form

  DISEASE SubClassOf has_phenotype some PHENOTYPE

Frequency data was added as axiom annotations using the has_frequency
property and an ad-hoc list of semi-controlled strings (Frequent,
Hallmark, Less fequent).

Note that this in not strictly in accord with OWL semantics - the
frequency metadata is invisible to OWL reasoners. This can create some
unusual scenarios in which a disease subclass "overrides" a child
disease subclass.

## Next steps

### Incorporation of rare genetic diabetes into DO

The DO editors can incorporate the rare disease terms directly. Open
question: mint new DO IDs or just keep the orphanet IDs as primary and
have a mixed IDspace ontology [causing problems with the current OLS]?
The EFO developers have experience merging the orphanet disease
hierarchy and can advise.

This should probably be thought of in the context of an overall plan
for merging orphanet and OMIM with DO, and will probably require DO
switching their edit version to OWL. For the short term it may simply
be easier to mint new DOIDs for the rare genetic diabetes and bring
them in.

### Incoporation of new phenotypes into HPO

We added some phenotypes in the DOCJM idspace in
diabetes-subset.owl. These are mostly simple subclasses/refinements of
existing HPO classes. These belong in the HPO.

### Incoporation of disease-phenotype associations into Phenotype commons

The typical workflow for OMIM and Orphanet diseases is to annotate
using Phenote, store the resulting tab delimited file in the phenotype
commons svn dir. These are later incorporated into the
disease-phenotype association files distributed from the HPO site.

It would be possible to automatically translate the OWL axioms to this
format, but it may be easier for Peter or someone to do this by hand
and review at the same time.

Again, longer term we may want to think of this in the context of an
OWL model of disease-phenotype associations that makes use of
frequency information.



 

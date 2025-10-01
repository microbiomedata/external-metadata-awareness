# OBO Design Pattern Coordination Effort

To harmonize ontologies across domains in the OBO Foundry we have started to employ design patterns to coordinate consistent logical axiomatisation through community discussion. The general idea is this: When a modelling problem is identified, for example we discover the need for representing `abnormally increased rate of a biological process somewhere in the body of an organism (phenotype)`, we propose a pattern that describes such an entity using a pattern, typically as a DOSDP template. This pattern is proposed to the community as a way to capture its essence, both in terms of terminological variation (synonyms, definition etc) and logically: which relations should be used in conjunction with this term? Which other entities? How are they related?

This is a concrete proposal for the example above:

```
pattern_name: abnormalRateOfBiologicalProcessInLocation
pattern_iri: http://purl.obolibrary.org/obo/upheno/patterns-dev/abnormalRateOfBiologicalProcessInLocation.yaml
description: "Changed rate of a biological process, i.e. changed number of events per unit time of a biological process, or changed output of a continuous biological process) in a location."

contributors:
  - https://orcid.org/0000-0001-9076-6015
  - https://orcid.org/0000-0002-3528-5267
  - https://orcid.org/0000-0002-6490-7723
  - https://orcid.org/0000-0002-7356-1779

classes:
  rate: PATO:0000161
  abnormal: PATO:0000460
  biological_process: GO:0008150
  independent continuant: BFO:0000004

relations:
  inheres_in: RO:0000052
  qualifier: RO:0002573
  has_part: BFO:0000051
  occurs_in: BFO:0000066

annotationProperties:
  exact_synonym: oio:hasExactSynonym

vars:
  biological_process: "'biological_process'"
  location: "'independent continuant'"
name:
  text: "changed %s rate in %s"
  vars:
  - biological_process
  - location

def:
  text: "Changed rate of %s in %s."
  vars:
  - biological_process
  - location

equivalentTo:
  text: "'has_part' some ('rate' and ('inheres_in' some (%s and ('occurs_in' some %s))) and ('qualifier' some 'abnormal'))"
  vars:
  - biological_process
  - location
``` 


Most importantly, we can see that the templates encodes the logical pattern recommended to represent entities of this kind (`equivalentTo`). Members of the community review this pattern and can "sign off" on the pattern by adding there id to the `contributors` field. 


While evolving design patterns in a particular domain, like phenotypes, biological processes, or environmental exposure is powerful and leads to a huge jump in consistency of representation, coordinating _between domains_ is still and open issue. For example, consider the phenotype template above. The so called "bearer" portion of the pattern, `(%s and ('occurs_in' some %s))`, involves a biological process connected to an anatomical entity (well, _any location_ in this case, but lets ignore that for now) using the `occurs_in` relation. When designing the pattern, the phenotype community went to take a look at how the relationship between biological processes and anatomical entities is modelled by _looking at GO_ - which defines patterns for this case. So far, trying to track patterns across ontologies is done on an ad-hoc basis (by simply looking) - while a more close - co-evolution of patterns is desirable. 

The OBO Design Pattern Coordination Effort (ODPCE) aims at reconciling and connecting design patterns across ontologies by 1) coordinating the definition of designing patterns across ontologies and domains by bringing together their respective experts, 2) developing appropriate tool support to ensure their consistent use and 3) providing an interface into the template and design pattern libraries used across ontologies. Furthermore, we will develop a set of best practices for the design of templates, recommendations around the appropriate formalisms and links to hands on tutorials.
 
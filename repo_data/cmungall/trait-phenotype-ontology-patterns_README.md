# Modelling patterns for trait and phenotype data

Phenotype data in the broad sense - observations about organisms in a lab or populations of organisms - are recorded/curated using a wide variety of different systems, for example:

- using terms from ontologies of phenotypic abnormalities, such as the Human Phenotype Ontology (HPO) or the Mammalian Phenotype Ontology (MPO)
- using terms from "trait" ontologies, such as the Vertebrate Trait Ontology or the Ontology of Biological Attributes (OBA)
- using terms from "measurement" ontologies such as the Experimental Factor Ontology (EFO), the Clinical Measurement Ontology (CMO) and the Ontology of Biomedical Investigations (OBI)
- using free text

The problem is aggrevated by the fact that there is no clear distinctions between phenotype, trait, measurement and similar terms, even within the various ontologies, which makes analysis across resources extremely difficult. Furthermore, specific resources, such as Monarch, MGI, IMPC, FlyBase or RGD may use terms and record them together with contextual modifiers that change their meaning - contextual information that no other source understands. This may be information such as `negation` (NOT "Abnormally Increased Tail Length"), `normalisation` (normal "Abnormally Increased Tail length") and `normal variation` ("Abnormally Increased Tail Length" as in "consistently increased tail length, but within normal range") to more complex contextual information such as `non-wild comparators` ("Abnormally Increased Tail Length" compared to control rather than wild) or `measurement protocols` ("We checked for Abnormally Increased Tail Length but didnt record the outcome").

The goal of this community effort is to reconcile our discussions on trait and phenotype modelling patterns, including quantitative (phenotypic) measurements. Specifically we set out to do the following:

1. Design a semantic modelling framework that enables the comparative analysis of phenotypic abnormalities ("Abnormally Increased Tail Length"), traits ("Tail Length"), and quantitative (phenotypic) measurements ("Tail Length of 4cm").
2. Specify a set of modelling patterns that can be used for phenotype, trait and measurement ontologies to logically define terms compatible with the proposed framework.
3. Specify a data-model compatible with phenopackets and biolinkml into which databases can map their data to become compatible with the proposed framework.

We are losely organised through bi-monthly meetings and discussions on this GitHub repostory. If you want to join the discussion, please open a ticket in the issue tracker.

## Current members of the effort:

| Name | Github | Institution | Role |
| ---- | ------- | ----------- | ----- |
| David Osumi-Sutherland | @dosumis | EMBL-EBI, Monarch Initiative | Coordinator, semantics specialist |
| Susan Bello | @sbello| JAX, MGI, Alliance of Genome Resources | Coordinator, ontology engineer, bio-curator |
| Nicolas Matentzoglu | @matentzn | EMBL-EBI, Monarch Initiative | Coordinator, semantic engineer |
| Anna Anagnostopoulos | @anna-anagnostop| JAX, MGI, Alliance of Genome Resources | ontology engineer, bio-curator |
| Nicole Vasilevsky | @nicolevasilevsky| OHSU, Monarch Initiative | ontology engineer, bio-curator |
| Leigh Carmody | @LCCarmody| JAX, Monarch Initiative | ontology engineer, bio-curator |
| Anna Anagnostopoulos | @anna-anagnostop| JAX, MGI, Alliance of Genome Resources | ontology engineer, bio-curator |
| Violeta Munoz Fuentes | @viomunoz | EMBL-EBI, IMPC | |
| Meghan Balk |  |  | |
| Jim Balhoff | @balhoff  |  | |
| Cari Park |  |  | |
| Elliot Sollis |  |  | |
| Elissa Chesler |  |  | |
| Jeremy Mason |  |  | |
| Kalliope Panoutsopoulou |  |  | |
| Laura Harris |  |  | |
| Randi Vita |  |  | |
| Zoe Pendlington |  |  | |
| Laura Harris |  |  | |
| Kent Shefchek |  |  | |
| Stan Laulederkind |  |  | |
| Jennifer Smith |  |  | |

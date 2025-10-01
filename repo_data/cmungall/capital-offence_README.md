# capital-offence

This project aims to find misuse of capitalization in OBO Ontologies.

Particularly:

 * use of capitalization where this is inappropriate
 * failure to capitalize (e.g. "purkinje cell" rather than "Purkinje cell")

This takes into account ontology-specific rules. E.g.

 * in HP, all terms have the initial word capitalized, so there is no signal in the capitalization state of the 1st letter
 * in DOID, synonyms are very heterogeneous, so these are ignored
 * OMIM uses SCREAMING CAPS. Some version of OMIM may auto-downcase (whilst retaining capitalization of each word). There is thus no signal here

To see an ongoing list of reports from this, see the linked tickets from here: https://github.com/cmungall/capital-offence/issues/1

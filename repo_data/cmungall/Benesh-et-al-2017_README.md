# Benesh-et-al-2017

Parasite host data from Benesh, D. P., Lafferty, K. D. and Kuris, A. (2017), A life cycle database for parasitic acanthocephalans, cestodes, and nematodes. Ecology, 98: 882. that will be made available in Global Biotic Interactions (GloBI, http://globalbioticinteractions.org).

## Data Format Explanation
The file [interactions.tsv](./interactions.tsv) is a suggestion on how to encode your interaction data using a tab separated file format (tsv) in combination with columns described below. This provides an example on how to capture your data in a human and machine friendly way and keep it relatively doable to update the file using a basic text editor. Other formats are supported, just let us know about the syntax, and we'll make it work.

term | example | description | 
--- | --- | ---
 sourceTaxonId | EOL:328583 | taxon classification id of originating organism in some taxon name authority
 sourceTaxonName | Enhydra lutris  | scientific name of taxon classification of originating organism 
 interactionTypeId | RO:0002470 | id of interaction as described by the [OBO Relations Ontology](https://code.google.com/p/obo-relations/)
 interactionTypeName | eats | human readable description of interactions
 targetTaxonId |  EOL:1971 | taxon classification id of originating organisms 
 targetTaxonName | Echinoidea | scientific name of taxon classification of target organism of interaction
 LocationinhostName | gut | location where the parasite is affecting the host
 localityId | GEONAMES:5391961 | reference to geo classification like geonames.org, gazetteer or other.
 localityName | San Francisco Bay, California, USA | human readable description of locale
 decimalLatitude | -41.0983423 | latitude of geographic center of interaction observation location http://rs.tdwg.org/dwc/terms/index.htm#decimalLatitude
 decimalLongitude | -121.1761111 | longtide of geographic center of interaction observation location http://rs.tdwg.org/dwc/terms/index.htm#decimalLongitude
 observationDateTime | 2014-11-18T06:37:04Z | [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) formatted date time string
 referenceSource  | Abdou. 1958. J. Parasitol. 44: 484-488 | Where the original information came from
 referenceDoi | doi:10.3354/dao002147 | Digital Object Id (DOI, http://doi.org) is commonly used to give papers, datasets or other digital object a permanent id
 referenceCitation| Jangoux, M. 1986 Diseases of Echinodermata. I. Agents microorganisms and protistans Diseases of Aquatic Organisms (Impact Factor: 1.59) 2:147-162. doi:10.3354/dao002147 | human readable reference 

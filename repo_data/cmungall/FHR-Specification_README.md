# FHR-Specification
FHR (<u>Fair</u> <u>H</u>eader <u>R</u>eference genome): a simple FAIR enough metadata structure for reference genomes that you can TRUST
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6762549.svg)](https://doi.org/10.5281/zenodo.6762549)

Part of what FHR sets off to do is make sure that we can map back to Schema.org as much as possible, this will be useful for microdata and rdfa conversions for users that want to embed data into genome webpages. We also want to be able to split out the header if we have to, we can make the coding easy on ourselves if we throw yaml into the header itself. or something that is a regex away from yaml. I think it's important that the header has a secondary character after the comment delineator to indicate that this is part of the header, otherwise a simple mistake in a regex for the header could easily grab regular comments in the fasta file. I also think that the secondary header delineating character should be on the keyboard, and not a yaml special character, this leaves the tilde as the best option. I could imagine it would look something like this:

_NOTE_: This is the FFRGS Specification Repo, if you would like to convert between data serialization, or validate your ffrgs instance, see [FHR-File-Converter](https://github.com/FAIR-bioHeaders/FHR-File-Converter)

```
;~schema: https://raw.githubusercontent.com/FAIR-bioHeaders/FHR-Specification/main/fhr.json
;~schemaVersion: 1
;~genome: Example species
;~genomeSynonym: eg. species
;~taxon:
;~  name: Example species
;~  uri: https://identifiers.org/taxonomy:0000
;~version: 0.0.1
;~metadataAuthor:
;~  name: Adam Wright
;~  uri: https://orcid.org/0000-0002-5719-4024
;~assembler:
;~  name: David Molik
;~  uri: https://orcid.org/0000-0003-3192-6538
;~dateCreated: '2022-03-21'
;~location:
;~  name: Cool Science Organization
;~  url: https://example.org/awesome_science/project-1024
;~instrument:
;~- Amazing Sequencer IIe
;~- Neato Sequencer
;~physicalSample: Located in Freezer 33, Drawer 137
;~scholarlyArticle: https://doi.org/10.1371/journal.pntd.0008755
;~documentation: 'Built assembly from... '
;~identifier:
;~- eg:1024512256128643216842
;~relatedLink:
;~- https://example.org/example-species/our_genome
;~funding: 'some'
;~licence: 'public domain'
;~checksum: md5:7582b26fcb0a9775b87c38f836e97c42
>Contig 1
AAAATCGATCGGCATA
.
.
.
``` 
 
## Metadata Draft v0.2 (fasta yaml header with easy microdata conversions)
FFRGS utilizes schema.org as much as possible for later integration

---
Specialised instances of Schema.org (we want as few of these as possible):
 
- `schemaVersion` (String) - Version of FFRGS (Currently always "1.0")
- `genome` (String) - ( Schema.org name )
- `version` (String) - ( Schema.org version ) Version of the Genome
- `license` (String) - ( Schema.org license ) License used (url or name of common license) 
- `funding` (String) - ( Schema.org funding ) Name of Grant used in the creation of the genome
 
These will always be remaps of properties, so:

``` 
Genome: <name>
```

---
Instances of Schema.org entities, where we just want a name and url because we’re not storing that data here: 
 
- `author` - ( Schema.org author ) (URL and String)
- `assembler` - creator of the genome ( Schema.org Person or Organisation ) (URL and String)
- `location` (URL) (Schema.org place)  (URL and String)
- `assemblySoftware` (Schema.org SoftwareApplication) (URL and String) [Optional]
- `physicalSample` (String) - ( Schema.org Thing ) (URL and String)

These will be names, and urls:

``` 
author: 
 name: Name
 url: https://link 
```

---
Direct use of Schema.org entities:
 
- `dateCreated` (DataTime) (Schema.org dateCreated) (date)
- `instrument` (Schema.org instrument) (URL or String) [Optional]
- `scholarlyArticle` (Schema.org ScholarlyArticle) (URL) [Optional]
- `documentation` (Schema.org documentation) (URL or String) [Optional]
- `identifier` (Schema.org identifier ) (String) [Optional]
- `relatedLink` (Schema.org relatedLink) (URL) [Optional]

``` 
These are all direct use:
 
- `dateCreated`: <date>
```

Another benefit of having this easy conversion is that we can submit the spec to say bioschema without much work after publishing. 


# NMDC External Metadata Awareness

## Background

NMDC brings unique value to environmental microbial research by

- emphasizing multi-omics experiments
- processing data with standardized workflows
- describing relevant material entities and processes with a LinkML schema

But NMDC is not the source of any of that data or metadata, and the NMDC schema is strongly influenced by external
standards and ontologies.

## High Level Goals

We have developed the NMDC schema to ensure that our metadata is FAIR, meaning that once a user has basic familiarity
with the Data Portal or our APIs, they should be able to retrieve metadata about study X as easily as the can retrieve
metadata about study Y. They should also be able to generate trustworthy summaries of the metadata across studies. None
of that should require any prior familiarly with any of those studies.

NMDC launched a Value Set Squad in August 2024 to formalize which ontology terms (especially from EnvO) are suitable for
populating MIxS' `env_broad_scale`, `env_local_scale` and `env_medium` fields, in the context of a particular MIxS
Extension (aka environment). See more below.

## Challenges

We haven't completely achieved that goal yet, which means that some NMDC team members need the ability to retrieve the
external metadata in their native form, analyze them systematically, and possibly integrate subsets of two or more
metadata sources. We also need the ability to compare these external metadata against the schemas that accompany them.

The interpretation of metadata can be especially challenging when the values that are allowed for a particular slot or
field come from some hierarchy in an ontology.

## Individual vs Collaborative Approaches

There is no shortage of expertise on our various metadata sources within NMDC. However, if person A asks their colleague
B about sme metadata, and B does some web searches followed by a mashup analysis on their laptop, then A (or someone
else) won't be in a better position to build on that in the future. That means that external metadata exploration
requires automation and the use of machine-readable file formats. This doesn't mean that B's web searching skills aren't
valuable. It just means that B and A are responsible for converting the successful web search strategy into something
that can be automated.

## How to Contribute

This repo uses the following technologies

- Linux/MacOS command line tools like `yq` and `runoak`
- Python scripts
- Makefiles, which show how the command line tools and Python scripts can be chained together to achieve a goal (usually
  a final output file)

Everyone is welcome to contribute to the Python scripts and Makefile targets, although that is not necessary

The greatest contribution that NMDC team member can make is to add value-added file to the `contributed` directory.
Ideally these files would be in a machine-readable format like TSV, CSV, YAML or JSON. Contributors who have XLSX files
or Google Sheets are asked to save them as TSV or CSV. Please be aware of any knowledge that is captured in a way that
would be lost upon conversion to TSV or CSV, like color coding or comments. See Mark for help.

### TSV vs CSV

Many LinkML related tools like `runoak` generate TSV output even when CSV is requested. However, many of the LLM web
interfaces will accept CSV uploads by reject TSV uploads. In a similar vein, YAML files are usually easier to read, but
LLMs are more likely to accept JSON files. This means that conversion between formats is a common task in the Makefiles.

### Role of LLMs

Large language models like ChatGPT can provide value insights about the metadata and their standards, but there are many
caveats about loading data and prompts into LLMs and about interpreting their output. NMDC team members are encouraged
to
experiment with LLMs for metadata and schema exploration, even if it is though a web interface. However, all use of LLMs
in this repo will be automated with the `llm` or `litellm` tools.

While many vendors provide a free tier for using their LLMs, those are usually not sufficient for NMDC metadata/schema
exploration tasks. That's partially due to the fact that the free tiers don't use the most advanced models, but also due
to the fact that the free (or even less expensive) models are more limited in the number of tokens (words or portions of
words) they will accept as input, and the number of tokens they will emit as a response.

https://artificialanalysis.ai/ provides a nice analysis of the available LLM vendors and models, along with some quality
metrics, token limits and pricing.

Your institution may provide some level of free access to the more advanced LLMs. Most BBOP team members have access to
a LBL-paid OpenAI/GPT account for API access (but not web access). LBL also provides the CBORG multi-model
interface https://cborg.lbl.gov/

The LLMs that Mark has found most useful are Anthropic Claude Sonnet 3.5 (200k tokens input), OpenAI GPT 4 and 4o (128k)
and Google Gemini 1.5 pro (2M).

The time and financial cost of developing LLM methods is not trivial, and there's no guarantee that the results will be
accurate, comprehensive or repeatable. In the long run, the best use of LLMs may be in interpreting input data in order
to
generate code that solves a problem algorithmically.

## Value set task

NMDC follows the MIxS practice of requiring Biosamples to be annotated with a triad of environmental context
fields, [env_broad_scale](https://genomicsstandardsconsortium.github.io/mixs/0000012/), [env_local_scale](https://genomicsstandardsconsortium.github.io/mixs/0000013/)
and [env_medium](https://genomicsstandardsconsortium.github.io/mixs/0000014/). The EnvO repo
provides general [guidance for using
EnvO terms to fill these fields](https://github.com/EnvironmentOntology/envo/wiki/Using-ENVO-with-MIxS) (and that
guidance is mirrored very closely by the descriptions of the MIxS fields
linked above).

For example, the guidance for `env_broad_scale` is to use an identifier for some subclass
of [biome](https://www.ebi.ac.uk/ols4/ontologies/envo/classes/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252FENVO_00000428).

But MIxS recognizes that Biosamples come from a wide variety of environments, which it models
as [Extensions](https://genomicsstandardsconsortium.github.io/mixs/#extensions). [mediterranean sea biome](https://www.ebi.ac.uk/ols4/ontologies/envo/classes/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252FENVO_01000047?lang=en)
and [broadleaf forest biome](https://www.ebi.ac.uk/ols4/ontologies/envo/classes/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252FENVO_01000197?lang=en)
are both subclasses of `biome`, but we **intuitively** wouldn't expect
a [Soil](https://genomicsstandardsconsortium.github.io/mixs/0016012/) sample to have a `env_broad_scale` annotation
of `mediterranean sea biome`, nor would we **intuitively** expect
a [Water](https://genomicsstandardsconsortium.github.io/mixs/0016014/) sample to have a `env_broad_scale` annotation
of `broadleaf forest biome`.

The problem here is that **intuition** shouldn't be required for either providing metadata about Biosamples, or for
searching over Biosample metadata. NMDC should take a stance on which ontology terms are appropriate for each
combination of a MIxS environmental context field and a MIxS Extension, and NMDC should provide metadata submission and
search tools that are aware of those per-Extension# NMDC External Metadata Awareness

## Background

NMDC brings unique value to environmental microbial research by

- emphasizing multi-omics experiments
- processing data with standardized workflows
- describing relevant material entities and processes with a LinkML schema

But NMDC is not the source of any of that data or metadata, and the NMDC schema is strongly influenced by external
standards and ontologies.

## High Level Goals

We have developed the NMDC schema to ensure that our metadata is FAIR, meaning that once a user has basic familiarity
with the Data Portal or our APIs, they should be able to retrieve metadata about study X as easily as the can retrieve
metadata about study Y. They should also be able to generate trustworthy summaries of the metadata across studies. None
of that should require any prior familiarly with any of those studies.

NMDC launched a Value Set Squad in August 2024 to formalize which ontology terms (especially from EnvO) are suitable for
populating MIxS' `env_broad_scale`, `env_local_scale` and `env_medium` fields, in the context of a particular MIxS
Extension (aka environment). See more below.

## Challenges

We haven't completely achieved that goal yet, which means that some NMDC team members need the ability to retrieve the
external metadata in their native form, analyze them systematically, and possibly integrate subsets of two or more
metadata sources. We also need the ability to compare these external metadata against the schemas that accompany them.

The interpretation of metadata can be especially challenging when the values that are allowed for a particular slot or
field come from some hierarchy in an ontology.

## Individual vs Collaborative Approaches

There is no shortage of expertise on our various metadata sources within NMDC. However, if person A asks their colleague
B about sme metadata, and B does some web searches followed by a mashup analysis on their laptop, then A (or someone
else) won't be in a better position to build on that in the future. That means that external metadata exploration
requires automation and the use of machine-readable file formats. This doesn't mean that B's web searching skills aren't
valuable. It just means that B and A are responsible for converting the successful web search strategy into something
that can be automated.

## How to Contribute

This repo uses the following technologies

- Linux/MacOS command line tools like `yq` and `runoak`
- Python scripts
- Makefiles, which show how the command line tools and Python scripts can be chained together to achieve a goal (usually
  a final output file)

Everyone is welcome to contribute to the Python scripts and Makefile targets, although that is not necessary

The greatest contribution that NMDC team member can make is to add value-added file to the `contributed` directory.
Ideally these files would be in a machine-readable format like TSV, CSV, YAML or JSON. Contributors who have XLSX files
or Google Sheets are asked to save them as TSV or CSV. Please be aware of any knowledge that is captured in a way that
would be lost upon conversion to TSV or CSV, like color coding or comments. See Mark for help.

### TSV vs CSV

Many LinkML related tools like `runoak` generate TSV output even when CSV is requested. However, many of the LLM web
interfaces will accept CSV uploads by reject TSV uploads. In a similar vein, YAML files are usually easier to read, but
LLMs are more likely to accept JSON files. This means that conversion between formats is a common task in the Makefiles.

### Role of LLMs

Large language models like ChatGPT can provide value insights about the metadata and their standards, but there are many
caveats about loading data and prompts into LLMs and about interpreting their output. NMDC team members are encouraged
to
experiment with LLMs for metadata and schema exploration, even if it is though a web interface. However, all use of LLMs
in this repo will be automated with the `llm` or `litellm` tools.

While many vendors provide a free tier for using their LLMs, those are usually not sufficient for NMDC metadata/schema
exploration tasks. That's partially due to the fact that the free tiers don't use the most advanced models, but also due
to the fact that the free (or even less expensive) models are more limited in the number of tokens (words or portions of
words) they will accept as input, and the number of tokens they will emit as a response.

https://artificialanalysis.ai/ provides a nice analysis of the available LLM vendors and models, along with some quality
metrics, token limits and pricing.

Your institution may provide some level of free access to the more advanced LLMs. Most BBOP team members have access to
a LBL-paid OpenAI/GPT account for API access (but not web access). LBL also provides the CBORG multi-model
interface https://cborg.lbl.gov/

The LLMs that Mark has found most useful are Anthropic Claude Sonnet 3.5 (200k tokens input), OpenAI GPT 4 and 4o (128k)
and Google Gemini 1.5 pro (2M).

The time and financial cost of developing LLM methods is not trivial, and there's no guarantee that the results will be
accurate, comprehensive or repeatable. In the long run, the best use of LLMs may be in interpreting input data in order
to
generate code that solves a problem algorithmically.

## Value set task

NMDC follows the MIxS practice of requiring Biosamples to be annotated with a triad of environmental context
fields, [env_broad_scale](https://genomicsstandardsconsortium.github.io/mixs/0000012/), [env_local_scale](https://genomicsstandardsconsortium.github.io/mixs/0000013/)
and [env_medium](https://genomicsstandardsconsortium.github.io/mixs/0000014/). The EnvO repo
provides general [guidance for using
EnvO terms to fill these fields](https://github.com/EnvironmentOntology/envo/wiki/Using-ENVO-with-MIxS) (and that
guidance is mirrored very closely by the descriptions of the MIxS fields
linked above).

For example, the guidance for `env_broad_scale` is to use an identifier for some subclass
of [biome](https://www.ebi.ac.uk/ols4/ontologies/envo/classes/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252FENVO_00000428).

But MIxS recognizes that Biosamples come from a wide variety of environments, which it models
as [Extensions](https://genomicsstandardsconsortium.github.io/mixs/#extensions). [mediterranean sea biome](https://www.ebi.ac.uk/ols4/ontologies/envo/classes/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252FENVO_01000047?lang=en)
and [broadleaf forest biome](https://www.ebi.ac.uk/ols4/ontologies/envo/classes/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252FENVO_01000197?lang=en)
are both subclasses of `biome`, but we **intuitively** wouldn't expect
a [Soil](https://genomicsstandardsconsortium.github.io/mixs/0016012/) sample to have a `env_broad_scale` annotation
of `mediterranean sea biome`, nor would we **intuitively** expect
a [Water](https://genomicsstandardsconsortium.github.io/mixs/0016014/) sample to have a `env_broad_scale` annotation
of `broadleaf forest biome`.

The problem here is that **intuition** shouldn't be required for either providing metadata about Biosamples, or for
searching over Biosample metadata. NMDC should provide pre-determined sets of ontology terms that are appropriate for
each combination of a MIxS environmental context field and a MIxS Extension, and NMDC should provide metadata submission
and search tools that are aware of those value sets. This repo is more concerned with creating appropriate value sets,
but some attention will be made to handing off the value sets or other rules off to the submission/search tools.

The construction of value sets is intended to support submitters in faithfully describing their Biosamples, even in the
context of innovative science, while also supporting data searchers. EnvO has a aquatic biome supercalss with 

## Implementation Questions

- Should the submission of ontology terms for these fields be absolutely limited to the value sets, or should a string
  pattern be allowed as a fallback?
    - If submitters provide a term outside of the value set, are they responsible for providing the term ID, the label
      or both?
    - If we are validating on a pattern only, and the ID and label don't match, how will be know which one the submitter
      really meant?
- Should any attempt be made to display the ontology term value sets in a hierarchical view? If so, and there are
  multiple paths from a term up to its root, should all of those paths be shown?

Note that this repo provides tooling for manually reviewing the ontology terms that have been associated with each NMDC
biosample.

## Requesting New Terms for the Value Set

In some cases it may be necessary to request new terms from EnvO (or another ontology) to reflect the true environmental
context

----

## resources to explore

https://www.ncbi.nlm.nih.gov/viewvc/v1/trunk/submit/public-docs/biosample/biosample.xsd?view=co # 8 years old. seems
very incomplete.

https://www.ncbi.nlm.nih.gov/viewvc/v1/trunk/submit/public-docs/bioproject/bioproject.xsd?view=co

* get specifications from EBI too, in addition to NCBI?
* get DATA from EBI/ENA?
* what data to mirror and possibly restructure here vs accessing via APIs?
* what other repos to share code/notes with?

## document the use of APIs here

* https://www.ebi.ac.uk/biosamples/samples/SAMEA104726483.json
* https://www.ebi.ac.uk/ena/browser/advanced-search
* https://www.ebi.ac.uk/ena/portal/api/swagger-ui/index.html
* https://www.ebi.ac.uk/ena/taxonomy/rest/swagger-ui/index.html

----

```shell
make load-biosamples-into-mongo
```

> 2024-08-13T19:00:28.052828: 40000, 0.1%
> 2024-08-13T19:00:57.346565: 80000, 0.2%
> 2024-08-13T19:01:34.743793: 120000, 0.3%
>
>2024-08-14T05:34:00.487742: 43104782, 107.8%
>
>Process finished with exit code 0

```shell
mongosh
```

```mongo
use biosamples

db.biosamples.estimatedDocumentCount()

biosamples> db.biosamples.countDocuments({})
```

> 40347716

```shell
grep -c "</BioSample>" local/biosample_set.xml
```

> 40347716

Ids have been saved as strings. There are probably some Booleans in there too that are expressed as integers as a
strings

```mongo
db.biosamples.createIndex({ accession: 1 })

db.collectionName.createIndex({ "Package.value": 1 })
```

```compass
{"Package.value": "MIMS.me.soil.6.0"}
```

```shell
poetry run list-mongodb-paths \
		--db-name biosamples \
		--collection biosamples \
		--sample-size 500000 > local/mongodb-paths-1pct.txt
```

> Processing documents: 100% 500000/500000 [07:28<00:00, 1114.98it/s]





----

## resources to explore

https://www.ncbi.nlm.nih.gov/viewvc/v1/trunk/submit/public-docs/biosample/biosample.xsd?view=co # 8 years old. seems
very incomplete.

https://www.ncbi.nlm.nih.gov/viewvc/v1/trunk/submit/public-docs/bioproject/bioproject.xsd?view=co

* get specifications from EBI too, in addition to NCBI?
* get DATA from EBI/ENA?
* what data to mirror and possibly restructure here vs accessing via APIs?
* what other repos to share code/notes with?

## document the use of APIs here

* https://www.ebi.ac.uk/biosamples/samples/SAMEA104726483.json
* https://www.ebi.ac.uk/ena/browser/advanced-search
* https://www.ebi.ac.uk/ena/portal/api/swagger-ui/index.html
* https://www.ebi.ac.uk/ena/taxonomy/rest/swagger-ui/index.html

----

```shell
make load-biosamples-into-mongo
```

> 2024-08-13T19:00:28.052828: 40000, 0.1%
> 2024-08-13T19:00:57.346565: 80000, 0.2%
> 2024-08-13T19:01:34.743793: 120000, 0.3%
>
>2024-08-14T05:34:00.487742: 43104782, 107.8%
>
>Process finished with exit code 0

```shell
mongosh
```

```mongo
use biosamples

db.biosamples.estimatedDocumentCount()

biosamples> db.biosamples.countDocuments({})
```

> 40347716

```shell
grep -c "</BioSample>" local/biosample_set.xml
```

> 40347716

Ids have been saved as strings. There are probably some Booleans in there too that are expressed as integers as a
strings

```mongo
db.biosamples.createIndex({ accession: 1 })

db.collectionName.createIndex({ "Package.value": 1 })
```

```compass
{"Package.value": "MIMS.me.soil.6.0"}
```

```shell
poetry run list-mongodb-paths \
		--db-name biosamples \
		--collection biosamples \
		--sample-size 500000 > local/mongodb-paths-1pct.txt
```

> Processing documents: 100% 500000/500000 [07:28<00:00, 1114.98it/s]




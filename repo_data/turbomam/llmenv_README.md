system requirements:
- [go](https://go.dev/)
- [yamlfmt](https://github.com/google/yamlfmt)
- [robot](https://robot.obolibrary.org/)
- wget
- [yq](https://github.com/mikefarah/yq) (Mike Farah/GO)

----

- try [litellm](https://litellm.vercel.app/) instead of [llm](https://llm.datasette.io/en/stable/)?
- extract `Extension`s with [linkml-map](https://linkml.io/linkml-map/) instead of yq?


## Ontology Access Kit operations 
https://github.com/INCATools/ontology-access-kit/

These `runoak` commands fetch a SQLite version of EnvO from the clous (a BBOP S3 bucket?) if needed. They don't require downloading the EnvO RDF/XML OWL from GitHub
CJM would create an alias like `envo="runoak -i obo:sqlite:envo"`

```shell
# for anything that uses the Bioportal endpoint
runoak set-apikey --endpoint bioportal <SECRET>

runoak --input bioportal: ontology-metadata envo
runoak --input bioportal: ontology-versions envo
runoak --input bioportal: search biome

runoak cache-ls # cache-clear if really necessary

# most useful for MIxS/EnvO subsetting tasks?
runoak --input sqlite:obo:envo relationships .desc//p=i ENVO:00000428 > biome-relationships.tsv # !!! pivot? include entailment? --include-entailed / --no-include-entailed; --non-redundant-entailed / --no-non-redundant-entailed
runoak --input sqlite:obo:envo term-metadata .desc//p=i ENVO:00000428 > biome-metadata.yaml # !!! try different formats? or predicate list?

runoak --input sqlite:obo:envo aliases 'biome'
runoak --input sqlite:obo:envo ancestors 'biome'
runoak --input sqlite:obo:envo definitions 'biome' 
runoak --input sqlite:obo:envo descendants 'biome' 
runoak --input sqlite:obo:envo info 'biome'
runoak --input sqlite:obo:envo labels 'biome' 
runoak --input sqlite:obo:envo languages
runoak --input sqlite:obo:envo leafs
runoak --input sqlite:obo:envo obsoletes
runoak --input sqlite:obo:envo prefixes
runoak --input sqlite:obo:envo siblings 'aquatic biome'
runoak --input sqlite:obo:envo terms
runoak --input sqlite:obo:envo tree  biome # up by default
runoak --input sqlite:obo:envo usages  biome
```


## Needs followup
```
runoak --input envo.ofn axioms 'biome' # NotImplementedError requires OFN... but still getting ERROR:root:function AnnotationAssertion(oboInOwl:hasExactSynonym, obo:FOODON_00001014, yoghurt) TypeError: Type mismatch between en-br (type: <class 'str'> and [<class 'funowl.general_definitions.LanguageTag'>, <class 'NoneType'>]
runoak --input sqlite:obo:envo disjoints 'biome' --autolabel -O csv # biome is disjoint from both ecoregion and ecozone # additional single-blank-node disjoints?!
runoak --input sqlite:obo:envo paths  -p i,p biosphere 'polar biome' # reports results but then says no paths found
runoak --input sqlite:obo:envo roots # why are hail and CL:0000000 reported?
runoak --input sqlite:obo:envo singletons # do these results make sense?
runoak --input sqlite:obo:envo statistics # ERRORS
runoak --input sqlite:obo:envo subsets # output and ERRORS
runoak --input sqlite:obo:envo term-categories biome # nothing
runoak --input sqlite:obo:envo term-subsets biome # nothing```
```

## Haven't goten these to work yet
__May not be relevant for MIxS EnvO tasks__

- cache-clear
- annotate
- apply 
- apply-obsolete
- apply-taxon-constraints
- associations
- associations-counts
- associations-matrix
- diff
- diff-associations
- diff-terms
- diff-via-mappings
- dump
- enrichment
- expand-subsets # WARNING:root:Subset may be incorrectly encoded as value for envoPolar # subset  term    subset_termValueError: Subset envoPolar not found in ...
- EXTRACT
- fill-table
- generate-definitions
- generate-disjoints
- generate-lexical-replacements
- generate-logical-definitions
- generate-synonyms
- information-content
- lexmatch
- lint
- logical-definitions
- mappings
- migrate-curies 
- normalize
- ontologies
- QUERY
- rollup
- similarity 
- similarity-pair
- synonymize # Deprecated: use generate-synonyms
- taxon-constraints
- termset-similarity
- transform
- validate
- validate-definitions
- validate-mappings
- validate-multiple
- validate-synonyms

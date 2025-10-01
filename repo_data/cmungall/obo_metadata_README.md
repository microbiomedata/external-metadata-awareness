# obo_metdata

Convenience prolog predicates for working with ontologies and triples that use either the OBO IAO or OboInOwl (oio) metadata vocabulary.

## Examples:

query in-memory triplestore for class text definitions plus related synonyms"

```
definition(C,D),
has_related_synonym(C,S)
```

related synonyms, with all axiom annotation:

```
has_related_synonym_axiom(C,S,A),
rdf(A,P,B)
```


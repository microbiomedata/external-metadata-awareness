## Relation Graph, Python Port

This is a minimal implementation of [relation-graph](https://github.com/balhoff/relation-graph/) in Python

The goal is to reason over a minimal subset

- subClassOf
- someValuesFrom
- transitive properties
- property chains

To run:

```python
run_relation_graph("tests/input/test.csv", "tests/output/results.csv")
```

- input must be csv
- headers must be subject, predicate, object
- domain entities can be any syntax, rdf/owl terms must be CURIEs
- rows are either:
   - relation graph direct edges
   - triples of the form `PRED,rdf:type,owl:TransitiveProperty`

See tests/input for details

## TODO

- reflexive edges
- relax equivalence to paired subClassOf
- compare with scala relation-graph
- property chains

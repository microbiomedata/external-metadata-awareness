# cat-merge

Python library for merging individual source KGX files in the Monarch Initiative ingest pipeline. 

#### Dependencies

- [Poetry](https://python-poetry.org/docs/)
- [Pandas](https://pandas.pydata.org/)

#### Usage

Import the merge tool:
```python
from cat_merge.merge import merge
```

You can either merge a list of node and edge files:
```python
merge(
    name='monarch-kg',
    nodes=['xenbase_gene_nodes.tsv','reactome_pathway_nodes.tsv','monarch_ontology_nodes.tsv'],
    edges=['xenbase_gene_to_phenotype_edges.tsv','monarch_ontology_edges.tsv']
)
```

Or merge an entire directory:
```python
merge(
    name='monarch-kg',
    input_dir='transform_output',
    output_dir='merged-output'
)
```
[![Pyversions](https://img.shields.io/pypi/pyversions/biolink_model_pydantic.svg)](https://pypi.python.org/pypi/biolink_model_pydantic)
![](https://github.com/monarch-initiative/biolink-model-pydantic/actions/workflows/test.yml/badge.svg)
[![PyPi](https://img.shields.io/pypi/v/biolink_model_pydantic.svg)](https://pypi.python.org/pypi/biolink_model_pydantic)

# biolink-model-pydantic
Pydantic dataclasses for the Biolink model


#### Installation

```
pip install biolink_model_pydantic
```

#### Using the dataclasses

```python
from biolink_model_pydantic.model import Gene

gen_entity = Gene(id='NCBIGene:123', in_taxon='NCBITaxon:9606')
```

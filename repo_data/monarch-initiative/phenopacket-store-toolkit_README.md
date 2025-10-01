# Phenopacket Store Toolkit


Phenopacket Store Toolkit is a Python package and CLI 
for managing [Phenopacket Store](https://github.com/monarch-initiative/phenopacket-store), 
a collection of [GA4GH Phenopacket](https://phenopacket-schema.readthedocs.io/en/latest/) cohorts
that represent individuals with Mendelian diseases.

The toolkit aids the release and Q/C processes, 
and simplifies access to the Phenopacket Store data from the downstream applications.


## Availability

Phenopacket Store Toolkit can be installed from Python Package Index (PyPi):

```shell
python3 -m pip install phenopacket-store-toolkit
```

## Examples

### Access Phenopacket Store

The toolkit simplifies download and loading the cohort data. The `PhenopacketStoreRegistry` API
caches the release ZIP files locally (in `$HOME/.phenopacket-store` by default) 
and simplifies the loading:

```python
from ppktstore.registry import configure_phenopacket_registry

registry = configure_phenopacket_registry()

with registry.open_phenopacket_store(release="0.1.18") as ps:
   phenopackets = list(ps.iter_cohort_phenopackets("SUOX"))

assert len(phenopackets) == 35
```

The code checks if the release ZIP of Phenopacket Store version `0.1.18` is already 
available locally, and downloads the release ZIP file if necessary. 
This is followed by opening the store as `ps` 
and loading all phenopackets of the *SUOX* cohort.

We use Python context manager to ensure proper closing of the ZIP file handle.
`ps` *cannot* be used outside of the context manager block.

As an alternative to using a specific Phenopacket Store release, 
the *latest* release will be used if `release` argument is omitted.

### Make Phenopacket Store release

The release is handled by the Command Line Interface (CLI) of the toolkit.

The release functionality requires additional dependencies, which are installed automatically
by adding `release` profile:

```shell
python3 -m pip install phenopacket-store-toolkit[release]
```

Now, assuming that `notebooks` points to the notebook folder of the Phenopacket Store repository,
we can Q/C the phenopackets by running:

```shell
python3 -m ppktstore qc --notebook-dir notebooks
```

and we can create the release archive by running:

```shell
python3 -m ppktstore package --notebook-dir notebooks --release-tag 0.1.18 --output all_phenopackets
```

This will find all phenopackets in the `notebooks` folder, copy them into a top-level directory called `0.1.18`, 
and ZIP the directory into `all_phenopackets.zip`. 

## Learn more

Find more info in our detailed documentation:

- [Stable documentation](https://monarch-initiative.github.io/phenopacket-store-toolkit/stable) (last release on `main` branch)
- [Latest documentation](https://monarch-initiative.github.io/phenopacket-store-toolkit/latest) (bleeding edge, latest commit on `develop` branch)

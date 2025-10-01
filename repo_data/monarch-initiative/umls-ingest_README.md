# umls-ingest

UMLS ingest to generate mappings.

# Setup
This repository uses [`pyobo`](https://github.com/pyobo/pyobo) as the core dependency to function.

## Get ICD API token
[Registration](https://icd.who.int/icdapi/Account/Register) with ICD is needed to secure an API token that facilitates gaining access to resources. Save the API client ID and secret as environment variables in `~/bash_profile` or your preferred location.

```
export PYOBO_ICD_CLIENT_ID=whatever-client-id-assigned-to-you
export PYOBO_ICD_CLIENT_SECRET=whatever-client-secret-assigned-to-you
```

## Set DRUGBANK credentials
Same as ICD client ID and secret above, you can save DRUGBANK credentials (if you have one). If not, the following works too.
```
export DRUGBANK_USERNAME=username
export DRUGBANK_PASSWORD=password
```

## `make mappings`

Create a new virtual environment of your choice and install `poetry`. Install dependencies using `poetry install`. After that, do the following:
```
git clone https://github.com/monarch-initiative/umls-ingest.git
cd umls-ingest
make mappings
```
This should kickstart the process of an SSSOM tsv generation named `umls.sssom.tsv`.
# Acknowledgements

This [cookiecutter](https://cookiecutter.readthedocs.io/en/stable/README.html) project was developed from the [monarch-project-template](https://github.com/monarch-initiative/monarch-project-template) template and will be kept up-to-date using [cruft](https://cruft.github.io/cruft/).
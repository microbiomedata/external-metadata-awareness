# SynBio schema

This needs a rewrite.

### Requires

- Python 3.9
- [Poetry](https://python-poetry.org/docs/#installation)
- SQLite 3.37.1+
- postgres client
- ssh tunnel
    - ssh -L 1111:bicoid:5432 `<USER>`@merlot.lbl.gov

Use the `make all` target to make everything

A r documentation step is included:

```bash
make gh-deploy
```

That's it!

The Makefile takes care of dependencies. Downstream files are only rebuilt if source files change.

## Documentation framework

You can change the theme by editing [mkdocs.yml](mkdocs.yml)

Do not edit docs in place. They are placed in the `docs` dir by `make stage-docs`.

You can add your own docs to `src/docs/

Note that docs are actually deployed on the gh-pages branch, but you don't need to worry about this. Just type:

```bash
make gh-deploy
```

The root fork of this repo is private. Decisions to publish to GitHub Pages should be very conservative.

The template site is deployed on

~~http://cmungall.github.io/synbio-schema~~

## Annotating [enumerated values](https://linkml.io/linkml/intro/tutorial06.html?highlight=enumeration)

For example,
an [organsim's](https://turbomam.github.io/synbio-schema/Organism/) [binomial name](https://turbomam.github.io/synbio-schema/binomial_name_enum/)

`make target/organism_unique_binomial_names.txt`

Curate with

- Google
- Wikipedia
- NCBI's [Taxonomy Browser](https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi)

and
especially [The NCBITaxon browser at EBI's OLS](https://www.ebi.ac.uk/ols/ontologies/ncbitaxon/terms?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FNCBITaxon_1&viewMode=All&siblings=false)

then

- enums_to_curateable
- curated_to_enums

### More about LinkML and Enumerations

- https://linkml.io/
- https://linkml.io/linkml/
- https://github.com/linkml/linkml-model-enrichment/blob/main/pyproject.toml
- https://linkml.io/linkml/intro/tutorial06.html?highlight=enumeration

## Experiment with term constraints
- try asserting that an organism is_a named thing in [target/org_binomial_name_curated.yaml](target/org_binomial_name_curated.yaml), deleting an id value from [target/organisms_catted_repaired.tsv](target/organisms_catted_repaired.tsv) and running `make generated target/organisms_catted_repaired.yaml`
- try removing the `testspecies` permissible value in the `binomial_name_enum` enumeration in `org_binomial_name_curated.yaml` and tunning the same make steps


rec | req | multivalued | min instances | max instances
-- | -- | -- | -- | --
doesn't matter  | FALSE | FALSE | 0 | 1
doesn't matter  | FALSE | TRUE | 0 | inf
doesn't matter  | TRUE | FALSE | 1 | 1
doesn't matter  | TRUE | TRUE | 1 | inf

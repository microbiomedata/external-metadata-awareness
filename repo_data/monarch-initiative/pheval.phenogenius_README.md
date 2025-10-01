# PhEval Runner for PhenoGenius

This is the PhenoGenius plugin for PhEval. With this plugin, you can leverage the gene prioritisation tool, PhenoGenius, to run the PhEval pipeline seamlessly. The setup process for running the full PhEval Makefile pipeline differs from setting up for a single run. The Makefile pipeline creates directory structures for corpora and configurations to handle multiple run configurations. Detailed instructions on setting up the appropriate directory layout, including the input directory and test data directory, can be found here.

## Installation

Clone the pheval.phenogenius repo and set up the poetry environment:

```sh
git clone https://github.com/yaseminbridges/pheval.phenogenius.git

cd pheval.genius

poetry shell

poetry install

```

## Configuring a *single* run

### Setting up the input directory

A config.yaml should be located in the input directory and formatted like so:

```yaml
tool: PhenoGenius
tool_version: 0.1.0
variant_analysis: False
gene_analysis: True
disease_analysis: False
tool_specific_configuration_options:
```

The bare minimum fields are filled to give an idea on the requirements, as PhenoGenius is gene prioritisation tool, only `gene_analysis` should be set to `True` in the config. An example config has been provided pheval.phenogenius/config.yaml.

You will need to clone the PhenoGeniusCli into the input directory:

```shell
git clone https://github.com/kyauy/PhenoGeniusCli.git
```

The overall structure of the input directory should look something like so:
```tree
.
├── PhenoGeniusCli
│   ├── PKD1.tsv
│   ├── README.md
│   ├── data
│   │   ├── graph
│   │   │   ├── 390groups.gexf
│   │   │   ├── group_image.png
│   │   │   ├── onto_image.png
│   │   │   └── ontology.gexf
│   │   ├── img
│   │   │   ├── logo-chuga.png
│   │   │   ├── logo-seqone.png
│   │   │   ├── logo-uga.png
│   │   │   ├── logoMIAI-rvb.png
│   │   │   └── phenogenius.png
│   │   └── resources
│   │       ├── Homo_sapiens.gene_info.gz
│   │       ├── hp_2024.obo
│   │       ├── hpo_obo_2024.json
│   │       ├── ohe_all_thesaurus_weighted_2024.tsv.gz
│   │       ├── pheno_NMF_390_matrix_42_2024.pkl
│   │       ├── pheno_NMF_390_model_42_2024.pkl
│   │       └── similarity_dict_threshold_80_2024.json
│   ├── phenogenius_cli.py
│   ├── poetry.lock
│   └── pyproject.toml
└── config.yaml
```

### Setting up the testdata directory

The PhenoGenius plugin for PhEval accepts phenopackets as an input for running PhenoGenius. 

The testdata directory should include a subdirectory named phenopackets:

```tree
├── testdata_dir
   └── phenopackets
```

## Run command

Once the testdata and input directories are correctly configured for the run, the pheval run command can be executed.

```sh
pheval run --input-dir /path/to/input_dir \
--testdata-dir /path/to/testdata_dir \
--runner phenogeniusphevalrunner \
--output-dir /path/to/output_dir \
--version 1.0.1
```



# Docs

https://yaseminbridges.github.io/pheval.phenogenius/

# Acknowledgements

This [cookiecutter](https://cookiecutter.readthedocs.io/en/stable/README.html) project was developed from the [pheval-runner-template](https://github.com/yaseminbridges/pheval-runner-template.git) template and will be kept up-to-date using [cruft](https://cruft.github.io/cruft/).

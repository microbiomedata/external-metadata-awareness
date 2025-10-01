# Phen2Gene Runner for PhEval
This is the Phen2Gene plugin for PhEval. With this plugin, you can leverage the gene prioritisation tool, Phen2Gene, to run the PhEval pipeline seamlessly. The setup process for running the full PhEval Makefile pipeline differs from setting up for a single run. The Makefile pipeline creates directory structures for corpora and configurations to handle multiple run configurations. Detailed instructions on setting up the appropriate directory layout, including the input directory and test data directory, can be found here.

## Installation

Clone the pheval.phen2gene repo and set up the poetry environment:

```sh
git clone https://github.com/monarch-initiative/pheval.phen2gene.git

cd pheval.phen2gene

poetry shell

poetry install

```

or install with PyPi:

```sh
pip install pheval.phen2gene
```

## Configuring a *single* run

### Setting up the input directory

A config.yaml should be located in the input directory and formatted like so:

```yaml
tool: phen2gene
tool_version: 1.2.3
variant_analysis: False
gene_analysis: True
disease_analysis: False
tool_specific_configuration_options:
  environment: local
  phen2gene_python_executable: Phen2Gene/phen2gene.py
  post_process:
    score_order: descending
```

The bare minimum fields are filled to give an idea on the requirements, as Phen2Gene is gene prioritisation tool, only `gene_analysis` should be set to `True` in the config. An example config has been provided pheval.phen2gene/config.yaml.

The Phen2Gene input data directory should also be located in the input directory - or a symlink pointing to the location in a directory named `lib`.

The `phen2gene_python_executable` points to the name of the Phen2Gene python executable file - this is usually located within the `Phen2Gene` directory within the input directory.

The overall structure of the input directory should look something like so (omitting files in the `lib` for clarity):

```tree
.
├── config.yaml
├── lib
│   ├── Knowledgebase
│   ├── lib
│   ├── phen2gene.py
│   ├── skewness
│   └── weights
└── Phen2Gene
    ├── accuracy.py
    ├── accuracy.sh
    ├── calcs
    ├── Dockerfile
    ├── environment.yml
    ├── example
    ├── generate_ranking_data.py
    ├── getbenchmark.sh
    ├── lib
    ├── LICENSE
    ├── phen2gene.py
    ├── README.md
    ├── requirements.txt
    ├── runtest.sh
    ├── setup.sh
    └── test
```
### Setting up the testdata directory

The Phen2Gene plugin for PhEval accepts phenopackets as an input for running Phen2Gene. 

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
--runner phen2genephevalrunner \
--output-dir /path/to/output_dir \
--version 1.2.3
```

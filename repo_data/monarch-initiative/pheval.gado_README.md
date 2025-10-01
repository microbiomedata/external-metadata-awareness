# GADO Runner for PhEval
This is the GADO plugin for PhEval. With this plugin, you can leverage the gene prioritisation tool, GADO, to run the PhEval pipeline seamlessly. The setup process for running the full PhEval Makefile pipeline differs from setting up for a single run. The Makefile pipeline creates directory structures for corpora and configurations to handle multiple run configurations. Detailed instructions on setting up the appropriate directory layout, including the input directory and test data directory, can be found here.

## Installation

Clone the pheval.gado repo and set up the poetry environment:

```sh
git clone https://github.com/monarch-initiative/pheval.gado.git

cd pheval.gado

poetry shell

poetry install

```
or install with PyPi:

```sh
pip install pheval.gado
```

## Configuring a *single* run

### Setting up the input directory

A config.yaml should be located in the input directory and formatted like so:

```yaml
tool: GADO
tool_version: 1.0.1
variant_analysis: False
gene_analysis: True
disease_analysis: False
tool_specific_configuration_options:
  gado_jar: GadoCommandline-1.0.1/GADO.jar
  hpo_ontology: hp.obo
  hpo_predictions_info: predictions_auc_bonf.txt
  genes: hpo_prediction_genes.txt
  hpo_predictions: genenetwork_bonf_spiked/genenetwork_bonf_spiked.dat
```

The bare minimum fields are filled to give an idea on the requirements, as GADO is gene prioritisation tool, only `gene_analysis` should be set to `True` in the config. An example config has been provided pheval.gado/config.yaml.

All GADO input data files required for running (specified in the `tool_specific_configuration_options`) should be located in the input directory.
The `gado_jar` points to the name of the GADO jar file which should also be located in the input directory.

The overall structure of the input directory should look something like so:

```tree
.
├── GadoCommandline-1.0.1
├── config.yaml
├── predictions_auc_bonf.txt
├── hp.obo
├── hpo_prediction_genes.txt
└── genenetwork_bonf_spiked
   └── genenetwork_bonf_spiked.dat
```
### Setting up the testdata directory

The GADO plugin for PhEval accepts phenopackets as an input for running GADO. 

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
--runner gadophevalrunner \
--output-dir /path/to/output_dir \
--version 1.0.1
```

# OntoGPT Runner for PhEval
This is the OntoGPT plugin for PhEval. With this plugin, you can leverage OntoGPT to run the PhEval pipeline seamlessly. The setup process for running the full PhEval Makefile pipeline differs from setting up for a single run. The Makefile pipeline creates directory structures for corpora and configurations to handle multiple run configurations. Detailed instructions on setting up the appropriate directory layout, including the input directory and test data directory, can be found here.


## Installation

Clone the pheval.ontogpt repo and set up the poetry environment:

```shell
git clone https://github.com/yaseminbridges/pheval.ontogpt.git
cd pheval.ontogpt
poetry shell
poetry install
```
## Configuring a _single_ run

### Setting up the input directory

A config.yaml should be located in the input directory and formatted like so:

```yaml
tool: ontogpt
tool_version: 0.2.9
variant_analysis: False
gene_analysis: False
disease_analysis: True
tool_specific_configuration_options:
  # select from gpt-3.5-turbo-16k, gpt-3.5-turbo, gpt-4, gpt-4-32k
  model: gpt-4
  # specify the prompt you wish to use
  template: simple_disease_request_template.jinja2
  # specify the name of the constrained list of genes or diseases file you wish to use (optional)
  constrained_list_path:
```

The bare minimum fields are filled to give an idea on the requirements. An example config has been provided pheval.ontogpt/config.yaml.

The overall structure of the input directory will look something like so:

Where . is the root of the input directory

```tree
.
├── config.yaml
└── gene_request_template.jinja2

```

If you wish to use a constrained list of genes or diseases and provide that to the LLM to predict the diagnosis from that list, you should provide the relative path to the input directory of a text file containing all genes/diseases contained to one line, each item separated by a comma.


## Configuring the prompt

If you wish to alter the prompt given to the API, you can alter any of the template located in 
`pheval.ontogpt/src/pheval_ontogpt/prompt_templates/`. However, you **must** retain the output format outlined.


## Test data directory structure

The OntoGPT plugin for PhEval accepts phenopackets as an input for running OntoGPT.

The testdata directory should include a subdirectory named phenopackets:

Where . is the root of the test data directory

```tree
.
└── phenopackets
   ├── Abdul_Wahab-2016-GCDH-Patient_5.json
   └── Ajmal-2013-BBS1-IV-5_family_A.json

```

## Run command
```shell
pheval run --input-dir /path/to/input_dir \
--testdata-dir /path/to/testdata_dir \
--runner ontogptphevalrunner \
--output-dir /path/to/output_dir \
--version 0.2.9
```


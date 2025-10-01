# SvAnna Runner for PhEval

This is the SvAnna plugin for PhEval. With this plugin, you can leverage the structural variant prioritisation tool, SvAnna, to run the PhEval pipeline seamlessly. The setup process for running the full PhEval Makefile pipeline differs from setting up for a single run. The Makefile pipeline creates directory structures for corpora and configurations to handle multiple run configurations. Detailed instructions on setting up the appropriate directory layout, including the input directory and test data directory, can be found here.


## Installation

Clone the pheval.svanna repo and set up the poetry environment:

```shell
git clone https://github.com/monarch-initiative/pheval.svanna.git
cd pheval.svanna
poetry shell
poetry install
```

or install with PyPi:

```sh
pip install pheval.svanna
```
## Configuring a *single* run:

### Setting up the input directory

A `config.yaml` should be located in the input directory and formatted like so:

```yaml
tool: svanna
tool_version: 1.0.3
variant_analysis: True
gene_analysis: False
disease_analysis: False
tool_specific_configuration_options:
  svanna_jar_executable: svanna-cli-1.0.3/svanna-cli-1.0.3.jar
  post_process:
    sort_order: descending
```
The bare minimum fields are filled to give an idea on the requirements, as SvAnna is variant prioritisation tool, only variant_analysis should be set to True in the config. An example config has been provided pheval.svanna/config.yaml.

The `svanna_jar_executable` points to the location of the Svanna jar executable in the input directory.


### Setting up the testdata directory

The SvAnna plugin for PhEval accepts phenopackets and vcf files as an input. 

The testdata directory should include subdirectories named `phenopackets` and `vcf`.

e.g., 

```tree
├── testdata_dir
   ├── phenopackets
   └── vcf
```

## Run command

Once the testdata and input directories are correctly configured for the run, the `pheval run` command can be executed.

```bash
pheval run --input-dir /path/to/input_dir \
--testdata-dir /path/to/testdata_dir \
--runner svannaphevalrunner \
--output-dir /path/to/output_dir \
--version 1.0.3
```

## Common errors

You may see an error that is related to the current `setuptools` being used:

```shell
pkg_resources.extern.packaging.requirements.InvalidRequirement: Expected closing RIGHT_PARENTHESIS
    requests (<3,>=2.12.*) ; extra == 'parse'
             ~~~~~~~~~~^
```

To fix the error, `setuptools` needs to be downgraded to version 66:

```shell
pip uninstall setuptools
pip install -U setuptools=="66"
```

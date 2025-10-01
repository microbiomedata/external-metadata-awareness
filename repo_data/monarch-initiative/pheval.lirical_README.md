# LIRICAL Runner for PhEval

This is the LIRICAL plugin for PhEval. With this plugin, you can leverage the prioritisation tool, LIRICAL, to run the PhEval pipeline seamlessly. he setup process for running the full PhEval Makefile pipeline differs from setting up for a single run. The Makefile pipeline creates directory structures for corpora and configurations to handle multiple run configurations. Detailed instructions on setting up the appropriate directory layout, including the input directory and test data directory, can be found here.

## Installation 

Install with pip:

```shell
pip install pheval.lirical
```
Alternatively clone the pheval.lirical repo and set up the poetry environment:

```shell
git clone https://github.com/monarch-initiative/pheval.lirical.git
cd pheval.lirical
poetry shell
poetry install
```

## Configuring a *single* run:

### Setting up the input directory

A `config.yaml` should be located in the input directory and formatted like so:

```yaml
tool: LIRICAL
tool_version: 2.0.0-RC2
variant_analysis: True
gene_analysis: True
disease_analysis: True
tool_specific_configuration_options:
  mode: phenopacket
  lirical_jar_executable: lirical-cli-2.0.0-RC2/lirical-cli-2.0.0-RC2.jar
  exomiser_db_configurations:
    exomiser_database:
    exomiser_hg19_database: 2302_hg19_variants.mv.db
    exomiser_hg38_database:
  post_process:
    sort_order: descending
```
The bare minimum fields are filled to give an idea on the requirements. 

The `mode` should specify the mode you want to run LIRICAL in (either manual or phenopacket) both of these options require phenopackets as an input.

The LIRICAL data files should be located in the input directory under a subdirectory named `data`
If running LIRICAL with variant and/or gene analysis set to true, you will need to provide the relevant exomiser hg19/hg38 databases.

The lirical jar executable points to the location in the input directory.

The input directory should look something like so (removed some files for clarity):

```tree
.
├── 2302_hg19_variants.mv.db
├── config.yaml
├── data
│   ├── hg19_refseq.ser
│   ├── hg19_ucsc.ser
│   ├── hg38_refseq.ser
│   ├── hg38_ucsc.ser
│   ├── hgnc_complete_set.txt
│   ├── hp.json
│   ├── mim2gene_medgen
│   └── phenotype.hpoa
└── lirical-cli-2.0.0-RC2
    └── lirical-cli-2.0.0-RC2.jar

```
### Setting up the testdata directory

The LIRICAL plugin for PhEval accepts phenopackets and vcf files as an input. The plugin can be run in only `disease_analysis` mode, where only phenopackets are required as an input, however, this *must* be specified in the `config.yaml`.

The testdata directory should include subdirectories named `phenopackets` and `vcf` if running with gene/variant prioritisation.

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
--runner liricalphevalrunner \
--output-dir /path/to/output_dir \
--version 13.2.0
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

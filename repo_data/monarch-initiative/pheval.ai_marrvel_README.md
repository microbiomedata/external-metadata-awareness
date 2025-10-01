# AI-MARRVEL Runner for PhEval

This is the AI-MARRVEL plugin for PhEval. With this plugin, you can leverage the tool, AI-MARRVEL, to run the PhEval pipeline seamlessly. Detailed instructions on setting up the appropriate directory layout, including the input directory and test data directory, can be found here.
# Installation

```bash
git clone https://github.com/yaseminbridges/pheval.ai_marrvel.git
cd pheval.ai_marrvel
poetry install
poetry shell
```

Alternative install with pip

```shell
pip install pheval-ai-marrvel
```

# Configuring a single run:

## Setting up the input directory
A `config.yaml` should be located in the input directory and formatted like so:

```yaml
tool: AI-MARRVEL
tool_version: 1.0.0
variant_analysis: True
gene_analysis: True
disease_analysis: False
tool_specific_configuration_options:
  environment: nextflow # either apptainer/docker/nextflow
```

The AI-MARRVEL data dependencies should also be unpacked into the input directory. The overall structure of the input directory should look something like:

```tree
.
├── annotate
├── bcf_annotate 
├── config.yaml
├── filter_vep
├── merge_expand
├── mod5_diffusion
├── model_inputs
├── omim_annotate
├── phrank
├── predict_new 
├── var_tier 
└── vep 
```

The testdata directory should include the subdirectory named `phenopackets` - which should contain phenopackets and `vcf` - which should contain the gzipped VCF files.

e.g.,

```tree
├── testdata_dir
   ├── phenopackets
   └── vcf
```
# Run command

```bash
pheval run --input-dir /path/to/input_dir \
--runner aimarrvelrunner \
--output-dir /path/to/output_dir \
--testdata-dir /path/to/testdata_dir
```
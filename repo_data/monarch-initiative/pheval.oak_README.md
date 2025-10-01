# OAK Runner for PhEval (WORK IN PROGRESS)

This serves as an OAK PhEval runner. [PhEval](https://monarch-initiative.github.io/pheval/) (Phenotypic Inference Evaluation Framework) is an extensible framework for evaluating variant prioritisation and phenotype matching pipelines.


# Installation

```bash
git clone https://github.com/monarch-initiative/pheval.oak.git
cd pheval.oak
poetry install
poetry shell
```

# Configuring a run with the template runner

A `config.yaml` should be located in the input directory and formatted like so:

```yaml
tool: template
tool_version: 1.0.0
variant_analysis: False
gene_analysis: True
disease_analysis: False
tool_specific_configuration_options:
```

The testdata directory should include the subdirectory named `phenopackets` - which should contain phenopackets.

# Run command

```bash
pheval run --input-dir /path/to/input_dir \
--runner phenologrunner \
--output-dir /path/to/output_dir \
--testdata-dir /path/to/testdata_dir
```

# Benchmark

You can benchmark the run with the `pheval-utils benchmark` command:

```bash
pheval-utils benchmark --directory /path/to/output_directoy \
--phenopacket-dir /path/to/phenopacket_dir \
--output-prefix OUTPUT_PREFIX \
--gene-analysis \
--plot-type bar_cumulative
```

The path provided to the `--directory` parameter should be the same as the one provided to the `--output-dir` in the `pheval run` command

You should also remove the `src/pheval_template/run/fake_predictor.py` and implement the running of your own tool. Methods in the post-processing can also be altered to process your own tools output.

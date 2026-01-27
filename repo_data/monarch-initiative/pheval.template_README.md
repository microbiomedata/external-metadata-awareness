# Template Runner for PhEval

This serves as a template repository designed for crafting a personalised PhEval runner. [PhEval](https://monarch-initiative.github.io/pheval/) (Phenotypic Inference Evaluation Framework) is an extensible framework for evaluating variant priorotization and phenotype matching pipelines.

Presently, the runner executes a mock predictor found in `src/pheval_template/run/fake_predictor.py`. Nevertheless, the primary objective is to leverage this repository as a starting point to develop your own runner for your tool, allowing you to customise and override existing methods effortlessly, given that it already encompasses all the necessary setup for integration with PhEval. There are exemplary methods throughout the runner to provide an idea on how things could be implemented.

# Installation

```bash
git clone https://github.com/yaseminbridges/pheval.template.git
cd pheval.template
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
--runner templatephevalrunner \
--output-dir /path/to/output_dir \
--testdata-dir /path/to/testdata_dir
```

# Benchmark

You can benchmark the run with the `pheval-utils generate-benchmark-stats` command:

```bash
pheval-utils generate-benchmark-stats --run-yaml /path/to/runs.yaml \
```

The path provided to the `---run-yaml` parameter should be the path to the YAML  configuration file for running the benchmark, it may be formatted like so:

```yaml
benchmark_name: pheval_template_benchmark
runs:
  - run_identifier: template_runner
    results_dir: /path/to/results_dir # Should be the same directory specified as the --output-dir in the pheval run command
    phenopacket_dir: /path/to/phenopacket_dir
    gene_analysis: True
    variant_analysis: False
    disease_analysis: False
    threshold:
    score_order: descending
plot_customisation:
  gene_plots:
    plot_type: bar_cumulative
    rank_plot_title: PhEval Template Recall Performance
    roc_curve_title: PhEval Template ROC Curve
    precision_recall_title: PhEval Template PR Curve
  disease_plots:
    plot_type:
    rank_plot_title:
    roc_curve_title: 
    precision_recall_title: 
  variant_plots:
    plot_type:
    rank_plot_title: 
    roc_curve_title: 
    precision_recall_title:
```

# Personalising to your own tool

If overriding this template to create your own runner implementation. There are key files that should change to fit with your runner implementation.

1. The name of the Runner class in `src/pheval_template/runner.py` should be changed.
2. Once the name of the Runner class has been customised, line 15 in `pyproject.toml` should also be changed to match the class name, then run `poetry lock` and `poetry install`

The runner you give on the CLI will then change to the name of the runner class.

You should also remove the `src/pheval_template/run/fake_predictor.py` and implement the running of your own tool. Methods in the post-processing can also be altered to process your own tools output.

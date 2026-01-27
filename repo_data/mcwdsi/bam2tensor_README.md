# bam2tensor

[![PyPI](https://img.shields.io/pypi/v/bam2tensor.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/bam2tensor.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/bam2tensor)][pypi status]
[![License](https://img.shields.io/pypi/l/bam2tensor)][license]

[![Documentation](https://github.com/mcwdsi/bam2tensor/actions/workflows/docs.yml/badge.svg)][documentation]
[![Tests](https://github.com/mcwdsi/bam2tensor/actions/workflows/tests.yml/badge.svg)][tests]
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=mcwdsi_bam2tensor&metric=coverage)][sonarcov]
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=mcwdsi_bam2tensor&metric=alert_status)][sonarquality]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)][poetry]

[pypi status]: https://pypi.org/project/bam2tensor/
[documentation]: https://mcwdsi.github.io/bam2tensor
[tests]: https://github.com/mcwdsi/bam2tensor/actions?workflow=Tests

[sonarcov]: https://sonarcloud.io/summary/overall?id=mcwdsi_bam2tensor
[sonarquality]: https://sonarcloud.io/summary/overall?id=mcwdsi_bam2tensor
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black
[poetry]: https://python-poetry.org/

bam2tensor is a Python package for converting .bam files to dense representations of methylation data (as .npz NumPy arrays). It is designed to evaluate all CpG sites and store methylation states for loading into other deep learning pipelines.

![bam2tensor logo](https://raw.githubusercontent.com/mcwdsi/bam2tensor/main/docs/logo/bam2tensor-logo.png)


## Features
- Parses .bam files using [pysam](https://github.com/pysam-developers/pysam)
- Extracts methylation data from all CpG sites
- Supports any genome (Hg38, T2T-CHM13, mm10, etc.)
- Stores data in sparse format (COO matrix) for efficient loading
- Exports methylation data to .npz NumPy arrays
- Easily parallelizable

## Requirements

- Python 3.9+
- pysam, numpy, scipy, tqdm

## Installation

You can install _bam2tensor_ via [pip] from [PyPI]:

```console
pip install bam2tensor
```

## Usage

Please see the [Reference Guide] for full details.

## Data Structure

One `.npz` file is generated for each separate `.bam`, which can be loaded using `scipy.sparse.load_npz()`. Each `.npz` file contains a single sparse SciPy [COO matrix].

In the COO matrix, each row represents a read and each column represents a CpG site. The value at each row/column is the methylation state (`0` = unmethylated, `1` = methylated, `-1` = no data). Note that `-1` can represent indels or point mutations.

## Todo
- Consider storing a Read ID: Row ID mapping?
- Export / more stably store & import embedding mapping? (.npz or other instead of .json?)
- Store metadata / object reference in .npz file?
- Explore using Xarray or [Sparse](https://sparse.pydata.org/en/stable/)?

## Contributing

Contributions are welcome! Please see the [Contributor Guide].

## License

Distributed under the terms of the [MIT license][license],
_bam2tensor_ is free and open source.

## Issues

If you encounter any problems,
please [file an issue] along with a detailed description.

## Credits

This project is developed and maintained by [Nick Semenkovich (@semenko)], as part of the Medical College of Wisconsin's [Data Science Institute].

This project was generated from [Statistics Norway]'s [SSB PyPI Template].

[Nick Semenkovich (@semenko)]: https://nick.semenkovich.com/
[Data Science Institute]: https://www.mcw.edu/departments/data-science-institute
[statistics norway]: https://www.ssb.no/en
[pypi]: https://pypi.org/
[ssb pypi template]: https://github.com/statisticsnorway/ssb-pypitemplate
[file an issue]: https://github.com/mcwdsi/bam2tensor/issues
[pip]: https://pip.pypa.io/
[COO matrix]: https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.coo_matrix.html

<!-- github-only -->

[license]: https://github.com/mcwdsi/bam2tensor/blob/main/LICENSE
[contributor guide]: https://github.com/mcwdsi/bam2tensor/blob/main/CONTRIBUTING.md
[reference guide]: https://mcwdsi.github.io/bam2tensor/reference.html

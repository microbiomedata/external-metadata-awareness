# eagerutils

# Description
This is an unofficial collection of utility scripts for the EAGER v1.9.* genome reconstruction pipeline (Peltzer et al. (2016) _Genome Biology_. DOI: https://doi.org/10.1186/s13059-016-0918-z).

The tool contains small bash scripts that allow you do various things on EAGER configuration and output files and directories.

These utility scripts are compatible with EAGER version 1.92.55, and have been tested on Ubuntu 14.04 LTS with GNU Bash 4.3.11.

# Installation

  1. Clone the github repository to your local computer.
  3. Execute the `eagerutils` file in the `bin/` directory

# Modules

## Implemented
`reset` - cleans up a EAGER results directory to the state it was when originally generated (i.e. containing just the .xml file). If a parent directory of multiple runs is given, this will 'reset'  all sample directories and remove any ReportTable related files.

## Coming soon

`summarise` - will concatenate multiple ReportTable result files into a single file (useful when running multiple EAGER runnings against different genomes or testing different parameters).

`view` - prints a more readable version of the config file, for easy recovery of an EAGER run's settings.

# split-pool-mod-schema

A Schema with processes for splitting, pooling and modifying material entities. Intended to illustrate solutions for NMDC modeling of NEON metadata and metabolomics data

May also be used for isolating issues from other schema repos, like nmdc-schema

Based on https://github.com/turbomam/examples-first-cookiecutter

Sample data with broken rendering: https://htmlpreview.github.io/?https://github.com/turbomam/split-pool-mod-schema/blob/main/examples/output/Database-heterogeneous.html

## Website

[https://turbomam.github.io/split-pool-mod-schema](https://turbomam.github.io/split-pool-mod-schema)

## Repository Structure

* [examples/](examples/) - example data
* [project/](project/) - project files (do not edit these)
* [src/](src/) - source files (edit these)
  * [split_pool_mod_schema](src/split_pool_mod_schema)
    * [schema](src/split_pool_mod_schema/schema) -- LinkML schema
      (edit this)
    * [datamodel](src/split_pool_mod_schema/datamodel) -- generated
      Python datamodel
* [tests/](tests/) - Python tests

## Developer Documentation

<details>
Use the `make` command to generate project artefacts:

* `make all`: make everything
* `make deploy`: deploys site
</details>

## Credits

This project was made with [turbomam/examples-first-cookiecutter](https://github.com/turbomam/examples-first-cookiecutter), 
a derivative of [linkml-project-cookiecutter](https://github.com/linkml/linkml-project-cookiecutter).


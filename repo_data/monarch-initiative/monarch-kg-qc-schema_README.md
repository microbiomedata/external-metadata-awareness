# monarch-kg-qc-schema

Schema for QC reports on the Monarch KG.

## Website

[https://monarch-initiative.github.io/monarch-kg-qc-schema](https://monarch-initiative.github.io/monarch-kg-qc-schema)

## Repository Structure

* [examples/](examples/) - example data
* [project/](project/) - project files (do not edit these)
* [src/](src/) - source files (edit these)
  * [monarch_kg_qc_schema](src/monarch_kg_qc_schema)
    * [schema](src/monarch_kg_qc_schema/schema) -- LinkML schema
      (edit this)
    * [datamodel](src/monarch_kg_qc_schema/datamodel) -- generated
      Python datamodel
* [tests/](tests/) - Python tests

## Developer Documentation

<details>
Use the `make` command to generate project artefacts:

* `make all`: make everything
* `make deploy`: deploys site
</details>

## Credits

This project was made with
[linkml-project-cookiecutter](https://github.com/linkml/linkml-project-cookiecutter).

# biocore-data-model-linkml-template

LinkML model for the Data Biosphere project, migrated from https://github.com/DataBiosphere/biocore-data-model/tree/main/content/linkml into a LinkML cookie cutter template

## Website

[https://turbomam.github.io/biocore-data-model-linkml-template](https://turbomam.github.io/biocore-data-model-linkml-template)

## Repository Structure

* [examples/](examples/) - example data
* [project/](project/) - project files (do not edit these)
* [src/](src/) - source files (edit these)
  * [biocore_data_model_linkml_template](src/biocore_data_model_linkml_template)
    * [schema](src/biocore_data_model_linkml_template/schema) -- LinkML schema
      (edit this)
    * [datamodel](src/biocore_data_model_linkml_template/datamodel) -- generated
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

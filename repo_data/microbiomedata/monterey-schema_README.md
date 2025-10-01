# monterey-schema

Proving grounds for a refactored nmdc-schmea

## Website

[https://microbiomedata.github.io/monterey-schema](https://microbiomedata.github.io/monterey-schema)

## Repository Structure

* [examples/](examples/) - example data
* [project/](project/) - project files (do not edit these)
* [src/](src/) - source files (edit these)
  * [monterey_schema](src/monterey_schema)
    * [schema](src/monterey_schema/schema) -- LinkML schema
      (edit this)
    * [datamodel](src/monterey_schema/datamodel) -- generated
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

# minimal-metab

A LinkML cookiecutter repo for modelling metabolomics from the ground up

## Website

[https://microbiomedata.github.io/minimal-metab](https://microbiomedata.github.io/minimal-metab)

## Repository Structure

* [examples/](examples/) - example data
* [project/](project/) - project files (do not edit these)
* [src/](src/) - source files (edit these)
  * [minimal_metab](src/minimal_metab)
    * [schema](src/minimal_metab/schema) -- LinkML schema
      (edit this)
    * [datamodel](src/minimal_metab/datamodel) -- generated
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


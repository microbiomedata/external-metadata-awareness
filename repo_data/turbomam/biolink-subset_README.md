# biolink-subset

illustrates subsetting the BIlink schema with sheets_and_friends do-shuttle

## Website

[https://turbomam.github.io/biolink-subset](https://turbomam.github.io/biolink-subset)

## Repository Structure

* [examples/](examples/) - example data
* [project/](project/) - project files (do not edit these)
* [src/](src/) - source files (edit these)
  * [biolink_subset](src/biolink_subset)
    * [schema](src/biolink_subset/schema) -- LinkML schema
      (edit this)
    * [datamodel](src/biolink_subset/datamodel) -- generated
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


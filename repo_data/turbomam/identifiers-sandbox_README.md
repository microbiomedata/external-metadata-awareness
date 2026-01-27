# identifiers-sandbox

A LinkML schema and project for exploring the functionality of LinkML slots with `identifier: true`

## Website

[https://turbomam.github.io/identifiers-sandbox](https://turbomam.github.io/identifiers-sandbox)

## Repository Structure

* [examples/](examples/) - example data
* [project/](project/) - project files (do not edit these)
* [src/](src/) - source files (edit these)
  * [identifiers_sandbox](src/identifiers_sandbox)
    * [schema](src/identifiers_sandbox/schema) -- LinkML schema
      (edit this)
    * [datamodel](src/identifiers_sandbox/datamodel) -- generated
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


# tank-schema

a vehicle and tank schema

illustrates a concern that `slot_usage` of `false` on `required` is not applied to an inherited slot

## Website

[https://turbomam.github.io/tank-schema](https://turbomam.github.io/tank-schema)

## Repository Structure

* [examples/](examples/) - example data
* [project/](project/) - project files (do not edit these)
* [src/](src/) - source files (edit these)
  * [tank_schema](src/tank_schema)
    * [schema](src/tank_schema/schema) -- LinkML schema
      (edit this)
    * [datamodel](src/tank_schema/datamodel) -- generated
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


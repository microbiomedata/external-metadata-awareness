# cleanroom-schema

Cleanroom reboot of NMDC schema

## Website

* [https://microbiomedata.github.io/cleanroom-schema](https://microbiomedata.github.io/cleanroom-schema)

## Repository Structure

* [examples/](examples/) - example data
* [project/](project/) - project files (do not edit these)
* [src/](src/) - source files (edit these)
    * [cleanroom_schema](src/cleanroom_schema)
        * [schema](src/cleanroom_schema/schema) -- LinkML schema (edit this)
* [datamodel](src/cleanroom_schema/datamodel) -- Generated python datamodel
* [tests](tests/) - python tests

## Developer Documentation

<details>
Use the `make` command to generate project artefacts:

- `make all`: make everything
- `make deploy`: deploys site

</details>

## Credits

this project was made with [linkml-project-cookiecutter](https://github.com/linkml/linkml-project-cookiecutter)

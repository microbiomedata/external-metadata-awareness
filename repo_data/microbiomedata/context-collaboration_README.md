# context-collaboration

Resources for data-driven and collaboratively refined mappings between ontology classes like ENVO:00002259 ‘agricultural soil’ to MIxS environmental context questions like env_medium, subsetted according to MIxS environmental extensions like Agriculture.

## Website

[https://microbiomedata.github.io/context-collaboration](https://microbiomedata.github.io/context-collaboration)

## Repository Structure

* [examples/](examples/) - example data
* [project/](project/) - project files (do not edit these)
* [src/](src/) - source files (edit these)
  * [context_collaboration](src/context_collaboration)
    * [schema](src/context_collaboration/schema) -- LinkML schema
      (edit this)
    * [datamodel](src/context_collaboration/datamodel) -- generated
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

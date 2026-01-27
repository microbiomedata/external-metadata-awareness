# submission-schema

The NMDC submission schema.

Note that the while this repo is named `submission-schema`, the generated artifacts are named `nmdc_submission_schema` for disambiguation purposes when publishing to PyPI.

## Website

* [https://microbiomedata.github.io/submission-schema](https://microbiomedata.github.io/submission-schema)

## Repository Structure

* [examples/](examples/) - example data
* [project/](project/) - project files (do not edit these)
* [src/](src/) - source files (edit these)
    * [nmdc_submission_schema](src/nmdc_submission_schema)
        * [schema](src/nmdc_submission_schema/schema) -- LinkML schema (edit this)
* [datamodel](src/nmdc_submission_schema/datamodel) -- Generated python datamodel
* [tests](tests/) - python tests

## Developer Documentation

### Updating the submission schema

The version of `nmdc-schema` used as a basis when building the submission schema is controlled by a dependency in the `dev` group, specified in `pyproject.toml`. You can update the version used by running:

```shell
poetry add nmdc-schema==X.Y.Z --group dev  # replace X.Y.Z with the desired version
```

> [!NOTE]  
> It is important to use the `==` version constraint to ensure the exact version is installed. 

### Building the submission schema

Here's how you can generate the submission schema release artifacts:

#### Container-based process

##### Prerequisites

- Docker is installed on your computer
- You are in the root directory of the repository

##### Procedure

1. Build the container image you will later use to build the submission schema:
   ```shell
   docker build -t submission-schema-builder -f builder.Dockerfile .
   ```
2. Use that container image to build the submission schema:
   ```shell
   docker run --rm -it -v ${PWD}:/submission-schema submission-schema-builder
   ```
3. Commit the changes, using the new `nmdc-schema` version number as the commit message; like this:
   ```shell
   git add .
   git commit -m "X.Y.Z"  # replace X.Y.Z with the nmdc-schema version
   ```
4. (Optional) Delete the container image:
   ```shell
   docker image rm submission-schema-builder
   ```

#### Direct process

##### Procedure

1. Install Python dependencies:
   ```shell
   poetry install
   ```
2. Generate the release artefacts:
   ```shell
   make clean all
   ```
3. Commit the changes, using the new `nmdc-schema` version number as the commit message; like this:
   ```shell
   git add .
   git commit -m "X.Y.Z"  # replace X.Y.Z with the nmdc-schema version
   ```

## Credits

this project was made with [linkml-project-cookiecutter](https://github.com/linkml/linkml-project-cookiecutter)

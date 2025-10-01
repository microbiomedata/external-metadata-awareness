# mixs_fresh_start

This project provides support for converting the MIxS standard into LinkML via schemasheets

It provides full automation and better reporting, as an alternative to the more manual curation that was started in https://github.com/GenomicsStandardsConsortium/mixs/tree/issue-511-tested-schemasheets/schemasheets/tsv_in (although it does not address the class definitions or slot-to-class assignments that are aviaoable in that repo yet.)

The current implemntation focuses on aiding curators in distilling global definitions for terms that have (intentional or not) variations in the contest of different environmentla packages.

This prject can save a colored log of the difference between the original combined sheet and any user-provided differences in the modified sheet. **It only works on Linux systems at this point.**

This project requires the following system dependencies in addition to the Python libraties in pyproject.toml
- https://github.com/aswinkarthik/csvdiff for streaming the colored diff to STDOUT
  - this can be run on MacOS too, sending the colored output to the screen
- The linux version of https://man7.org/linux/man-pages/man1/script.1.html for saving the colored diff to a "typescript" file
- https://github.com/theZiz/aha for converting the colored "typescript" file to HTML
- optionally soemthing like https://github.com/wkhtmltopdf/wkhtmltopdf/blob/master/docs/usage/wkhtmltopdf.txt to convert the HTML output to PDF

The HTML report that is bundled with this repo can be viewed with this [htmlpreview.github.io link](https://htmlpreview.github.io/?https://github.com/microbiomedata/mixs_fresh_start/blob/main/assets/mixs_combined_diff_conservative.html)

_Note that this report skips a few MIxS terms that cause the difference engine to crash. See project.Makefile._



## Website

* [https://microbiomedata.github.io/mixs_fresh_start](https://microbiomedata.github.io/mixs_fresh_start)

## Repository Structure

* [examples/](examples/) - example data
* [project/](project/) - project files (do not edit these)
* [src/](src/) - source files (edit these)
    * [mixs_fresh_start](src/mixs_fresh_start)
        * [schema](src/mixs_fresh_start/schema) -- LinkML schema (edit this)
* [datamodel](src/mixs_fresh_start/datamodel) -- Generated python datamodel
* [tests](tests/) - python tests

## Developer Documentation

<details>
Use the `make` command to generate project artefacts:

- `make all`: make everything
- `make deploy`: deploys site

</details>

## Credits

this project was made with [linkml-project-cookiecutter](https://github.com/linkml/linkml-project-cookiecutter)

## Where can we get MIxS specifications?

- Google Sheets (these aren't locked, so somebody could have altered them)
    - [MIxS 6 term updates, MIxS6 packages - Final_clean tab](https://docs.google.com/spreadsheets/d/1QDeeUcDqXes69Y2RjU2aWgOpCVWo5OVsBX9MKmMqi_o/edit#gid=750683809)
    - [MIxS 6 term updates, MIxS6 Core- Final_clean](https://docs.google.com/spreadsheets/d/1QDeeUcDqXes69Y2RjU2aWgOpCVWo5OVsBX9MKmMqi_o/edit#gid=178015749)
- Excel representation, recommend by Chris Hunter.
  - https://github.com/GenomicsStandardsConsortium/mixs/blob/main/mixs/excel/mixs_v6.xlsx
- Chris
  Mungall's [automated LinkML conversion](https://github.com/GenomicsStandardsConsortium/mixs/tree/main/model/schema),
  based on https://github.com/GenomicsStandardsConsortium/mixs/blob/main/gsctools/mixs_converter.py
- [Incomplete schemasheets branch](https://github.com/GenomicsStandardsConsortium/mixs/tree/issue-511-tested-schemasheets/schemasheets)

### Advantages and disadvantages

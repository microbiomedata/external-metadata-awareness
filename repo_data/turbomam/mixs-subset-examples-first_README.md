## Welcome to turbomam/mixs-subset-examples-first!

### This is an attempt to improve the venerable MIxS standard by

- including all refernece material in-line
- creating global definitions of all terms
- mapping GSC's term attributes to LinkML slot attributes
- removing redundancies and contradictions between term attributes
- enabling machine-validation of as many term attributes as possible
- providing sample data files that are clearly either valid or invalid
- bundling the DataHarmonizer schema-based, web-accessible, spreadsheet-like data collection and validation tool

### What does the word "subset" mean in this repo's name? How can I help?

MIxS is a specification of the Minimal Information about any (x) Sequence. It takes a stand on the information that a
submitter should provide when submitting sequence data to a repository like NCBI, EMBL or DDBJ. When data submitters
stick to these standards, their submission are more findable, interoperable and comparable.

The explict elements of MIxS are **terms** (like temperature, pH, primers), **environmental packages** (like soil,
water, plant-associated) and **checklists** (like sequencing of a cultured eukaryote vs sequencing of a metagenome). The
checklists and environmental packages can be **combined** to form specification for a soil sample intended for metgenome
sequencing (MimsSoil), a water sample intended for sequencing of as isolated bacterium (MigsBaWater), etc.

In the LinkML language, the terms are modeled as slots and the environmental packages, checklists and combinations are
modeled as classes that bear slots (variable, fields,attributes, etc.)

We consider the MIxS 6.1 source of trust to
be https://github.com/GenomicsStandardsConsortium/mixs/blob/main/mixs/excel/mixs_v6.xlsx. This workbook has a "MIxS"
sheet that describes terms most closely associated with checklists in a wide format: each term is listed on a single
line, and requirement columns named migs_ba, mims, etc. specify whether the term on that row is required, recommend,
optional, or not applicable to the term on that row. Note that the wod "requirement" doesn't appear anywhere on the
sheet's rows, and that one must consult un-lined data to understand the requirement codes. See for
example https://github.com/GenomicsStandardsConsortium/mixs/wiki/5.-MIxS-checklists. See also this bundled file for the
LinkML interpretation of teh requirement codes: data/mixs_requirement_codes.tsv

- improving the titles for the classes
- improving the descriptions for classes
- adding aliases for classes
    - while the aliases column doesn't provide a space for attribution, these alias should be found relatively commonly
      in the wild. This is not a place to put pet names.
- curating enumerations
    - ideally we would have a minimal number of pure enumerations, with good reuse of enumeration across terms/slots
- pure means that the enumerations are just a list of permissible values, not part of a pattern. compound validations
  like enumeration + count will be dealt with elsewhere
- identify which attributes of a term/slot must be invariant across all classes (name, identifier), and which could be
  customized on a clas-by-class basic (example value, requirement level)
- review data/hand_stacked_conflicts.csv, to obtain
    - global, invariant definitions of each term for ddata/mixs_combined_slotdefs.tsv
    - class-specific customizations of terms on class-by-class basic, for data/hand_stacked_for_slot_usages.csv
    - convert MIxS Value syntaxes (in consultation with other term attributes) into LinkML "settings" for structured
      patterns
    -

sources to consult when resolving conflicts in invariant term attribute associated with different classes

- consensus within the classes
- down-voting variants from the noisiest classes
    - add summary here
- [NCBI's table (or XML model) of  BioSample Attributes](https://www.ncbi.nlm.nih.gov/biosample/docs/attributes/)
- usage of the terms/slots in actual NCBI Biosample records
    - this can be difficult to determine directly from NCBI's website or efetch utilities. We can provide a relational
      database of BioSample attributes to interested parties.

Note that the MIxS standard has been subsetted in one additional way for this code repository: combining the 11 MIxS 6.1
checklists by the 23 environmental packages would yield 253 classes. Dynamically generating all of those combinations is
computationally costly, so we have limited the combination in this demonstration repository to MigsBa and Mims * the
PlantAssociated, Sediment, Soil, and Water environments. Contributors who would like to prioritize the inclusion of some
core combinations, or who would like to devise more efficient ways of working with large numbers of combinations are
encouraged to speak up.

Additionally, this schema is closed: a compliant data set can't provide values for any term that is not already associated with the class that the user has selected to model their samples. In other words, users can't "add their own columns."  MIxS already provides several terms with open-ended semantics. Allowing users to provide values in fields of their own design is a sure way to decrease interoperability with other data sets.  

Cumulative log of
modifications: https://htmlpreview.github.io/?https://raw.githubusercontent.com/turbomam/mixs-subset-examples-first/main/assets/mixs_combined_diff.html

----

## Website

[https://turbomam.github.io/mixs-subset-examples-first](https://turbomam.github.io/mixs-subset-examples-first)

## Repository Structure

* [examples/](examples/) - example data
* [project/](project/) - project files (do not edit these)
* [src/](src/) - source files (edit these)
    * [mixs_subset_examples_first](src/mixs_subset_examples_first)
        * [schema](src/mixs_subset_examples_first/schema) -- LinkML schema
          (edit this)
        * [datamodel](src/mixs_subset_examples_first/datamodel) -- generated
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

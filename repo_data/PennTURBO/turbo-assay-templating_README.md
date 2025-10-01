# turbo-assay-templating
Here's a first step in modelling assays* with terms from [OBO foundry ontologies](http://www.obofoundry.org/). It generates a template that can be executed by the [ROBOT](http://robot.obolibrary.org/) application, leading to an RDF data model. Assays currently in scope have a specimen collected from an organism as the evaluant and can be used in EHR 2ry research or in vivo basic research. We are currently bootstrapping the models from LOINC, but they are not intended for patient care.

Specifically, where we say "assays", healthcare providers might say "lab tests". However, we do not mean to imply that these tests are only relevant in the course of diagnosing disease or planning and monitoring therapy. They would be equally applicable to modelling in vivo research.

## To regenerate the template and then the RDF model

```Bash
cd pipeline
Rscript turbo_assay_template_generation.R
./execute_template.sh
```

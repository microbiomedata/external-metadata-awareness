The files in the `submission-schema` repo's `notebooks/environmental_context_value_sets` directory are
provided as a one step in adding `Extension`-specific environmental context enumerations to the NMDC submission schema.

The `Extensions` (also called Environments, Packages, etc.) are defined in
the [MIxS standard](https://genomicsstandardsconsortium.github.io/mixs/#extensions) and provide guidance about how one
should describe samples from different environmental contexts.

The `submission-schema` captures granular details about the environmental context of a samples with MIxS'
[env_broad_scale](https://genomicsstandardsconsortium.github.io/mixs/0000012/), [env_local_scale](https://genomicsstandardsconsortium.github.io/mixs/0000013/)
and [env_medium](https://genomicsstandardsconsortium.github.io/mixs/0000014/). (Those three fields are informally called
the MIxS environmental triad amongst NMDC staff). Those three slots must be populated with
the name and CURIes for a class in an appropriate ontology. In many cases that ontology is
the [Environmental Ontology](https://environmentontology.org/), EnvO. MIxS and EnvO provide guidance about populating
those context fields, but the guidance is only specific to what classes would reasonably go in which fields. It does not
address what subsets of classes could go in the fields on an Extension-byExtension basis. For example, it would not make
sense to say the ten env_broad_scale of a soil samples was 'ocean biome [ENVO:01000048]'.

We assume that some exploration may have already been done with other tools, followed by human review, 
but these notebooks do not yet consult voting sheets,
such as those created in the external-metadata-awareness repo, like [soil-env_medium.Makefile](https://github.com/microbiomedata/external-metadata-awareness/blob/main/Makefiles/soil-env_medium.Makefile),
which have been [shared as Google Sheets](https://docs.google.com/spreadsheets/d/1qYrUvWK6toajWpadaEJ66X05MjiZ7YAB/edit?gid=502854718#gid=502854718) at times.
They do not [inject the value sets into LinkML YAML files as enumerations](https://github.com/microbiomedata/submission-schema/pull/260) either.

## Generating the env_broad_scale value set for soil samples:

1. Make the `clean` target in the `environmental_context_value_sets.Makefile` in this directory
2. Familiarize yourself with `soil/discover_excludable_soils.ipynb`. It saves a report of relations between soils and
   other EnvO classes as `soil/discover_excludable_soils.tsv`. That file is used later to remove some soil classes
   from the `env_medium` value set for soil samples, if greater inter-study consistency could be achieved by expressing
   some characteristics of the soils in the `env_broad_scale` or `env_local_scale` fields. For example, we want to avoid
   submitters being inconsistent in saying that they have 'garden soil [ENVO:00002263]' samples from a '
   garden [ENVO:00000011]' local contexts vs 'soil [ENVO:00001998]' samples from a 'garden [ENVO:00000011]' local
   context. **Note**: the output of this notebook has been curated and saved as
   `soil/discover_excludable_soils_curated.tsv`. THe curated file includes guidance for some removal or retention that
   are not substantiated but axioms in EnvO as of November 2024. AsInn fact, this file could be a good guide to adding
   missing EnvO axioms. Other notebooks in this repo configured to use the curated file.
3. Run `soil/env_broad_scale/post_google_sheets_soil_env_broad_scale.ipynb` to generate
   `soil/env_broad_scale/post_google_sheets_soil_env_broad_scale.tsv`
4. Familiarize yourself with the inferences about which EnvO classes can be composed together to
   for [GOLD ecosystem paths](https://gold.jgi.doe.gov/ecosystem_classification), as some of them are hard-coded into
   the next `env_local_scale` step. We provide two methods to obtain this
   information and both have system prerequisites. The `gold-soils-by-semsql-wide.tsv` target in
   `soil/gold/gold-soils.Makefile` assumes that `envo.db` and `goldterms.db` have been downloaded
   from https://s3.amazonaws.com/bbop-sqlite/ into this
   project's `local/` directory and that `sqlite` is available on the system path and that `click` and `pandas` are
   available in a Python poetry environment. One can also recreate a file like `soil/gold/gold-soils-by-sparql.tsv` by
   running `soil/gold/gold-soils-by-sparql.rq` against a SPARQL endpoint populated with the datasets in
   `soil/gold/goldterms-with-support-graphs.png` and then pivoting the results.
5. Run `soil/env_local_scale/post_google_sheets_soil_env_local_scale.ipynb` to generate
   the temporary report `soil/env_local_scale/post_google_sheets_soil_env_local_scale_initial.tsv`
   and the final value set `soil/env_local_scale/post_google_sheets_soil_env_local_scale.tsv`
6. Run `soil/env_medium/post_google_sheets_soil_env_medium.ipynb` to generate
   `soil/env_medium/post_google_sheets_soil_env_medium.tsv`. The notebook will indicate which soil classes are being
   excluded based on rows in `soil/discover_excludable_soils_curated.tsv` and
   `soil/env_local_scale/post_google_sheets_soil_env_local_scale.tsv`. This repo also includes
   `soil/env_medium/post_google_sheets_soil_env_medium_retention_justification.tsv` which provides additional
   perspective on gaps or inconsistencies in EnvO.


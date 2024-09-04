## `local/soil-env-local-scale-evidence-table.tsv`

_from `Makefiles/soil-env_local_scale.Makefile`_

- Doesn't include sematic grouping or leveling (eg farm,, agricultural plot, banana plantation, etc)
- Determines which NMDC Biosamples are have `env_package` = 'soil' by machine learning from the environmental triad
  slots, so one could argue that there's some circulatory. The classifications have very high confidence but should
  be reviewed by human experts. The `env_package` values that are used for training have also been lightly curated by
  @turbomam
- Makes some queries against the Postgres Biosample database from later February 2024, which requires a NERSC ssh tunnel
  and `local/.env` file entries
- Which evidence files are included is determined by the `--config` option, which has been set to
- The `all_evidence` column is the average of the `...frequency` columns, followed by 0-1 normalization.
- Some of the evidence, like GOLD, NCBI, NMDC comes with Biosamples counts. Other evidence, like the OAK queries, does
  not. Since the `all_evidence` column is based on frequencies which are based on counts, non-count sources can have
  their frequencies set to 1 (which may overweight them) or to the average of the non-zero values in the other frequency
  columns, by using the `--downsample-uncounted` flag
- Rows that are True for any column whose names begin with `is...` should probably be excluded from prospective value
  sets in the submission-schema. We may want to update the annotation for those Biosamples in NMDC. Or, if we ever put
  constraints on the environmental context slots in nmdc-schema, we may want to include those theoretically
  inappropriate values in teh constraints.
- Rows with an EnvO id that are lacking a label should be discarded. Their claimed ids do not appear in EnvO (as of the
  time the EnvO sematic sql database was downloaded). From what I have seen so far, they come from NCBI records, and
  might be traced back to the submitter trying to drag a legitimate EnvO CURIe down a column in a spreadsheet, but
  incrementing the value on each row without noticing it.
- Rows where the label starts with 'obsolete...' should probably be excluded from prospective value sets
- The normalization of ontology class CURIes is currently limited to curies with the prefix 'ENVO' and the CURIe
  annotation from labels is currently limited to any class in EnvO
- See files like `local/ncbi-mims-soil-biosamples-env_broad_scale-failures.csv` for a record of NCBI Biosample
  annotations that look as if an EnvO CURIe could be parsed out, with some additional development effort. Some of these
  will be recovered thorough label annotation
- `jaccard_distance`s in files like `local/ncbi-mims-soil-biosamples-env_broad_scale-real-labels.csv` may be erroneous (
  see issue ???)
- There's probably potential for templating some of the Makefile targets

## `local/soil-env-broad-scale-evidence-table.tsv`

_from `Makefiles/soil-env_broad_scale.Makefile`_

- all of the notes above should still apply, **except** that the `is_biome` column should ideally be set to 'True' for a
  prospective value set
- ENVO:00000428, 'biome' would itself not be a useful in the value set

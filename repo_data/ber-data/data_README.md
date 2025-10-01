# data

This repository contains data files and related scripts/notebooks used for testing and experimenting with BERtron-related services.

## Inter-repository dependence

> [!IMPORTANT]  
> The map web page (in the [bertron](https://github.com/ber-data/bertron) repository) depends upon the following files in this repository remaining in their current locations:
> - `emsl/map/all_emsl_samples.json`
> - `emsl/map/latlon_project_ids.json`
> - `ess-dive/ess_dive_packages.csv`
> - `jgi/jgi_gold_biosample_geo.csv`
> - `jgi/jgi_gold_organism_geo.csv`
> - `nmdc/nmdc_biosample_geo_coordinates.csv`
>
> Please ensure the map web page has been updated accordingly before you move or delete any of those files.

## Data Ingest Folder Structure and File Naming Conventions

To ensure consistency, efficient validation, and compatibility with the latest release schema, all new data ingest processes must follow these conventions:

### Folder Structure

- All ingested data must reside within the top-level `ingest/` directory.
- Each data provider must have its own subfolder within `ingest/`, e.g.:
  - `ingest/emsl/`
  - `ingest/jgi/`
  - `ingest/ess-dive/`
  - `ingest/nmdc/`

### File Format

- All files must be formatted as JSON lists (i.e., data enclosed in square brackets).
- Each file contains only complete records (entities). No record may be split across files.
- Each record must be independently valid against the current release schema.
- (Future consideration: [JSON Lines](https://jsonlines.org/) format may be adopted if more appropriate for downstream usage.)

### File Size and Splitting

- Each data file should not exceed approximately 25 MB.
- If the dataset is larger, split into multiple files. Do not split individual entity records across files.
- Document the splitting strategy if custom logic is required.

### File Naming Convention

- Files must be named as `<data provider>_<padded 5 digit sequence>.json`
  - Example: `emsl_00001.json`, `jgi_00005.json`
- Numbering must start at `00001` for each provider and increment as needed.

### Example Structure

```
ingest/
  emsl/
    emsl_00001.json
  jgi/
    jgi_00001.json
    jgi_00002.json
  ess-dive/
    ess-dive_00001.json
  nmdc/
    nmdc_00001.json
```

### Additional Notes

- All ingests must support the latest release schema.
- JSON format (list or dict) is specified above; future migrations to JSON Lines will be documented separately.
- No records are to be split between files; each file is independently valid.
- For more information or updates to these conventions, see [issue #9](https://github.com/ber-data/data/issues/9).

## Tools and Scripts for Data Generation

Tools, scripts, notebooks etc. for populating the data (for ingest into MongoDB) from each resouce should live in the contrib directory.
Each data provider has its own subfolder within `contrib/`, e.g.:
  - `contrib/emsl/`
  - `contrib/jgi/`
  - `contrib/ess-dive/`
  - `contrib/nmdc/`


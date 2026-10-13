# Wastewater biosamples in NCBI BioSample

First cut for https://github.com/microbiomedata/external-metadata-awareness/issues/570, Find wastewater biosamples without relying on the NCBI package. Counts measured 2026-10-01 (scan run 2026-09-29) on a local `biosamples_flattened` load of 56,254,160 biosamples whose newest `submission_date` is 2026-05-12.

Reproduce:

```bash
# MONGO_URI is the full URI including the database, e.g. mongodb://localhost:27017/ncbi_metadata
# (add credentials and ?authSource=admin if auth is on; see docs/MONGODB_PATTERNS.md)
mongosh "$MONGO_URI" mongo-js/find_wastewater_biosamples.js    # about 4 min
mongosh "$MONGO_URI" mongo-js/report_wastewater_biosamples.js
```

## Definition

- **Wastewater**: any of `package_content`, `env_package`, `taxonomy_name`, `env_broad_scale`, `env_local_scale`, `env_medium`, `isolation_source` or `description_title` matches `/wast[e]?[ -]?water|sewage|sewer|wwtp|activated[ -]?sludge/i`. Activated sludge was counted as adjacent until 2026-10-01; the recall check below is why it moved.
- **Adjacent**: none of those match, but one matches `/sludge|effluent|influent|digester|biosolid/i`.
- **Wastewater package**: the nine MIxS `*.wastewater.6.0` packages, plus NCBI's `SARS-CoV-2.wwsurv.1.0` and `PHA4GE.wwsurv.1.0`.

## Counts

| set | biosamples |
|---|---|
| wastewater | 503,365 |
| of which matched only by "activated sludge" | 21,857 |
| adjacent only | 75,708 |
| wastewater, MIxS wastewater package | 97,100 |
| wastewater, `SARS-CoV-2.wwsurv.1.0` or `PHA4GE.wwsurv.1.0` | 208,465 |
| wastewater, no wastewater package | 197,800 |

Filtering on package would miss 39.3% of wastewater samples. The largest groups outside a wastewater package are `Generic.1.0` (98,606) and `Metagenome.environmental.1.0` (60,042).

Wastewater samples found by only one field:

| field | found only by this field |
|---|---|
| isolation_source | 44,951 |
| taxonomy_name | 24,387 |
| package_content | 20,720 |
| env_medium | 10,034 |
| description_title | 6,266 |
| env_broad_scale | 3,325 |
| env_local_scale | 2,504 |
| env_package | 312 |

The `package_content` row counts only MIxS wastewater packages, because the `wwsurv` package names do not match the terms.

Most common organisms are "wastewater metagenome" (328,759), "activated sludge metagenome" (26,734) and SARS-CoV-2 (13,224). The largest submitters are EBI (87,047), the US CDC National Wastewater Surveillance System (44,660), Biobot Analytics (30,953) and Verily Life Sciences (28,443).

## env_broad_scale, env_local_scale, env_medium

| field | absent | ENVO id present | distinct values |
|---|---|---|---|
| env_broad_scale | 315,616 | 34,732 | 10,193 |
| env_local_scale | 374,192 | 33,033 | 5,574 |
| env_medium | 315,912 | 33,074 | 9,025 |

- The surveillance packages explain most absences: 208,459 of the 208,465 `wwsurv` samples have no `env_broad_scale`.
- Within MIxS wastewater packages, 25,247 of 97,100 samples (26.0%) have an ENVO id in `env_medium`.
- Most common values: `env_broad_scale` "sewage treatment plant" (37,186), `env_local_scale` "wastewater treatment plant" (7,671), `env_medium` "sewage" (40,325).

## Curation problems

- Facilities in `env_broad_scale`, where a biome belongs: "sewage treatment plant", "wastewater treatment plant".
- Placeholders ("missing", "not applicable", "not collected", "restricted access") on about 10,700 to 11,900 samples per env field.
- Misspelling "wastwater" in `isolation_source` (2,165 samples, plus 12 "WASTWATER").
- Label and id mixed with formatting noise: "waste water [ENVO:00002001 ]", "activated sludge[ENVO_00002046]".
- Several values in one field: "anaerobic digester| wastewater treatment plant".

## Recall check

Checked 2026-09-30 against the 491 BioSamples in the five wastewater BioProjects curated in https://github.com/cmungall/site-kb (`db/raw/research/wastewater_expansion_ena.json`, retrieved 2026-09-23). All 491 are in the local corpus and all 491 are candidates. Under the original terms, 389 matched; the other 102 were all from PRJNA432264 and said only "activated sludge". With activated sludge added, all 491 count as wastewater.

| BioProject | biosamples | wastewater, original terms | wastewater, with activated sludge |
|---|---|---|---|
| PRJNA1012295 | 222 | 222 | 222 |
| PRJNA1149857 | 134 | 134 | 134 |
| PRJNA432264 | 114 | 12 | 114 |
| PRJNA1037153 | 11 | 11 | 11 |
| PRJNA505617 | 10 | 10 | 10 |

PRJNA1037153's 13 runs carry 11 different child study accessions (PRJNA1029202 to PRJNA1029224), so it looks like an umbrella BioProject; its samples are filed under the child projects.

How these studies were chosen isn't recorded here; if they were found by searching for wastewater, this is a weak test of recall.

## MGnify cross-check

Checked 2026-10-01 against the 4,256 samples MGnify files under `root:Engineered:Wastewater` and its child biomes (API v1, `/biomes/root:Engineered:Wastewater/samples`). Every one carries a BioSample accession, and all 4,256 are in the local NCBI corpus, so MGnify adds no samples NCBI lacks.

| tier in this scan | MGnify wastewater samples |
|---|---|
| wastewater, original terms | 3,258 |
| wastewater, "activated sludge" only | 18 |
| adjacent only | 132 |
| not a candidate | 848 |

The 848 have no wastewater, sludge or effluent wording in any of the eight fields. The largest groups are duck (*Anas platyrhynchos*) water and cecal contents (338), "riverine metagenome" stream water (192), pig-manure biogas fermenters (60) and biofilters (48). Reading 20 of them at random (2026-10-01): 3 are sediment from a wastewater treatment plant that the NCBI record names only in `geo_loc_name`; the other 17 are duck farm water and cecal contents, stream water, pig-manure biogas digesters, aquarium-style tanks and biofilters, which look like MGnify filing broader material under wastewater.

## By BioProject

[wastewater-bioprojects.tsv](wastewater-bioprojects.tsv) has one row per BioProject (15,514 rows, plus one for candidates with no BioProject), so a subset can be picked by whole project. Built 2026-10-12 from the same candidates, with the inflow and outflow columns added 2026-10-13:

```bash
mongosh "$MONGO_URI" mongo-js/wastewater_bioproject_table.js > docs/wastewater-bioprojects.tsv
```

The BioProject comes from the BioSample record's own link, or from the SRA run table when the record has none, which is common for EBI samples. A biosample linked to several BioProjects is counted in each row, so each row is that project's full membership and the column sums exceed the totals above. The `in_mgnify` column needs a `mgnify_wastewater_samples` collection, one document per MGnify sample with its BioSample accession in `accession`; without that collection the script still runs and counts every sample as not in MGnify. Fields containing a double quote are quoted, so read the file with a quote-aware TSV reader.

| BioProjects by wastewater biosamples | BioProjects | sum of wastewater biosamples |
|---|---|---|
| any | 9,457 | 446,710 |
| 1 to 9 | 6,455 | 17,040 |
| 10 to 99 | 2,499 | 73,648 |
| 100 to 999 | 447 | 114,981 |
| 1,000 or more | 56 | 241,041 |
| no surveillance-package samples | 9,286 | 237,116 |
| some MGnify wastewater samples | 150 | |

- 444,658 distinct wastewater biosamples have a BioProject; 58,707 (11.7%) have none in either source.
- The largest projects are SARS-CoV-2 surveillance (for example PRJNA839090, Biobot Analytics, 22,153).
- PRJEB13831 (Global surveillance of infectious diseases and antimicrobial resistance from sewage) has 97 wastewater biosamples, 81 of them in MGnify. Those 81 are also in PRJEB23496 (COMPARE global sewage snapshot virome sequencing part).
- PRJNA1037153 from site-kb has no row; its samples are filed under the child projects.

## Inflow and outflow

Inflow here means untreated sewage entering a plant or sampled in the sewer; outflow means effluent. Measured 2026-10-13 on the same 579,073 candidates. Three columns of the BioProject table count them:

- `inflow_ww_sample_matrix`: `ww_sample_matrix` is "raw wastewater" or "post grit removal". 207,072 of the 207,847 biosamples that have this field are in the NCBI `SARS-CoV-2.wwsurv.1.0` package; its other values are "primary effluent", "secondary effluent", "primary sludge", "sewer pipeline sediments" and placeholders.
- `inflow_wording`: any of `env_broad_scale`, `env_local_scale`, `env_medium`, `isolation_source` or `description_title` matches `/influent|inflow|in-flow|raw (sewage|wastewater|waste water)|untreated (sewage|wastewater|waste water)|plant inlet|\binlet\b/i`, except "surface water influent", which is river water.
- `outflow`: `ww_sample_matrix` contains "effluent", or one of those five fields matches `/effluent|outflow|outfall|treated (sewage|wastewater|waste water)|discharge/i`, not counting "untreated".

| set | biosamples |
|---|---|
| inflow by `ww_sample_matrix` | 196,969 |
| inflow by wording | 53,598 |
| inflow by wording only, not by `ww_sample_matrix` | 49,113 |
| inflow by either | 246,082 |
| outflow | 13,426 |
| both inflow and outflow | 36 |

| BioProjects with at least one | BioProjects | sum of biosamples |
|---|---|---|
| inflow by `ww_sample_matrix` | 148 | 196,520 |
| inflow by wording | 507 | 16,310 |
| inflow by wording, no surveillance-package samples | 500 | |
| outflow | 1,280 | 12,781 |

- Most inflow samples come from the surveillance package; the largest such project is PRJNA839090 (Biobot Analytics, 22,008 by `ww_sample_matrix`).
- Outside those packages the largest inflow projects are PRJNA1247874 (CASPER metagenomic sequencing, 1,729), PRJNA966185 (Baylor, 808), PRJNA729801 (Southern California metatranscriptomes, 640) and PRJEB53227 (614).
- 37,300 of the wording matches have no BioProject. 37,057 of those are EBI samples in `Generic.1.0` titled "European sewage" with `isolation_source` "untreated sewage"; none has a BioProject link or an SRA run in the local copy.
- Outflow wording also catches bioreactor and biofilter effluent, palm oil mill effluent, hospital effluent and "ileostomy effluent", so read the outflow column as samples to drop from an inflow set, not as treatment-plant effluent.

## Limits

- Precision was checked by eye on 25 random wastewater samples outside any wastewater package, under the original terms: 23 were wastewater or treatment-plant samples; 2 matched on fields not reviewed. The 21,857 samples that match only "activated sludge" were checked separately on 50 random samples (2026-10-01, one reader, judged from the record's own fields): 2 state a treatment plant, 9 a lab or pilot reactor, microcosm or experiment, 12 are genomes derived from activated sludge with no setting given, and 27 give no setting. So this row cannot be read as treatment-plant samples; exclude it if lab reactors should not count. The terms also catch hospital wastewater and industrial effluent.
- `geo_loc_name` is not scanned. 556 biosamples name a treatment plant or sewer only there (for example "USA: Altavista Wastewater Treatment Plant, Altavista, Virgina"), some of them river samples upstream or downstream of a plant.
- Not yet run against the BERDL (KBase BER Data Lakehouse) copy of NCBI BioSample.
- The value sets that would fix the env fields are requested in https://github.com/microbiomedata/submission-schema/issues/486, Add wastewater value sets for env_broad_scale, env_local_scale and env_medium.

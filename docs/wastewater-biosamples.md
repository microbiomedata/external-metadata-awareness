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

### Sample names

Some submitters mark flow only in the BioSample sample name: PRJNA1224513 says "Wastewater treatment plant" in `isolation_source`, and influent only in names like "JNW-IN_Virome". Two more columns count this (measured 2026-10-13; 383,097 of the 579,073 candidates have a sample name, from `biosamples_ids` label "Sample name"):

- `inflow_sample_name`: the name matches the inflow regex, or has a separate token IN, INF, INFL, Inf or Infl (no letter on either side; case-sensitive).
- `outflow_sample_name`: the name matches the outflow regex, or has a token EF, EFF, Eff or OUT.

```bash
mongosh "$MONGO_URI" mongo-js/wastewater_sample_name_flow_check.js
```

checks each name rule against the field-based flags. "Agree" means the fields say the same flow, "disagree" only the other one, "new" neither. The last column leaves out samples with no BioProject.

| name rule | agree | disagree | new | agreement % | without the largest project % |
|---|---|---|---|---|---|
| inflow tokens | 5,374 | 27 | 683 | 99.5 | 97.5 |
| inflow words | 403 | 3 | 94 | 99.3 | 99.1 |
| outflow tokens | 469 | 11 | 913 | 97.7 | 99.4 |
| outflow words | 374 | 0 | 114 | 100.0 | 100.0 |
| RAW, Raw, RW tokens (not used) | 488 | 106 | 176 | 82.2 | 73.2 |

- One project carries the inflow tokens: PRJNA938474 (OHA/OSU wastewater project, names like "ALB-Inf-3-29-23-A") holds 4,591 of the 5,374 agreements.
- "Influent" can mean the influent to one treatment step. In two water reclamation projects, names like "O3_INF" and "SE1_Inf" appear to mark the feed to an ozone or filter step, while the fields say effluent; PRJNA749122's `isolation_source` is "Liquid sample from filtered secondary wastewater effluent" (PRJNA849266, 14 samples; PRJNA749122, 6).
- Some records contradict themselves: PRJNA1083020 (CIWARS) names samples "..._EFF_..." with `isolation_source` "influent sewage" (9 samples).
- RAW disagrees mostly in PRJNA951863, where "Raw1_bin" is a genome bin from palm oil mill effluent sludge.
- Sample names add 777 inflow and 1,027 outflow samples that the fields say nothing about. Inflow by fields or name is 246,889: the 246,082 from fields, the 777, and 30 samples whose name says inflow while the fields say outflow. 82 BioProjects have inflow only by sample name (704 samples).
- `wastewater_flow_labels` keeps one document per candidate with every flag, for training a subtype classifier (https://github.com/microbiomedata/external-metadata-awareness/issues/580).

## Subtype classifier, first baseline

A first try at https://github.com/microbiomedata/external-metadata-awareness/issues/580 scope item 3, run 2026-10-13:

```bash
MONGO_URI=... poetry run wastewater-subtype-classifier --out-dir local/wastewater_subtype/<date> --hold-out docs/wastewater-subtype-handchecked-2026-10-13.tsv
```

Labels come from rules: inflow and effluent from `wastewater_flow_labels`, plus sludge (`sludge|mixed liquor|biosolid`), digester (`digest(er|or|ate|ion)|biogas`, which wins over sludge) and sewer (`sewer`, `manhole`, `sewershed`, pump or lift station). The rule words are removed from the text before training, so the model has to learn from the rest of the record. The model is one logistic regression per subtype, on word unigrams and bigrams (letters only, so it can't memorize sample-ID patterns), from `env_broad_scale`, `env_local_scale`, `env_medium`, `isolation_source`, `description_title` and the sample name.

Evaluation holds out 20% of BioProject groups, plus every group that holds a hand-checked sample (132,622 of 579,073 samples; seed 0). BioProjects that share a sample form one group, named by its smallest accession so the split doesn't depend on input order, and the 65,712 samples with no BioProject are used for training only. An earlier run that split those samples one by one put near-identical "European sewage" records on both sides and reported inflow F1 0.817 outside the surveillance package; with them kept out of the test set it is 0.08 to 0.15, depending on the split.

| subtype | rule labels | held-out groups with a positive | held-out F1 | held-out F1, no surveillance package | unlabeled samples predicted at 0.8 |
|---|---|---|---|---|---|
| inflow | 246,889 | 155 | 0.892 | 0.082 | 12,118 |
| effluent | 14,464 | 265 | 0.120 | 0.149 | 11,673 |
| sludge | 119,364 | 1,376 | 0.779 | 0.781 | 4,169 |
| digester | 40,568 | 520 | 0.855 | 0.855 | 382 |
| sewer | 5,964 | 26 | 0.048 | 0.134 | 449 |

Reading each subtype's 200 highest-scoring unlabeled samples in an earlier run with the same features (one reader, 8 random ones each plus counts):

- Inflow: 197 of 200 are SARS-CoV-2 surveillance samples without `ww_sample_matrix`. The model learned that surveillance means inflow, which may be true but is not evidence, and it does not carry inflow to other projects.
- Effluent: finds rule gaps, such as "A secondary Aug14" and river water downstream of a plant, but also "Incoming wastewater from a wastewater treatment plant, after removal of large particulate matter", which is inflow the inflow rule misses.
- Digester: mostly anaerobic digesters and reactors ("Mesophilic AD", "Anaerobic reactor"), plus food waste.
- Sludge: treatment-plant and EBPR or anammox reactor biomass, plus one stool sample.
- Sewer has too few projects to train or test.

Against the rules, sludge and digester transfer to unseen projects and inflow, effluent and sewer do not. The hand-checked set below tests the samples the rules don't decide, and there only digester and sewer hold up.

### Hand-checked set

[wastewater-subtype-handchecked-2026-10-13.tsv](wastewater-subtype-handchecked-2026-10-13.tsv) holds 300 held-out samples that the rules leave unlabeled, labeled by reading each record against [wastewater-subtype-labeling-guide.md](wastewater-subtype-labeling-guide.md), which was written before any sample was read. For each subtype, 25 come from classifier scores of 0.8 or more, 15 from 0.5 to 0.8 and 10 from 0.2 to 0.5, plus 50 at random, with at most 3 per BioProject group in a band. The labeling sheet had no scores on it. The scores in the file come from the run that drew the set (head a84ac04, before group names were made order-independent); later runs keep these samples in the test set through `--hold-out`.

```bash
MONGO_URI=... poetry run wastewater-subtype-labeling sample --predictions <run>/held_out_predictions.tsv --sheet sheet.tsv --key key.tsv
poetry run wastewater-subtype-labeling score --sheet labeled.tsv --key key.tsv [--other second_labeled.tsv]
# reproduce the table below from the committed file
poetry run wastewater-subtype-labeling score --sheet docs/wastewater-subtype-handchecked-2026-10-13.tsv --label-column labels_first \
  --key docs/wastewater-subtype-handchecked-2026-10-13.tsv --other docs/wastewater-subtype-handchecked-2026-10-13.tsv --other-column labels_second
```

Both labelers are language models: the first was Claude in the working session, the second a separate Claude model with only the guide and the sheet. They gave the same label to 279 of 300 samples (Cohen's kappa 0.88), including all 4 inflow and all 4 effluent samples. Most disagreements were "unclear" against a subtype. A person has not yet checked them.

First labeler's counts: unclear 191, none 47, sludge 24, digester 17, sewer 13, inflow 4, effluent 4. Of the 50 random samples, 33 are unclear, 13 none, 3 sludge and 1 sewer, so most samples the rules miss carry too little in the record to decide.

Classifier against the first labeler, at a score of 0.5:

| subtype | hand positives | predicted | predicted but unclear | correct | precision, unclear counted wrong | precision among decided | recall |
|---|---|---|---|---|---|---|---|
| inflow | 4 | 53 | 52 | 0 | 0.00 | 0.00 | 0.00 |
| effluent | 4 | 90 | 59 | 1 | 0.01 | 0.03 | 0.25 |
| sludge | 24 | 92 | 54 | 7 | 0.08 | 0.18 | 0.29 |
| digester | 17 | 42 | 14 | 16 | 0.38 | 0.57 | 0.94 |
| sewer | 13 | 45 | 29 | 10 | 0.22 | 0.63 | 0.77 |

Scoring the rerun with `--hold-out` (`--key <run>/held_out_predictions.tsv`) gives similar results: precision among decided samples 0.59 for digester, 0.75 for sewer, 0.21 for sludge, 0.12 for effluent, and no decided inflow predictions.

These are on a sample drawn mostly from high scores, so they describe the score bands, not the corpus. In the top band (0.8 or more), 13 of 25 digester picks are digesters and 6 of 25 sewer picks are sewer samples. None of the 25 inflow picks is inflow (all unclear), and 11 of 25 sludge picks are not wastewater: compost (4), crude oil enrichments (3), growth medium (2), a plasmid stock and a pit latrine. Sludge scored F1 0.78 against the rules but has 0.18 precision among decided samples here, so agreement with the rules says little about samples the rules don't decide.

## Limits

- Precision was checked by eye on 25 random wastewater samples outside any wastewater package, under the original terms: 23 were wastewater or treatment-plant samples; 2 matched on fields not reviewed. The 21,857 samples that match only "activated sludge" were checked separately on 50 random samples (2026-10-01, one reader, judged from the record's own fields): 2 state a treatment plant, 9 a lab or pilot reactor, microcosm or experiment, 12 are genomes derived from activated sludge with no setting given, and 27 give no setting. So this row cannot be read as treatment-plant samples; exclude it if lab reactors should not count. The terms also catch hospital wastewater and industrial effluent.
- `geo_loc_name` is not scanned. 556 biosamples name a treatment plant or sewer only there (for example "USA: Altavista Wastewater Treatment Plant, Altavista, Virgina"), some of them river samples upstream or downstream of a plant.
- Not yet run against the BERDL (KBase BER Data Lakehouse) copy of NCBI BioSample.
- The value sets that would fix the env fields are requested in https://github.com/microbiomedata/submission-schema/issues/486, Add wastewater value sets for env_broad_scale, env_local_scale and env_medium.

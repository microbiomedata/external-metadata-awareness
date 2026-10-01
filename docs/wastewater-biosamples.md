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

## Limits

- Precision was checked by eye on 25 random wastewater samples outside any wastewater package, under the original terms: 23 were wastewater or treatment-plant samples; 2 matched on fields not reviewed. The 21,857 samples added by activated sludge were not spot-checked. The terms also catch hospital wastewater and industrial effluent.
- Not yet run against the BERDL (KBase BER Data Lakehouse) copy of NCBI BioSample.
- The value sets that would fix the env fields are requested in https://github.com/microbiomedata/submission-schema/issues/486, Add wastewater value sets for env_broad_scale, env_local_scale and env_medium.

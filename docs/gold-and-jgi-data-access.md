# GOLD and JGI Data Access — Consolidated Reference

> **Canonical location:** This is the single source of truth for how to access GOLD metadata and other JGI data.
> All other docs should point here rather than duplicating this content.
>
> Previous versions lived in `sample-annotator/gold-knowledge-management.md` and
> `external-metadata-awareness/docs/gold-knowledge-management.md`. Both now redirect here.

**Last updated:** 2026-03-26

---

## Table of Contents

- [Recommended: JGI Dremio Data Lakehouse](#recommended-jgi-dremio-data-lakehouse)
- [GOLD APIs (Two Distinct APIs)](#gold-apis-two-distinct-apis)
  - [Public GOLD Swagger API](#1-public-gold-swagger-api)
  - [NMDC-Specific GOLD API](#2-nmdc-specific-gold-api)
- [Other GOLD Access Methods](#other-gold-access-methods)
- [What NMDC Uses in Production](#what-nmdc-uses-in-production)
- [The EMA Flattening Pipeline (When You Still Need It)](#the-ema-flattening-pipeline)
- [Non-GOLD JGI Data in the Lakehouse](#non-gold-jgi-data-in-the-lakehouse)
- [JGI Data NOT in the Lakehouse](#jgi-data-not-in-the-lakehouse)
- [Authentication Reference](#authentication-reference)
- [Related Repos](#related-repos)
- [GOLD Ecosystem Classification](#gold-ecosystem-classification)
- [GOLD Date/Provenance Fields](#gold-dateprovenance-fields)

---

## Recommended: JGI Dremio Data Lakehouse

The **JGI Dremio data lakehouse** is the preferred way to access GOLD metadata at scale.
It provides direct SQL access to GOLD's relational tables without the single-ID query
limitations of the GOLD APIs.

| Detail | Value |
|--------|-------|
| URL | `https://lakehouse.jgi.lbl.gov` |
| Auth | `DREMIO_USER` / `DREMIO_PASSWORD` + Cloudflare Access cookie (`CF_AUTHORIZATION`) |
| GOLD tables | `"gold-db-2 postgresql".gold.study`, `.biosample`, `.organism_v2`, `.analysis_project` |
| Sequencing projects | `"img-db-2 postgresql".img_gold.gold_sequencing_project` (different source) |
| Isolate submissions | `"gold-db-2 postgresql".gold.dw_samples` JOIN `dw_sample_taxonomy_info` ON `sample_id` |

```sql
-- Example: all GOLD biosamples
SELECT * FROM "gold-db-2 postgresql".gold.biosample LIMIT 10

-- Example: isolate sample with taxonomy
SELECT s.*, t.*
FROM "gold-db-2 postgresql".gold.dw_samples s
JOIN "gold-db-2 postgresql".gold.dw_sample_taxonomy_info t
  ON s.sample_id = t.sample_id
LIMIT 10
```

### Lakehouse Limitations

- **Cloudflare Access cookie** has a limited lifetime (hours to days). Extract from browser DevTools > Application > Cookies > `CF_Authorization`. No programmatic refresh exists yet.
- **Flight SQL port 32010 is blocked** — only REST API via HTTPS works. This means `ibis` cannot connect directly.
- **Missing env triad fields:** `env_broad_scale`, `env_local_scale`, `env_medium` are **not present** in the Dremio GOLD tables. These fields are only available via the NMDC-specific GOLD API (see below).
- **organism_v2 gotchas:** Boolean columns are stored as VARCHAR (`"Yes"/"No"/"Unknown"`), not actual booleans. The `sample_oid` column is NULL for all rows, breaking the join to `dw_samples`.
- **Junction tables** for multi-valued attributes (metabolism, habitat, disease, etc.) are keyed by `organism_id`. There are 8 of them: `organism_biotic_rel`, `organism_cell_arrangement`, `organism_disease`, `organism_energy_source`, `organism_habitat`, `organism_metabolism`, `organism_phenotype`, `organism_body_product`.
- **The lakehouse is in demo state** (per Georg Rath, Feb 2026) — not yet suitable for production external-facing services.

### Tools for Lakehouse Access

| Tool | Repo | Notes |
|------|------|-------|
| Minimal Python client | [turbomam/jgi-dremio-exploration](https://github.com/turbomam/jgi-dremio-exploration) | Two-stage auth (Dremio login + CF cookie), async job polling, JSONL/TSV export |
| Claude Code skills | [cmungall/lakehouse-skills](https://github.com/cmungall/lakehouse-skills) | `jgi-lakehouse` and `kbase-lakehouse-analysis` skills |
| linkml-store | [linkml/linkml-store](https://github.com/linkml/linkml-store) | Unified access with `linkml-store[dremio]` extra. CLI: `linkml-store -d "dremio-rest://..." -c study query --limit 10` |
| Inferred LinkML schemas | [cmungall/bridge-schemas](https://github.com/cmungall/bridge-schemas) | `gold.linkml.yaml` (31 FKs), `img_gold.linkml.yaml` (72 tables, 14 FKs), auto-generated from Dremio |

### Dremio Authentication Details

**Two Dremio instances:**
- **Production** (`lakehouse.jgi.lbl.gov`) — behind Cloudflare Access gate. Requires `CF_AUTHORIZATION` cookie.
- **POC/Staging** — no Cloudflare gate (when available).

**Two login methods:**
- Dremio native username/password (`DREMIO_USER` / `DREMIO_PASSWORD`)
- SSO via JGI Staff Keycloak or LBL Identity

**Getting `CF_AUTHORIZATION`:**
1. Open `https://lakehouse.jgi.lbl.gov` in a browser
2. Authenticate through Cloudflare Access (LBL identity)
3. Browser DevTools > Application > Cookies > `CF_Authorization`
4. Copy the value into your `.env` file

**Python auth pattern:**
```python
import requests

# Step 1: Dremio login
headers = {"Cookie": f"CF_Authorization={cf_auth}"}
login_resp = requests.post(
    "https://lakehouse.jgi.lbl.gov/apiv2/login",
    json={"userName": dremio_user, "password": dremio_password},
    headers=headers
)
token = login_resp.json()["token"]

# Step 2: Submit SQL job
headers["Authorization"] = f"_dremio{token}"
job_resp = requests.post(
    "https://lakehouse.jgi.lbl.gov/api/v3/sql",
    json={"sql": 'SELECT * FROM "gold-db-2 postgresql".gold.study LIMIT 5'},
    headers=headers
)
# Step 3: Poll for results...
```

---

## GOLD APIs (Two Distinct APIs)

GOLD exposes two separate REST APIs. They are often confused but serve different purposes
and use different authentication.

### 1. Public GOLD Swagger API

| Detail | Value |
|--------|-------|
| Base URL | `https://gold-ws.jgi.doe.gov` |
| Swagger UI | `https://gold-ws.jgi.doe.gov/swagger-ui/index.html` |
| Auth | None required for public endpoints |
| Tech stack | Spring Boot, Keycloak-backed (but public endpoints are unauthenticated) |

**Endpoints:** `/biosamples`, `/studies`, `/projects`, `/analysisProjects`, `/organisms`

**Critical limitation:** Only supports queries where a **single ID** is provided:
```
GET /biosamples?studyGoldId=Gs0000008
```
- No filtering by metadata fields (ecosystem, location, dates)
- No pagination
- No bulk download
- No Boolean OR queries

**What it's good for:** Looking up metadata for a specific known GOLD entity by ID.

### 2. NMDC-Specific GOLD API

| Detail | Value |
|--------|-------|
| Base URL | `https://gold.jgi.doe.gov/rest/nmdc` |
| Auth | **HTTP Basic Auth** with NMDC-shared credentials |
| Documentation | [Google Doc](https://docs.google.com/document/d/1PgrFYmc7AU7Kd5Dtg-xbpAyC6ZcLw4ChFwg3bHV1JQg/edit?tab=t.0) (not public) |

**Endpoints:**
```
GET /rest/nmdc/biosamples?studyGoldId=Gs0114675
GET /rest/nmdc/biosamples?itsProposalId=1777
GET /rest/nmdc/projects?studyGoldId=Gs0114675
GET /rest/nmdc/studies?studyGoldId=Gs0114675
GET /rest/nmdc/analysisProjects?studyGoldId=Gs0114675
```

**Same ID-based restriction** as the public API — no bulk, no filtering, no pagination.

**Why it exists:** This API returns fields that the public API and Dremio do **not** provide,
most importantly the **MIxS environmental context triad**:
- `envBroadScale` (env_broad_scale)
- `envLocalScale` (env_local_scale)
- `envMedium` (env_medium)

**Authentication:** HTTP Basic Auth using shared NMDC credentials. The credentials are stored
in `config/gold-key.txt` (in the `sample-annotator` repo) or as `GOLD_API_USERNAME` /
`GOLD_API_PASSWORD` environment variables (in `nmdc-runtime`).

**This is what NMDC uses in production** — see below.

---

## Other GOLD Access Methods

### GOLD Website

- URL: [https://gold.jgi.doe.gov/](https://gold.jgi.doe.gov/)
- Manual filtering on select field combinations
- No programmatic interface, no bulk export, no Boolean OR
- Useful for browsing and visual inspection only

### Public Excel Download (`goldData.xlsx`)

- URL: [https://gold.jgi.doe.gov/download?mode=site_excel](https://gold.jgi.doe.gov/download?mode=site_excel)
- ~200MB, 6 tabs: Readme, Study, Biosample, Organism, Sequencing Project, Analysis Project
- **Missing:** env_broad_scale, env_local_scale, env_medium
- Extremely slow in LibreOffice on Linux
- No incremental updates, no provenance, no versioning

### Other GOLD Downloads

```
https://gold.jgi.doe.gov/download?mode=ecosystempaths           # ecosystem path tree
https://gold.jgi.doe.gov/download?mode=biosampleEcosystemsJson  # biosample ecosystem JSON
https://gold.jgi.doe.gov/download?mode=organismEcosystemsJson   # organism ecosystem JSON
```

---

## What NMDC Uses in Production

**nmdc-runtime uses the NMDC-specific GOLD API exclusively. It does NOT use Dremio.**

| Component | What it does | GOLD access method |
|-----------|-------------|-------------------|
| `GoldApiClient` (`resources.py`) | HTTP Basic Auth client for the NMDC-specific API | `https://gold.jgi.doe.gov/rest/nmdc` |
| `gold_study_to_database` graph (`graphs.py`) | Dagster ETL: fetches GOLD study + biosamples + projects, translates to NMDC | NMDC-specific API |
| `GoldStudyTranslator` (`gold_translator.py`) | Filters to Metagenome/Metatranscriptome strategies, mints NMDC IDs | Consumes API output |
| `DatabaseUpdater` (`database_updater.py`) | Repair tool: fills missing biosample/data_generation records | NMDC-specific API |
| `gold.py` (validation) | Validates translated GOLD data in `nmdc_etl_staging` MongoDB | No direct GOLD access |
| `gold.py` (normalization) | Normalizes GOLD IDs to `gold:` CURIE format | No direct GOLD access |
| nmdc-server (data portal) | Stores GOLD identifiers, generates "Open in GOLD" links | No direct GOLD access (links to gold.jgi.doe.gov UI) |

**Key implication:** If NMDC were to migrate to Dremio for GOLD access, it would need to
solve the missing env triad fields problem, since those are currently only available through
the NMDC-specific API.

### NMDC's GOLD Ingestion Pipeline (via sample-annotator)

For bulk loading (not production ingest), there is a separate pipeline in the
[sample-annotator](https://github.com/microbiomedata/sample-annotator) repo:

| Tool | What it does |
|------|-------------|
| `gold_tool.py` (preferred) | Unified CLI: API ingestion -> diskcache -> MongoDB. Handles credentials, resume, batch-size. |
| `gold_client.py` (legacy, Chris Mungall) | Monolithic JSON output via diskcache. ~3 sec/study, ~2.5 days for 63k studies. **No longer preferred.** |

Both use `config/gold-key.txt` for HTTP Basic Auth credentials against the NMDC-specific API.

The `gold_tool.py` pipeline populates the `gold_metadata` MongoDB database:
| Collection | Key Field | Records |
|------------|-----------|---------|
| `studies` | `studyGoldId` | ~4,700 |
| `biosamples` | `biosampleGoldId` | ~217,000 |
| `seq_projects` | `projectGoldId` | ~221,000 |
| `study_import_failures` | `studyGoldId` | Error traces |

---

## The EMA Flattening Pipeline

After GOLD data is loaded into MongoDB (via `sample-annotator`), the
`external-metadata-awareness` repo provides enrichment and normalization.

**When you still need this (i.e., when Dremio is not enough):**
- You need CURIE-normalized identifiers (e.g., `ENVO_01000339` -> `ENVO:01000339`)
- You need canonical ontology labels looked up via OAK (ENVO, PO, UBERON)
- You need obsolete term flagging
- You need MIxS-style standardized field names for environmental triads
- You need flattened, tabular documents from nested GOLD JSON

**Makefile targets:**
```bash
make -f Makefiles/gold.Makefile flatten-gold-biosamples    # -> flattened_biosamples + flattened_biosample_contacts
make -f Makefiles/gold.Makefile flatten-gold-studies        # -> flattened_studies + flattened_studies_contacts
make -f Makefiles/gold.Makefile flatten-gold-seq-projects   # -> flattened_seq_projects + contacts/publications/experiments
make -f Makefiles/gold.Makefile export-gold-flattened-csv   # -> local/csv_exports/
```

**Note:** GOLD scripts use `--dotenv-path` (not `--env-file` like other EMA CLIs).
Issue [#332](https://github.com/microbiomedata/external-metadata-awareness/issues/332) tracks unifying this.

---

## Non-GOLD JGI Data in the Lakehouse

The JGI Dremio lakehouse exposes far more than GOLD. Here is what's available,
with notes on NMDC relevance.

### IMG (Integrated Microbial Genomes) — High NMDC Relevance

All under `img-db-2 postgresql.*`:

| Schema | Tables | FKs | Contents | NMDC relevance |
|--------|--------|-----|----------|---------------|
| `img_core_v400` | 244 | 141 | Genes, taxons, scaffolds, COG/Pfam annotations | High — functional annotations |
| `img_ext` | 84 | 80 | Pathways, secondary metabolite clusters, comparative genomics | Medium |
| `img_gold` | 72 | 14 | IMG-to-GOLD integration/linking tables | High — cross-references |
| `img_sat_v450` | 141 | 127 | Experimental data, expression profiles, phenotypes | Low-Medium |
| `img_sub` | 49 | — | Genome submission system | Low |
| `imgsg_dev` | 254 | 38 | IMG development database | Low |
| `img_i_taxon` | 8 | — | Taxonomy data | Medium |
| `img_methylome` | 10 | — | Methylome experiments | Low |
| `img_proteome` | 15 | — | Proteomics | Medium |
| `img_rnaseq` | 11 | — | RNA-seq experiments | Medium |

IMG MySQL databases (`img-db-1 mysql.*`, no FK metadata):

| Schema | Tables | Contents | NMDC relevance |
|--------|--------|----------|---------------|
| `abc` | 18 | ABC transporter data | Low |
| `img` | 5 | Core IMG | Low |
| `imgvr_prod` | 7 | IMG/VR viral genomes | Medium |
| `mbin` | 17 | Metagenome binning | High |
| `misi` | 5 | Microbial signatures | Low |

### JGI Portal

`portal-db-1.portal` — thin submission tracker (userId, sampleId, dates).
Key-value `sampleMetadata` store. Not structured biological data.

### Other Schemas

| Schema | Contents | NMDC relevance |
|--------|----------|---------------|
| `sdm_metadata` | Scientific Data Management (analysis templates, publishing flags) | Low |
| `smc` | Biosynthetic gene clusters (BGCs) | Medium |
| `mycocosm` | Fungal genomics portal | Low |
| `phytozome` | Plant genomics portal | Low |
| `gcs_citation` | Citation/document metadata | Low |
| `numg` | 9 tables, not sample-related | None |

### Inferred Schemas

[cmungall/bridge-schemas](https://github.com/cmungall/bridge-schemas) has auto-generated
LinkML schemas for all the above, introspected from Dremio via `linkml-store`.

---

## JGI Data NOT in the Lakehouse

These exist on JGI's side but are **not exposed** through Dremio:

| Data | Description | Why it matters |
|------|-------------|---------------|
| `ribosomal_sequence` table | 16S/ITS/28S actual sequence strings, keyed by `sample_id` | Needed for isolate identification. Confirmed by Alicia Clum. |
| `sample_tissue_contact` table | Sample tissue and contact info | Useful for provenance tracking. |
| JAMO (JGI Archive and Metadata Organizer) | JGI's internal data archive system | Not relevant for metadata, but holds raw data files. |
| Organism-to-sample join | `organism_v2.sample_oid` is NULL for all rows | Prevents linking host/ecosystem metadata to isolate submissions. |

---

## Authentication Reference

| Access Method | Auth Type | Credentials | Where Stored |
|---------------|-----------|-------------|-------------|
| **JGI Dremio lakehouse** | Dremio login + Cloudflare cookie | `DREMIO_USER`, `DREMIO_PASSWORD`, `CF_AUTHORIZATION` | `~/.env` or project `.env` |
| **NMDC-specific GOLD API** | HTTP Basic Auth | `GOLD_API_USERNAME`, `GOLD_API_PASSWORD` (nmdc-runtime) or `config/gold-key.txt` (sample-annotator) | nmdc-runtime: Dagster resource config; sample-annotator: file |
| **Public GOLD Swagger API** | None | — | — |
| **GOLD Excel download** | None | — | — |
| **GOLD website** | None (optional JGI SSO for some features) | — | — |
| **KBase/BERDL lakehouse** (for comparison) | Bearer token | `KBASE_TOKEN` (expires weekly) | `~/.env` or project `.env` |
| **NMDC Submission Portal API** | OAuth2 (ORCID) refresh token | `NMDC_DATA_SUBMISSION_REFRESH_TOKEN` | `local/.env.nmdc-submissions` |

---

## Related Repos

### GOLD Data Pipeline (this repo's ecosystem)

| Repo | Role in the pipeline |
|------|---------------------|
| [microbiomedata/sample-annotator](https://github.com/microbiomedata/sample-annotator) | **Upstream:** `gold_tool.py` fetches GOLD via NMDC API -> MongoDB |
| [microbiomedata/external-metadata-awareness](https://github.com/microbiomedata/external-metadata-awareness) | **This repo:** Flattens, enriches, normalizes GOLD (and NCBI/SRA) metadata |
| [microbiomedata/nmdc-runtime](https://github.com/microbiomedata/nmdc-runtime) | **Downstream consumer:** `GoldStudyTranslator` ingests GOLD studies into NMDC production |
| [microbiomedata/nmdc-schema](https://github.com/microbiomedata/nmdc-schema) | **Downstream consumer:** GOLD-to-MIxS SSSOM mappings, identifier patterns, gold_path_field slots |
| [microbiomedata/submission-schema](https://github.com/microbiomedata/submission-schema) | **Downstream consumer:** Env triad value sets generated from EMA voting sheets |

### Lakehouse/Dremio Access

| Repo | What it provides |
|------|-----------------|
| [turbomam/jgi-dremio-exploration](https://github.com/turbomam/jgi-dremio-exploration) | Minimal Python Dremio client with two-stage auth |
| [cmungall/lakehouse-skills](https://github.com/cmungall/lakehouse-skills) | Claude Code skills for querying both JGI and KBase lakehouses |
| [cmungall/bridge-schemas](https://github.com/cmungall/bridge-schemas) | Auto-generated LinkML schemas from Dremio introspection |
| [linkml/linkml-store](https://github.com/linkml/linkml-store) | Unified access layer with `[dremio]` extra |

### GOLD Ontology/Classification

| Repo | What it provides | Status |
|------|-----------------|--------|
| [cmungall/gold-ontology](https://github.com/cmungall/gold-ontology) | OWL translation of GOLD ecosystem classification | Active (Chris) |
| [microbiomedata/GOLD-ontology-translation](https://github.com/microbiomedata/GOLD-ontology-translation) | Earlier env level -> ontology translation | **Dormant since 2020** |
| [contextualizer-ai/gold-tools](https://github.com/contextualizer-ai/gold-tools) | GOLD API tools | Low activity |

### Other Related

| Repo | Relationship |
|------|-------------|
| [microbiomedata/nmdc-ai-eval](https://github.com/microbiomedata/nmdc-ai-eval) | Eval datasets sourced from EMA; GOLD ecosystem fields excluded from prediction inputs |
| [microbiomedata/nmdc-metadata-suggestor-ai-tool](https://github.com/microbiomedata/nmdc-metadata-suggestor-ai-tool) | Test data provenance traces to EMA |
| [berkeleybop/contextualizer](https://github.com/berkeleybop/contextualizer) | Lat/lon-based metadata inference, conceptual overlap with env triad enrichment |
| [berkeleybop/metpo](https://github.com/berkeleybop/metpo) | METPO ontology with GOLD field analysis |
| [contextualizer-ai/to-duckdb](https://github.com/contextualizer-ai/to-duckdb) | MongoDB -> DuckDB framework used by EMA |
| [INCATools/biosample-analysis](https://github.com/INCATools/biosample-analysis) | Biosample metadata analysis |

---

## GOLD Ecosystem Classification

GOLD uses a 5-level hierarchical ecosystem classification with ~2,400 valid paths
observed across ~231,704 biosamples:

1. `ecosystem` (e.g., Environmental, Host-associated, Engineered)
2. `ecosystem_category` (e.g., Aquatic, Terrestrial, Human)
3. `ecosystem_type` (e.g., Freshwater, Soil, Digestive system)
4. `ecosystem_subtype` (e.g., Lake, Forest soil, Large intestine)
5. `specific_ecosystem` (e.g., Unclassified, Sediment)

**Key facts:**
- GOLD biosamples are 100% populated for ecosystem fields
- NMDC has 14,938 biosamples; 92% have ecosystem data (107 distinct paths, 8 invalid paths affecting 1,021 biosamples)
- NMDC submissions are ~74% empty for ecosystem fields
- The ecosystem tree JSON is downloadable from `gold.jgi.doe.gov/download?mode=biosampleEcosystemsJson`
- In nmdc-schema: all 5 slots are optional, no enums, no cross-field validation rules
- In submission-schema: recommended, with flat per-level enums built from the GOLD JSON tree
- The SSSOM lexical mappings between GOLD ecosystem terms and ENVO/MIxS are in `external-metadata-awareness/lexmatch-output/`
- OWL translations by Bill Duncan and Chris Mungall in [cmungall/gold-ontology](https://github.com/cmungall/gold-ontology)

**Relationship to MIxS env triad:** The GOLD 5-tuple and MIxS env triad (env_broad_scale,
env_local_scale, env_medium) are **parallel but non-identical** classification systems.
GOLD's is a controlled vocabulary tree; MIxS uses ENVO ontology terms. Both appear on
GOLD biosamples (through the NMDC-specific API), but they are maintained independently.

---

## GOLD Date/Provenance Fields

GOLD-sourced `add_date`/`mod_date` timestamps are midnight-only — no meaningful time
information. In NMDC, these are being migrated into a `ProvenanceMetadata` class with
`xsd:date` range constraints (nmdc-schema issues #2831/#2860, umbrella #2806).

Three code generations of GOLD date handling:
1. Bill Duncan's original `GoldStudyTranslator`
2. Sujay Patil's current `gold_translator.py` in nmdc-runtime
3. Patrick Kalita's `submission_portal_translator.py`

---

## Key Contacts

| Person | Area | Where to reach them |
|--------|------|-------------------|
| Valerie Skye (`ctparker` on GitHub) | JGI Dremio infrastructure, GOLD table access | NMDC Slack `#ber-data-integration-crew` |
| Supratim Mukherjee, T. B. K. Reddy | GOLD database internals, table structure | Via Valerie Skye |
| Brian Syumae, Matt Dunford | Dremio infrastructure, lakehouse provisioning | NMDC Slack `#dremio-tech-eval`, `#ber_lakehouse` |
| Georg Rath | Lakehouse strategy, bucket provisioning | NMDC Slack `#ber_lakehouse` |
| Alicia Clum | JGI isolate metadata, sample submission forms | NMDC Slack, DMs |
| Patrick Kalita | NMDC submission portal, runtime GOLD translator | NMDC Slack `#nmdc-server` |
| Sierra Moxon | nmdc-runtime, cross-lakehouse queries | NMDC Slack `#ber_lakehouse` |

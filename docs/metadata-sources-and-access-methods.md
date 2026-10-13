# Metadata Sources and Access Methods

This document clarifies where different people can get or reshape different forms of metadata from NMDC, GOLD, and INSDC sources.

## NMDC Metadata (runtime/production data)

| Method | Description | Tool/Repo |
|--------|-------------|-----------|
| NMDC API | Official runtime API | nmdc-runtime |
| KBase/BERDL lakehouse | `nmdc_core` table via REST API | linkml-store, cmungall/lakehouse-skills (requires KBASE_TOKEN) |
| Ad-hoc tunnel + analytical scripts in this repo | Live NMDC Mongo via SSH tunnel; this repo no longer manages the data lifecycle | See [`nmdc-data-access.md`](nmdc-data-access.md) |

This repo retired the NMDC main-Mongo ingest/flatten pipeline (`flatten-nmdc`, `restore-to-{un,}authenticated`, etc.) on 2026-05-18; lakehouse-ready parquet now comes from [`kbase/data-lakehouse-ingest`](https://github.com/kbase/data-lakehouse-ingest). The analytical scripts (`analyze-nmdc-biosample-coverage`, `extract-nmdc-doi-inventory`, schema/slot utilities) remain and run against whatever Mongo URI you pass — see `nmdc-data-access.md`.

> **TODO:** Gather more information about the `nmdc_core` namespace in KBase/BERDL lakehouse:
> - Who created/maintains it?
> - What data does it contain exactly?
> - What are its idiosyncrasies or limitations?
> - How is it synchronized with NMDC production?
>
> This information may be available via internal channels (Slack, Google Drive).

## NMDC Submissions (user-submitted metadata)

| Method | Description | Tool/Repo |
|--------|-------------|-----------|
| Submission Portal | Web UI | submission.microbiomedata.org |
| submission-schema | Schema definitions | microbiomedata/submission-schema |
| This repo | API → MongoDB → flattened/normalized | `make -f Makefiles/nmdc_metadata.Makefile nmdc-submissions-to-mongo` (requires NMDC_DATA_SUBMISSION_REFRESH_TOKEN) |

### Setting Up NMDC Submission Portal Credentials

The `nmdc-submissions-to-mongo` target requires a refresh token that grants access to `https://data.microbiomedata.org/api/metadata_submission`. To see **all** submissions (not just your own), you also need admin privileges.

#### Step 1: Get a Refresh Token

1. Open `https://data.microbiomedata.org` in a browser
2. Click **Sign In** — you'll authenticate via ORCID
3. After login, open browser DevTools (F12) → **Application** tab → **Local Storage** → `https://data.microbiomedata.org`
4. Copy the value of `storage.refreshToken`
   - This is a JWT valid for **365 days**
   - It is exchanged for short-lived access tokens via `POST /auth/refresh`

#### Step 2: Request Admin Access (Required to See All Submissions)

Without admin, the API only returns submissions where you have an explicit role (owner/editor/viewer).

1. Ask someone with **Postgres database access** to set `is_admin = True` on your user record
2. Known contacts with access: **Patrick Kalita**, **Shreyas Cholia**, or **Eric Cavanna**
3. Reach out via `#nmdc-server` or `#infra-admin` in NMDC Slack
4. Provide your **ORCID iD** so they can find your user record

There is no self-service path — this is a direct database update.

#### Step 3: Create the Env File

Create `local/.env.nmdc-submissions`:

```bash
NMDC_DATA_SUBMISSION_REFRESH_TOKEN=<paste_refresh_token_here>
```

#### Step 4: Run the Pipeline

```bash
make -f Makefiles/nmdc_metadata.Makefile nmdc-submissions-to-mongo
```

> **Note:** The Makefile target currently references the old env file path. Issue [#303](https://github.com/microbiomedata/external-metadata-awareness/issues/303) tracks updating it to use `local/.env.nmdc-submissions` and local MongoDB.

#### Auth Flow Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/auth/login?redirect_uri=...` | GET | Initiates ORCID OAuth (browser) |
| `/auth/token` | POST | Exchanges authorization code for access + refresh tokens |
| `/auth/refresh` | POST | Exchanges refresh token for new access token (24hr expiry) |
| `/api/metadata_submission` | GET | Lists submissions (paginated, requires Bearer token) |

Source: [microbiomedata/nmdc-server](https://github.com/microbiomedata/nmdc-server) — `nmdc_server/auth.py`

## GOLD and other JGI Metadata

Status as of 2026-10-13, checked from an LBL laptop on the LBL VPN. "Works" means a test query returned data that day.

| Method | Status | Needs | Notes |
|--------|--------|-------|-------|
| JGI Starburst lakehouse, https://lakehouse.jgi.lbl.gov | Works, staging | LBL or JGI SSO, plus the Cloudflare Access cookie `CF_Authorization` (about 30 days) | SQL through the Trino CLI 479 or later: `--external-authentication --extra-header "Cookie=CF_Authorization=..."`. Catalogs include `gold-db-2_postgresql` (schemas `gold`, `gold_dsi`), `img-db-*`, `smc-db_postgresql`, `myco-db-*`, `plant-db-*`, `portal-db-1_mysql` and `jaws-db-1_mysql`. JGI data only so far; no credential for unattended scripts yet. |
| JGI Dremio lakehouse | **Retired** | | `lakehouse.jgi.lbl.gov` now serves Starburst and the Dremio host refuses connections. `linkml-store[dremio]` and the `jgi-lakehouse` skill in cmungall/lakehouse-skills no longer work (https://github.com/cmungall/lakehouse-skills/issues/3). |
| NMDC-specific GOLD REST API, https://gold.jgi.doe.gov/rest/nmdc | Works | NMDC's shared HTTP Basic account (`GOLD_API_USERNAME`, `GOLD_API_PASSWORD`) | No VPN. Use nmdc-runtime's client, `nmdc_runtime/site/resources.py`, rather than writing another. `projects` returns `itsSpid` and `itsSequencingProductName`. |
| GOLD public API, https://gold-ws.jgi.doe.gov | Works | Offline token from the site's "Request Token" button (ORCID, or LBL account for LBL staff) | Lookups by GOLD ID or ITS proposal ID only. Rate-limited: HTTP 429 after about 6 rapid calls (2026-09-23). |
| GOLD dev PostgreSQL, `gold-db-2.jgi.lbl.gov:5432/golddb1` | Works, by request | Per-person login from JGI Data Platform Engineering; LBL VPN | The `gold_dsi` schema (GOLD tables plus the semantic-search layer); the `gold` schema was not readable with the login tested. Newest `mod_date` seen: 2026-06-23. |
| JGI internal web services (Data Warehouse, PPS) | Works through `https://ws-access-espprd.jgi.lbl.gov` | LBL VPN | Through `https://ws-access.jgi.doe.gov` the Data Warehouse services returned 404 on 2026-10-13. |
| GOLD Excel download | Works | Nothing | `goldData.xlsx` from gold.jgi.doe.gov; lacks some fields present in the database. |
| GOLD website | Works | Nothing | Manual, no bulk export. |
| contextualizer-ai/gold-tools | Not checked | | |
| SMC API, https://smc.jgi.doe.gov | Works | Nothing | Secondary Metabolism Collaboratory: biosynthetic gene clusters and their source genomes. Its data usage policy says the data are "freely available without restriction". |
| JGI Data Portal file search, https://files.jgi.doe.gov/search/ | Works | Nothing | Search returns JSON; downloads were not tested. |

## INSDC BioSample

| Method | Description | Tool/Repo |
|--------|-------------|-----------|
| NCBI FTP XML | Bulk download | ftp.ncbi.nlm.nih.gov |
| This repo | XML → MongoDB → flattened/normalized → DuckDB | `Makefiles/ncbi_metadata.Makefile` |
| NCBI E-utilities | Programmatic, rate limited | Entrez API |

## INSDC BioProject

| Method | Description | Tool/Repo |
|--------|-------------|-----------|
| NCBI FTP XML | Bulk download | ftp.ncbi.nlm.nih.gov |
| This repo | XML → MongoDB → flattened → DuckDB | `Makefiles/ncbi_metadata.Makefile` |

## SRA Metadata

| Method | Description | Tool/Repo |
|--------|-------------|-----------|
| AWS S3 parquet | Public, bulk | s3://sra-pub-metadata-us-east-1 |
| This repo | Parquet → DuckDB → MongoDB (biosample-bioproject links) | `Makefiles/sra_metadata.Makefile` |
| NCBI SRA API | Programmatic | SRA Toolkit |

---

## Important Notes

### Two Different Lakehouses

**KBase/BERDL** and the **JGI lakehouse** are separate, with different access methods:

| Lakehouse | Access Method | Auth | Notes |
|-----------|---------------|------|-------|
| KBase/BERDL | REST API | KBASE_TOKEN (expires weekly) | Contains nmdc_core, pangenomics, UniProt |
| JGI Starburst | SQL via the Trino CLI | SSO plus Cloudflare Access cookie | Catalogs named for GOLD, IMG, SMC, MycoCosm, plant databases and more. Replaced JGI Dremio in 2026. |

### Stability Warning

Contents and access methods for both lakehouses are **subject to change**.

### Additional Resources

- [cmungall/lakehouse-skills](https://github.com/cmungall/lakehouse-skills) - Claude Code skills; `kbase-query` covers KBase/BERDL, while `jgi-lakehouse` still targets the retired JGI Dremio
- [linkml/linkml-store](https://github.com/linkml/linkml-store) - Unified access layer; its Dremio adapter no longer reaches JGI
- [turbomam/jgi-dremio-exploration](https://github.com/turbomam/jgi-dremio-exploration) - Archived 2026-10-13; JGI Dremio example, kept for history

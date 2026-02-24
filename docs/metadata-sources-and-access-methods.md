# Metadata Sources and Access Methods

This document clarifies where different people can get or reshape different forms of metadata from NMDC, GOLD, and INSDC sources.

## NMDC Metadata (runtime/production data)

| Method | Description | Tool/Repo |
|--------|-------------|-----------|
| NMDC API | Official runtime API | nmdc-runtime |
| KBase/BERDL lakehouse | `nmdc_core` table via REST API | linkml-store, cmungall/lakehouse-skills (requires KBASE_TOKEN) |
| This repo | MongoDB cache + flattening | `make -f Makefiles/nmdc_metadata.Makefile flatten-nmdc` |

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

## GOLD Metadata

| Method | Description | Tool/Repo |
|--------|-------------|-----------|
| JGI Dremio lakehouse | **Recommended** - SQL access | linkml-store[dremio], cmungall/lakehouse-skills (requires DREMIO_USER/PASSWORD) |
| GOLD API | Limited, single-ID queries | contextualizer-ai/gold-tools |
| GOLD Excel | goldData.xlsx, missing env fields | Manual download from gold.jgi.doe.gov |
| GOLD website | Manual, no bulk export | gold.jgi.doe.gov |

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

**KBase/BERDL** and **JGI Dremio** are separate lakehouses with different access methods:

| Lakehouse | Access Method | Auth | Notes |
|-----------|---------------|------|-------|
| KBase/BERDL | REST API | KBASE_TOKEN (expires weekly) | Contains nmdc_core, pangenomics, UniProt |
| JGI Dremio | SQL via linkml-store | DREMIO_USER/PASSWORD | Contains GOLD, IMG |

### Stability Warning

Contents and access methods for both lakehouses are **subject to change**.

### Additional Resources

- [cmungall/lakehouse-skills](https://github.com/cmungall/lakehouse-skills) - Claude Code skills for querying both lakehouses
- [linkml/linkml-store](https://github.com/linkml/linkml-store) - Unified access layer with Dremio support
- [turbomam/jgi-dremio-exploration](https://github.com/turbomam/jgi-dremio-exploration) - Minimal JGI Dremio implementation example

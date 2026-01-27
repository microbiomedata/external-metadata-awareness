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

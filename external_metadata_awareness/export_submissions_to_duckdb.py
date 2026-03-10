"""Export NMDC submission collections from MongoDB to a single DuckDB file.

Exports four submission-related collections:
  - nmdc_submissions: outer submission with study-like fields (flattened)
  - submission_biosample_rows: native field-value pairs per biosample
  - flattened_submission_biosamples: transformed/flattened with ontology enhancement
  - submission_biosample_slot_counts: field usage statistics

Usage::

    poetry run export-submissions-to-duckdb
    poetry run export-submissions-to-duckdb --output local/nmdc_submissions.duckdb
    poetry run export-submissions-to-duckdb --mongo-uri mongodb://localhost:27017/nmdc
"""

import json
import logging

import click
import duckdb
import pandas as pd
from pymongo import MongoClient

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)


def _export_flattened_submission_biosamples(db, conn):
    """Export flattened_submission_biosamples (cast to string for mixed-type columns)."""
    log.info("Exporting flattened_submission_biosamples...")
    docs = list(db.flattened_submission_biosamples.find({}, {"_id": 0}))
    df = pd.DataFrame(docs)
    # Cast object columns to string — MongoDB docs have mixed types (e.g. int and str
    # in the same column like '281 degrees') that DuckDB cannot auto-infer.
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str).replace({"None": None, "nan": None})
    conn.register("_tmp_df", df)
    conn.execute("CREATE OR REPLACE TABLE flattened_submission_biosamples AS SELECT * FROM _tmp_df")
    conn.unregister("_tmp_df")
    log.info(f"  {len(df)} rows, {len(df.columns)} columns")


def _export_submission_biosample_slot_counts(db, conn):
    """Export submission_biosample_slot_counts (small reference table)."""
    log.info("Exporting submission_biosample_slot_counts...")
    docs = list(db.submission_biosample_slot_counts.find({}, {"_id": 0}))
    df = pd.DataFrame(docs)
    conn.register("_tmp_df", df)
    conn.execute("CREATE OR REPLACE TABLE submission_biosample_slot_counts AS SELECT * FROM _tmp_df")
    conn.unregister("_tmp_df")
    log.info(f"  {len(df)} rows")


def _export_submission_biosample_rows(db, conn):
    """Export submission_biosample_rows (flatten nested row_data array)."""
    log.info("Exporting submission_biosample_rows...")
    rows = []
    for doc in db.submission_biosample_rows.find({}, {"_id": 0}):
        base = {"submission_id": doc["submission_id"], "key": doc.get("key", "")}
        for item in doc.get("row_data", []):
            field = item.get("field", "")
            value = item.get("value")
            if isinstance(value, (list, dict)):
                value = json.dumps(value)
            rows.append({**base, "field": field, "value": str(value) if value is not None else None})
    df = pd.DataFrame(rows)
    conn.register("_tmp_df", df)
    conn.execute("CREATE OR REPLACE TABLE submission_biosample_rows AS SELECT * FROM _tmp_df")
    conn.unregister("_tmp_df")
    log.info(f"  {len(df)} rows (field-value pairs)")


def _export_nmdc_submissions(db, conn):
    """Export nmdc_submissions (flatten nested JSON into key columns)."""
    log.info("Exporting nmdc_submissions...")
    flat_rows = []
    for doc in db.nmdc_submissions.find({}, {"_id": 0}):
        row = {}
        row["submission_id"] = doc.get("id") or doc.get("submission_id", "")
        row["status"] = doc.get("status", "")
        row["created"] = doc.get("created", "")

        meta = doc.get("metadata_submission", {})
        row["package_name"] = json.dumps(meta.get("packageName", []))
        row["templates"] = json.dumps(meta.get("templates", []))

        study = meta.get("studyForm", {})
        row["study_name"] = study.get("studyName", "")
        row["pi_name"] = study.get("piName", "")
        row["pi_email"] = study.get("piEmail", "")
        row["pi_orcid"] = study.get("piOrcid", "")
        row["description"] = study.get("description", "")
        row["notes"] = study.get("notes", "")
        row["gold_study_id"] = study.get("GOLDStudyId", "")
        row["ncbi_bioproject_id"] = study.get("NCBIBioProjectId", "")
        row["data_dois"] = json.dumps(study.get("dataDois", []))
        row["funding_sources"] = json.dumps(study.get("fundingSources", []))

        multi = meta.get("multiOmicsForm", {})
        row["award"] = multi.get("award", "")
        row["award_dois"] = json.dumps(multi.get("awardDois", []))
        row["data_generated"] = multi.get("dataGenerated")
        row["doe"] = multi.get("doe")

        row["metadata_submission_json"] = json.dumps(meta, default=str)

        flat_rows.append(row)

    df = pd.DataFrame(flat_rows)
    conn.register("_tmp_df", df)
    conn.execute("CREATE OR REPLACE TABLE nmdc_submissions AS SELECT * FROM _tmp_df")
    conn.unregister("_tmp_df")
    log.info(f"  {len(df)} rows")


@click.command()
@click.option(
    "--mongo-uri",
    default="mongodb://localhost:27017/nmdc",
    show_default=True,
    help="MongoDB connection URI including database name.",
)
@click.option(
    "--output",
    type=click.Path(),
    default="local/nmdc_submissions.duckdb",
    show_default=True,
    help="Output DuckDB file path.",
)
def main(mongo_uri: str, output: str) -> None:
    """Export NMDC submission collections from MongoDB to a DuckDB file."""
    db_name = mongo_uri.rsplit("/", 1)[-1].split("?")[0]

    with MongoClient(mongo_uri) as client:
        db = client[db_name]

        with duckdb.connect(output) as conn:
            _export_flattened_submission_biosamples(db, conn)
            _export_submission_biosample_slot_counts(db, conn)
            _export_submission_biosample_rows(db, conn)
            _export_nmdc_submissions(db, conn)

            log.info(f"\nDone. Written to {output}")
            for tbl in conn.execute("SELECT table_name, estimated_size FROM duckdb_tables()").fetchall():
                log.info(f"  {tbl[0]:45s} ~{tbl[1]} rows")

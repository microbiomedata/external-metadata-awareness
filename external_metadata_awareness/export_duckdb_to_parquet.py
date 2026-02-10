"""Export all tables from a DuckDB database to individual Parquet files."""

import logging
from pathlib import Path

import click
import duckdb

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


@click.command()
@click.argument("duckdb_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    default="./local/ncbi_duckdb_export/parquet",
    show_default=True,
    help="Directory to write Parquet files into.",
)
def export_duckdb_to_parquet(duckdb_file: Path, output_dir: Path) -> None:
    """Export each table in DUCKDB_FILE to a separate Parquet file.

    Reads the DuckDB database and writes one <table>.parquet file per table
    into the output directory.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    conn = duckdb.connect(str(duckdb_file), read_only=True)
    try:
        tables = [
            (row[0], row[1])
            for row in conn.execute(
                "SELECT table_name, estimated_size "
                "FROM duckdb_tables() "
                "WHERE schema_name = 'main' "
                "ORDER BY table_name"
            ).fetchall()
        ]

        if not tables:
            logger.warning("No tables found in %s", duckdb_file)
            return

        logger.info("Exporting %d tables from %s to %s", len(tables), duckdb_file, output_dir)

        for table, estimated_rows in tables:
            out_path = output_dir / f"{table}.parquet"
            conn.execute(
                f'COPY "{table}" TO \'{out_path}\' (FORMAT PARQUET, COMPRESSION ZSTD)'
            )
            size_mb = out_path.stat().st_size / (1024 * 1024)
            logger.info("  %-40s ~%10d rows  %8.1f MB", table, estimated_rows, size_mb)

        logger.info("Done. %d Parquet files written to %s", len(tables), output_dir)
    finally:
        conn.close()

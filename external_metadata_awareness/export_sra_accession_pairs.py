# export_sra_accession_pairs.py
#
# This script exports pairs of biosample and bioproject accessions from the SRA metadata
# stored in Google BigQuery. It handles both direct output to a specified file and
# automated filename generation with clear timestamping.

from typing import Optional, Iterator, Tuple
from pathlib import Path
from datetime import datetime
import logging
import click
from google.cloud import bigquery
import csv

# Configure logging with a format that includes timestamps
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define constants for default values and naming
DEFAULT_PROJECT = "nmdc-377118"
DEFAULT_DATASET = "nih-sra-datastore.sra"
DEFAULT_TABLE = "metadata"
DEFAULT_BATCH_SIZE = 100000
OUTPUT_FILE_PREFIX = "sra_accession_pairs"  # Base name for auto-generated files


class SRAAccessionPairExporter:
    """
    Exports paired biosample and bioproject accessions from SRA metadata in BigQuery.

    This class handles querying BigQuery to extract, analyze, and export pairs of
    accession identifiers that link biosamples to their associated bioprojects
    in the SRA metadata.
    """

    def __init__(
            self,
            project_name: str,
            dataset: str = DEFAULT_DATASET,
            table: str = DEFAULT_TABLE,
            batch_size: int = DEFAULT_BATCH_SIZE,
            row_limit: Optional[int] = None,
            exclude_nulls: bool = True,
            report_nulls: bool = False
    ):
        """
        Initialize the accession pair exporter.

        Args:
            project_name: Google Cloud project ID
            dataset: BigQuery dataset name
            table: BigQuery table name
            batch_size: Number of pairs to process in each batch
            row_limit: Optional limit on total pairs to process
            exclude_nulls: Whether to exclude pairs with NULL values
            report_nulls: Whether to report statistics about NULL values
        """
        self.project_name = project_name
        self.dataset = dataset
        self.table = table
        self.batch_size = batch_size
        self.row_limit = row_limit
        self.exclude_nulls = exclude_nulls
        self.report_nulls = report_nulls
        self.client = bigquery.Client(project=project_name)

    @property
    def full_table_path(self) -> str:
        """Returns the fully qualified BigQuery table path."""
        return f"`{self.dataset}.{self.table}`"

    def build_base_query(self) -> str:
        """
        Builds the base query for selecting accession pairs with appropriate filtering.

        This ensures consistent NULL handling across different query operations.
        """
        if self.exclude_nulls:
            return f"""
            SELECT DISTINCT biosample, bioproject
            FROM {self.full_table_path}
            WHERE biosample IS NOT NULL 
            AND bioproject IS NOT NULL
            """
        return f"""
        SELECT DISTINCT biosample, bioproject
        FROM {self.full_table_path}
        """

    def analyze_pairs(self) -> Optional[int]:
        """
        Analyze the dataset to count accession pairs and estimate processing requirements.

        Returns:
            Total count of accession pairs, or None if analysis fails
        """
        try:
            # First get data processing size estimate from BigQuery
            job_config = bigquery.QueryJobConfig(dry_run=True)
            estimate_query = self.build_base_query()
            if self.row_limit:
                estimate_query += f"\nLIMIT {self.row_limit}"

            query_job = self.client.query(estimate_query, job_config=job_config)
            bytes_processed = query_job.total_bytes_processed
            gb_processed = bytes_processed / (1024 * 1024 * 1024)
            logger.info(f"Query will process approximately {gb_processed:.2f} GB of data")
            logger.info("This affects BigQuery costs - see https://cloud.google.com/bigquery/pricing")

            # If requested, analyze NULL values in the dataset
            if self.report_nulls:
                null_query = f"""
                SELECT
                    COUNT(*) as total_pairs,
                    COUNTIF(biosample IS NULL) as null_biosample_count,
                    COUNTIF(bioproject IS NULL) as null_bioproject_count,
                    COUNTIF(biosample IS NULL OR bioproject IS NULL) as any_null_count
                FROM (
                    SELECT DISTINCT biosample, bioproject
                    FROM {self.full_table_path}
                )
                """
                null_result = next(iter(self.client.query(null_query).result()))
                logger.info(f"NULL value analysis:")
                logger.info(f"  Pairs with NULL biosample: {null_result.null_biosample_count:,}")
                logger.info(f"  Pairs with NULL bioproject: {null_result.null_bioproject_count:,}")
                logger.info(f"  Total pairs with any NULL: {null_result.any_null_count:,}")
                logger.info(
                    f"  Percentage with NULLs: {(null_result.any_null_count / null_result.total_pairs * 100):.1f}%")
                if self.exclude_nulls:
                    logger.info("  Note: NULL values will be excluded from export")

            # Get final pair count for the actual export criteria
            count_query = f"""
            SELECT COUNT(*) as pair_count
            FROM ({self.build_base_query()})
            """
            if self.row_limit:
                count_query = f"""
                SELECT MIN(cnt) as pair_count
                FROM (
                    SELECT {self.row_limit} as cnt
                    UNION ALL
                    SELECT COUNT(*) as cnt
                    FROM ({self.build_base_query()})
                )
                """

            count_result = next(iter(self.client.query(count_query).result()))
            total_pairs = count_result.pair_count
            logger.info(f"Query will process {total_pairs:,} unique biosample-bioproject pairs")
            if self.row_limit and total_pairs == self.row_limit:
                logger.info(f"Note: Output limited to first {self.row_limit:,} pairs")

            return total_pairs

        except Exception as e:
            logger.error(f"Failed to analyze pairs: {str(e)}")
            return None

    def get_pairs_batch(self, offset: int) -> Iterator[Tuple[str, str]]:
        """
        Retrieve a batch of accession pairs starting from the given offset.

        Args:
            offset: Starting position for this batch

        Yields:
            Tuples of (biosample_accession, bioproject_accession)
        """
        # Build query based on whether we're excluding NULLs
        base_query = self.build_base_query()
        if self.row_limit:
            base_query += f"\nLIMIT {self.row_limit}"

        batch_query = f"""
        SELECT biosample, bioproject
        FROM ({base_query})
        ORDER BY biosample
        LIMIT @batch_size
        OFFSET @offset
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("batch_size", "INT64", self.batch_size),
                bigquery.ScalarQueryParameter("offset", "INT64", offset)
            ]
        )

        try:
            query_job = self.client.query(batch_query, job_config=job_config)
            for row in query_job.result():
                yield row.biosample, row.bioproject
        except Exception as e:
            logger.error(f"Failed to retrieve batch starting at offset {offset}: {str(e)}")
            raise

    def generate_default_filename(self, output_dir: Path) -> Path:
        """
        Generate a default output filename using a timestamp and optional limit.

        Args:
            output_dir: Directory where the file will be created

        Returns:
            Path object for the generated filename
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename_parts = [OUTPUT_FILE_PREFIX, timestamp]
        if self.row_limit:
            filename_parts.insert(1, f'limit_{self.row_limit}')
        return output_dir / f"{'_'.join(filename_parts)}.tsv"

    def export_pairs(
            self,
            output_file: Optional[Path] = None,
            output_dir: Path = Path('.'),
            preview: bool = False
    ) -> Optional[Path]:
        """
        Export accession pairs to a TSV file using batched processing.

        Args:
            output_file: Specific output file path to use. If None, generates a timestamped name.
            output_dir: Directory to save the output file (used only if output_file is None)
            preview: If True, shows dataset statistics without exporting

        Returns:
            Path to the output file if successful, None otherwise
        """
        if preview:
            logger.info("Analyzing accession pairs...")
            total_pairs = self.analyze_pairs()
            if total_pairs:
                # Estimate output file size (assuming ~50 bytes per pair)
                estimated_mb = (total_pairs * 50) / (1024 * 1024)
                logger.info(f"Estimated output file size: {estimated_mb:.1f} MB")
            logger.info("Preview completed. Use the same command without --preview to perform the export.")
            return None

        total_pairs = self.analyze_pairs()
        if not total_pairs:
            return None

        # Determine the output file path - either user-specified or auto-generated
        actual_output_file = output_file if output_file is not None else self.generate_default_filename(output_dir)

        try:
            # Ensure parent directory exists
            actual_output_file.parent.mkdir(parents=True, exist_ok=True)

            with actual_output_file.open('w', newline='') as f:
                writer = csv.writer(f, delimiter='\t')
                writer.writerow(['biosample', 'bioproject'])

                # Determine target number of pairs for progress calculation
                target_pairs = min(total_pairs, self.row_limit) if self.row_limit else total_pairs

                offset = 0
                pairs_processed = 0

                while offset < target_pairs:
                    batch_pairs = 0
                    for biosample, bioproject in self.get_pairs_batch(offset):
                        writer.writerow([biosample, bioproject])
                        batch_pairs += 1

                    pairs_processed += batch_pairs
                    offset += self.batch_size

                    # Calculate progress percentage and format timestamp
                    progress = (pairs_processed / target_pairs) * 100
                    current_time = datetime.now().isoformat(timespec='seconds')

                    # Format progress message to show context of limit if specified
                    progress_msg = (
                        f"[{current_time}] Progress: {progress:.1f}% "
                        f"({pairs_processed:,} / {target_pairs:,} pairs"
                    )
                    if self.row_limit:
                        progress_msg += f" requested from {total_pairs:,} total)"
                    else:
                        progress_msg += ")"

                    logger.info(progress_msg)

                    if batch_pairs < self.batch_size:
                        break

                completion_time = datetime.now().isoformat(timespec='seconds')
                logger.info(f"[{completion_time}] Export complete! File saved as: {actual_output_file}")
                logger.info(f"Total accession pairs exported: {pairs_processed:,}")
                return actual_output_file

        except Exception as e:
            error_time = datetime.now().isoformat(timespec='seconds')
            logger.error(f"[{error_time}] Export failed: {str(e)}")
            return None


@click.command(help="""
    Export paired biosample and bioproject accessions from NCBI's SRA database.

    Provides two modes of operation:
    1. Preview mode (--preview): Analyzes the pairs and shows statistics
    2. Export mode: Extracts accession pairs to a TSV file

    The output file will contain 'biosample' and 'bioproject' columns. You can specify
    an exact output path with --output, or let the tool generate a timestamped filename
    in the directory specified by --output-dir.
    """)
@click.option(
    '--project',
    default=DEFAULT_PROJECT,
    help="Google Cloud project ID",
    show_default=True
)
@click.option(
    '--dataset',
    default=DEFAULT_DATASET,
    help="BigQuery dataset name",
    show_default=True
)
@click.option(
    '--table',
    default=DEFAULT_TABLE,
    help="BigQuery table name",
    show_default=True
)
@click.option(
    '--batch-size',
    default=DEFAULT_BATCH_SIZE,
    help="Number of pairs to process in each batch",
    show_default=True
)
@click.option(
    '--limit',
    type=int,
    help="Limit the total number of pairs to retrieve (useful for testing)",
    default=None
)
@click.option(
    '--exclude-nulls/--include-nulls',
    default=True,
    help="Exclude pairs where either biosample or bioproject is NULL",
    show_default=True
)
@click.option(
    '--report-nulls',
    is_flag=True,
    help="Report statistics about NULL values in the dataset"
)
@click.option(
    '--output',
    type=click.Path(dir_okay=False, path_type=Path),
    help="Specific output file path (default: auto-generated timestamp-based name)",
    default=None
)
@click.option(
    '--output-dir',
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=Path('.'),
    help="Directory to save the output file (used only if --output not specified)",
    show_default=True
)
@click.option(
    '--preview',
    is_flag=True,
    help="Show dataset statistics and estimated processing size without exporting"
)
@click.option(
    '--verbose',
    is_flag=True,
    help="Enable verbose logging"
)
def main(
        project: str,
        dataset: str,
        table: str,
        batch_size: int,
        limit: Optional[int],
        exclude_nulls: bool,
        report_nulls: bool,
        output: Optional[Path],
        output_dir: Path,
        preview: bool,
        verbose: bool,
):
    """Main entry point for the SRA accession pair exporter."""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    exporter = SRAAccessionPairExporter(
        project_name=project,
        dataset=dataset,
        table=table,
        batch_size=batch_size,
        row_limit=limit,
        exclude_nulls=exclude_nulls,
        report_nulls=report_nulls
    )

    if output_file := exporter.export_pairs(output, output_dir, preview):
        logger.info(f"Successfully exported accession pairs to {output_file}")
    else:
        if not preview:
            logger.error("Failed to export accession pairs")


if __name__ == "__main__":
    main()

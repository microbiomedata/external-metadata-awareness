from typing import Optional

import click
import logging
from pathlib import Path
from datetime import datetime
from google.cloud import bigquery

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

OUTPUT_FILE_PREFIX = 'sra_schema'


class SchemaExporter:

    def __init__(
            self,
            project_name: str,
            dataset: str,
            table: str,
            output_format: str = 'tsv'  # Add output format option
    ):
        self.client = bigquery.Client(project=project_name)
        self.dataset = dataset
        self.table = table
        self.output_format = output_format.lower()  # Store lowercase for easier comparison


    def get_output_filename(self, output_dir: Path) -> Path:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return output_dir / f"{OUTPUT_FILE_PREFIX}_{timestamp}.{self.output_format}"

    def export_schema(self, output_file: Optional[Path] = None, output_dir: Path = Path('.')) -> Optional[Path]:

        table_ref = self.client.get_table(f"{self.dataset}.{self.table}")
        schema = table_ref.schema

        actual_output_file = output_file or self.get_output_filename(output_dir)

        try:
            if self.output_format == 'tsv':
                with open(actual_output_file, 'w') as f:
                    f.write("name\ttype\tmode\tdescription\n")  # Header row
                    for field in schema:
                        f.write(f"{field.name}\t{field.field_type}\t{field.mode}\t{field.description}\n")

            elif self.output_format == 'json':
                import json
                schema_list = [{"name": field.name, "type": field.field_type, "mode": field.mode, "description": field.description} for field in schema]
                with open(actual_output_file, 'w') as f:
                    json.dump(schema_list, f, indent=4)
            else:
                 logger.error(f"Unsupported output format: {self.output_format}")
                 return None


            completion_time = datetime.now().isoformat(timespec='seconds')
            logger.info(f"[{completion_time}] Schema export complete! File saved as: {actual_output_file}")
            return actual_output_file


        except Exception as e:
            error_time = datetime.now().isoformat(timespec='seconds')
            logger.error(f"[{error_time}] Schema export failed: {str(e)}")
            return None



@click.command(help="Export schema of a BigQuery table to a TSV or JSON file.")
@click.option('--project', required=True, help='Your Google Cloud project ID.')
@click.option('--dataset', required=True, help='BigQuery dataset name.')
@click.option('--table', required=True, help='BigQuery table name.')
@click.option('--output', type=click.Path(writable=True, path_type=Path), help='Output file path (optional). If not provided, a timestamped file will be created in the current directory.')
@click.option('--output_dir', type=click.Path(file_okay=False, dir_okay=True, path_type=Path), default=Path('.'), help='Output directory (used if --output is not specified).', show_default=True)
@click.option('--format', type=click.Choice(['tsv', 'json'], case_sensitive=False), default='tsv', show_default=True, help='Output format (tsv or json).')  # Add format option
@click.option('--verbose', is_flag=True, help='Enable verbose logging.')
def main(project, dataset, table, output, output_dir, format, verbose):
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    exporter = SchemaExporter(project_name=project, dataset=dataset, table=table, output_format=format)

    if output_file := exporter.export_schema(output, output_dir):
        logger.info(f"Successfully exported schema to {output_file}")

    else:
        logger.error("Failed to export schema")



if __name__ == "__main__":
    main()
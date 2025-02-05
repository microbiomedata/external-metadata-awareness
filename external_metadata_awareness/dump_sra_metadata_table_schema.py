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
            output_format: str = 'tsv'
    ):
        self.client = bigquery.Client(project=project_name)
        self.dataset = dataset
        self.table = table
        self.output_format = output_format.lower()

    def get_output_filename(self, output_file: Optional[Path]) -> Path:
        if output_file:  # Use provided filename
            return output_file
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            return Path(
                '.') / f"{OUTPUT_FILE_PREFIX}_{timestamp}.{self.output_format}"  # create filename in current directory

    def export_schema(self, output_file: Optional[Path] = None) -> Optional[Path]:
        table_ref = self.client.get_table(f"{self.dataset}.{self.table}")
        schema = table_ref.schema

        actual_output_file = self.get_output_filename(output_file)

        try:
            if self.output_format == 'tsv':
                with open(actual_output_file, 'w') as f:
                    f.write("name\ttype\tmode\tdescription\tsubfields\n")
                    for field in schema:
                        subfields_str = ""
                        if field.field_type == 'RECORD':
                            subfields_str = ','.join([f"{sf.name}:{sf.field_type}" for sf in field.fields])
                        f.write(
                            f"{field.name}\t{field.field_type}\t{field.mode}\t{field.description}\t{subfields_str}\n")

            elif self.output_format == 'json':
                schema_list = []
                for field in schema:
                    field_dict = {
                        "name": field.name,
                        "type": field.field_type,
                        "mode": field.mode,
                        "description": field.description
                    }
                    if field.field_type == 'RECORD':
                        field_dict["subfields"] = [{"name": sf.name, "type": sf.field_type} for sf in field.fields]
                    schema_list.append(field_dict)

                with open(actual_output_file, 'w') as f:
                    import json
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
@click.option('--output', type=click.Path(writable=True, path_type=Path),
              help='Output file path. If omitted, uses sra_schema_[timestamp].[format] in the current directory.')  # modified help text
@click.option('--format', type=click.Choice(['tsv', 'json'], case_sensitive=False), default='tsv', show_default=True,
              help='Output format (tsv or json).')
@click.option('--verbose', is_flag=True, help='Enable verbose logging.')
def main(project, dataset, table, output, format, verbose):
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    exporter = SchemaExporter(project_name=project, dataset=dataset, table=table, output_format=format)

    if output_file := exporter.export_schema(output):
        logger.info(f"Successfully exported schema to {output_file}")

    else:
        logger.error("Failed to export schema")


if __name__ == "__main__":
    main()

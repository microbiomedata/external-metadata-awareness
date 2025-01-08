import sys
import click
from pymongo import MongoClient
import pandas as pd
from typing import Optional
from datetime import datetime
import duckdb
from tqdm import tqdm
import gc


@click.command()
@click.option('--connection-string', default="mongodb://localhost:27017/", help="MongoDB connection string.")
@click.option('--db-name', default="ncbi_metadata", required=True, help="Name of the database.")
@click.option('--collection-name', default="samples", required=True, help="Name of the collection.")
@click.option('--limit', default=50000000, help="Number of documents to fetch.", type=int)
@click.option('--batch-size', default=100000, help="Number of documents to fetch per batch.", type=int)
@click.option('--start-offset', default=0, help="Starting offset for id range.", type=int)
@click.option('--duckdb-file', default="../local/ncbi_biosamples.duckdb", help="Name of the DuckDB database file.")
@click.option('--table-name', default="attributes", help="Name of the table to store the data.")
@click.option('--path', default=None,
              help="Path within the document to process (e.g., 'BioSample.Attributes.Attribute').")
@click.option('--tsv-path', default="current_batch_dump.tsv",
              help="Path to the TSV file for dumping current DataFrame.")
def export_data(connection_string: str, db_name: str, collection_name: str, limit: int, batch_size: int,
                start_offset: int, duckdb_file: str, table_name: str, path: Optional[str], tsv_path: str) -> None:
    """
    Extracts fields from a specified path within MongoDB documents and exports them to a DuckDB table, or
    generates a custom report if no path is specified.

    Parameters:
    - connection-string: MongoDB connection string.
    - db-name: Name of the MongoDB database.
    - collection-name: Name of the MongoDB collection.
    - limit: Maximum number of documents to fetch.
    - batch-size: Number of documents to fetch per batch.
    - start-offset: Starting offset for id range.
    - duckdb-file: Path to the DuckDB file.
    - table-name: Name of the table in DuckDB.
    - path: Path within the document to extract data from.
    - tsv-path: Path to the TSV file for dumping current DataFrame.
    """
    # Log start time
    start_time = datetime.now()
    click.echo(f"Start time: {start_time}")

    # Connect to MongoDB
    client = MongoClient(connection_string)
    db = client[db_name]
    collection = db[collection_name]

    # Initialize connection to DuckDB
    con = duckdb.connect(duckdb_file)

    if path:
        path_root = '.'.join(path.split('.')[:3])
        expected_fields = {
            "BioSample.Attributes.Attribute": {"id", "attribute_name", "content",
                                               "display_name", "harmonized_name", "unit"},
            "BioSample.Ids.Id": {"id", "is_primary", "db", "content", 'is_hidden', 'db_label'},
            "BioSample.Links.Link": {"id", "content", "description", "label",
                                     "link_name", "submission_id", "target", "type", "url"},
            # actually empty? description, link_name. populated but not in dynamic schema: url
            "BioSample.Description.Organism": {"id", "OrganismName", "taxonomy_id",
                                               "taxonomy_name"},
        }

        if path_root in expected_fields:
            expected_columns = expected_fields[path_root]
        else:
            expected_columns = set()  # Default to empty, no specific expectations

        missing_path_count = 0

        for i in range(start_offset, limit, batch_size):
            # Fetch the batch
            documents = collection.find({}, {
                # "BioSample.accession": 1,
                "BioSample.id": 1,
                # "BioSample.Package.content": 1,
                f"{path}": 1,
                "_id": 0
            }).skip(i).limit(batch_size)

            data_rows = []
            min_id = float('inf')  # Initialize to high value
            max_id = float('-inf')  # Initialize to low value

            for doc in tqdm(documents, total=batch_size,
                            desc=f"Processing batch {i // batch_size + 1} of {limit // batch_size}"):
                common_fields = {
                    # "accession": doc.get("BioSample", {}).get("accession"),
                    "id": doc.get("BioSample", {}).get("id"),
                    # "package_content": doc.get("BioSample", {}).get("Package", {}).get("content")
                }
                # Track min and max id values
                if common_fields["id"] is not None:
                    min_id = min(min_id, common_fields["id"])
                    max_id = max(max_id, common_fields["id"])

                nested_data = doc
                for key in path.split('.'):
                    nested_data = nested_data.get(key, {})

                if isinstance(nested_data, list):
                    if len(nested_data) == 0:
                        missing_path_count += 1
                    else:
                        for item in nested_data:
                            if isinstance(item, dict):
                                combined_fields = {**common_fields, **item}
                                data_rows.append(combined_fields)

                                unexpected_columns = set(combined_fields.keys()) - expected_columns
                                if unexpected_columns:
                                    click.echo(
                                        f"{timestamp()} - Warning: Unexpected columns detected in batch {i // batch_size + 1}: {unexpected_columns}",
                                        err=True
                                    )
                elif isinstance(nested_data, dict):
                    combined_fields = {**common_fields, **nested_data}
                    data_rows.append(combined_fields)

                    unexpected_columns = set(combined_fields.keys()) - expected_columns
                    if unexpected_columns:
                        click.echo(
                            f"{timestamp()} - Warning: Unexpected columns detected in batch {i // batch_size + 1}: {unexpected_columns}",
                            err=True
                        )
                else:
                    missing_path_count += 1

            # Report the min and max id for the current batch
            if min_id != float('inf') and max_id != float('-inf'):
                click.echo(f"{timestamp()} - Batch {i // batch_size + 1}: Min id = {min_id}, Max id = {max_id}")

            if data_rows:  # Only proceed if there is data
                df = pd.DataFrame(data_rows)
                df = df.reindex(columns=sorted(expected_columns))

                # Filter out rows where only 'id' is populated
                df = df.dropna(how='all', subset=[col for col in df.columns if col != 'id'])

                # Dump DataFrame to TSV file
                df.to_csv(tsv_path, sep='\t', index=False)
                click.echo(f"{timestamp()} - Dumped current batch to {tsv_path}")

                if not df.empty:  # Ensure DataFrame is not empty before insertion
                    if i == start_offset:
                        # Check if the table already exists
                        table_exists_query = f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name='{table_name}'"
                        table_exists = con.execute(table_exists_query).fetchone()[0]

                        if table_exists > 0:
                            # Table exists, exit gracefully
                            click.echo(f"{timestamp()} - Table '{table_name}' already exists. Exiting gracefully.")
                            sys.exit(0)

                        # Exclude 'id' from schema if it is already in df.columns
                        schema_columns = [col for col in df.columns if col != 'id']
                        schema = ', '.join([f"{col} VARCHAR" for col in schema_columns])

                        # Create the table with the defined schema, adding 'id' separately as INTEGER
                        con.execute(f"CREATE TABLE {table_name} (id INTEGER, {schema})")
                    else:
                        # Reorder the DataFrame columns to match the existing table schema
                        df = df.reindex(columns=[col[0] for col in con.execute(f"DESCRIBE {table_name}").fetchall()],
                                        fill_value=None)
                        con.execute(f"INSERT INTO {table_name} SELECT * FROM df")

                # Explicitly delete the DataFrame and clear memory
                del df
                del data_rows
                gc.collect()
    else:
        click.echo("No path specified. Please provide a valid path to extract data.")

    con.close()
    end_time = datetime.now()
    duration = end_time - start_time
    click.echo(f"{limit} documents processed in {duration}. Completed at {end_time}")


def timestamp() -> str:
    """Returns the current date and time as a formatted string."""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


if __name__ == "__main__":
    export_data()

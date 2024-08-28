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
@click.option('--batch-size', default=1000000, help="Number of documents to fetch per batch.", type=int)
@click.option('--duckdb-file', default="../local/ncbi_biosamples.duckdb", help="Name of the DuckDB database file.")
@click.option('--table-name', default="attributes", help="Name of the table to store the data.")
@click.option('--path', default=None,
              help="Path within the document to process (e.g., 'BioSample.Attributes.Attribute').")
def export_data(connection_string: str, db_name: str, collection_name: str, limit: int, batch_size: int,
                duckdb_file: str, table_name: str, path: Optional[str]) -> None:
    """
    Extracts fields from a specified path within MongoDB documents and exports them to a DuckDB table, or
    generates a custom report if no path is specified.
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
        # If a path is provided, process the specified path
        expected_fields = {
            "BioSample.Attributes.Attribute": {
                "accession", "id", "package_content",
                "attribute_name", "content",
                "display_name", "harmonized_name", "unit"
            },
            "BioSample.Ids.Id": {
                "accession", "id", "package_content",
                "is_primary", "db", "content"
            },
            "BioSample.Links.Link": {
                "accession", "id", "package_content",
                "link_name", "url", "description"
            },
            "BioSample.Description.Organism": {
                "accession", "id", "package_content",
                "OrganismName", "taxonomy_id", "taxonomy_name",
            },
        }

        path_root = '.'.join(path.split('.')[:3])
        if path_root in expected_fields:
            expected_columns = expected_fields[path_root]
        else:
            expected_columns = set()  # Default to empty, no specific expectations

        missing_path_count = 0

        for i in range(0, limit, batch_size):
            documents = collection.find({}, {
                "BioSample.accession": 1,
                "BioSample.id": 1,
                "BioSample.Package.content": 1,
                f"{path}": 1,
                "_id": 0
            }).skip(i).limit(batch_size)

            data_rows = []
            for doc in tqdm(documents, total=batch_size,
                            desc=f"Processing batch {i // batch_size + 1} of {limit // batch_size}"):
                common_fields = {
                    "accession": doc.get("BioSample", {}).get("accession"),
                    "id": doc.get("BioSample", {}).get("id"),
                    "package_content": doc.get("BioSample", {}).get("Package", {}).get("content")
                }
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
                                        f"Warning: Unexpected columns detected in batch {i // batch_size + 1}: {unexpected_columns}",
                                        err=True
                                    )
                elif isinstance(nested_data, dict):
                    combined_fields = {**common_fields, **nested_data}
                    data_rows.append(combined_fields)

                    unexpected_columns = set(combined_fields.keys()) - expected_columns
                    if unexpected_columns:
                        click.echo(
                            f"Warning: Unexpected columns detected in batch {i // batch_size + 1}: {unexpected_columns}",
                            err=True
                        )
                else:
                    missing_path_count += 1

            if data_rows:  # Only proceed if there is data
                df = pd.DataFrame(data_rows)
                df = df.reindex(columns=sorted(expected_columns))

                if not df.empty:  # Ensure DataFrame is not empty before insertion
                    if i == 0:
                        con.execute(f"CREATE TABLE IF NOT EXISTS {table_name} AS SELECT * FROM df")
                    else:
                        con.execute(f"INSERT INTO {table_name} SELECT * FROM df")

                # Explicitly delete the DataFrame and clear memory
                del df
                del data_rows
                gc.collect()

    else:
        # Generate the overview report
        custom_fields = {
            "BioSample.access": "access",
            "BioSample.accession": "accession",
            "BioSample.Curation.curation_date": "curation_date",
            "BioSample.Curation.curation_status": "curation_status",
            "BioSample.id": "id",
            "BioSample.last_update": "last_update",
            "BioSample.Package.content": "package_content",
            "BioSample.publication_date": "publication_date",
            "BioSample.Status.status": "status",
            "BioSample.Status.when": "status_when",
            "BioSample.submission_date": "submission_date",
            "BioSample.Description.Title": "title",
        }

        for i in range(0, limit, batch_size):
            projection = {k: 1 for k in custom_fields.keys()}
            projection["_id"] = 0
            documents = collection.find({}, projection).skip(i).limit(batch_size)
            data_rows = []
            for doc in tqdm(documents, total=batch_size,
                            desc=f"Processing batch {i // batch_size + 1} of {limit // batch_size}"):
                row = {}
                for k, v in custom_fields.items():
                    value = doc
                    for part in k.split('.'):
                        value = value.get(part, None)
                        if value is None:
                            break
                    row[v] = value
                data_rows.append(row)

            if data_rows:  # Only proceed if there is data
                df = pd.DataFrame(data_rows)

                if not df.empty:  # Ensure DataFrame is not empty before insertion
                    if i == 0:
                        con.execute(f"CREATE TABLE IF NOT EXISTS {table_name} AS SELECT * FROM df")
                    else:
                        con.execute(f"INSERT INTO {table_name} SELECT * FROM df")

                # Explicitly delete the DataFrame and clear memory
                del df
                del data_rows
                gc.collect()

    con.close()

    end_time = datetime.now()
    duration = end_time - start_time
    click.echo(f"{limit} documents processed in {duration}. Completed at {end_time}")


if __name__ == "__main__":
    export_data()

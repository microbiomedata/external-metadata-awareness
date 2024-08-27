import click
from pymongo import MongoClient
import pandas as pd
from typing import Optional
from datetime import datetime
import duckdb
from tqdm import tqdm


@click.command()
@click.option('--connection-string', default="mongodb://localhost:27017/", help="MongoDB connection string.")
@click.option('--db-name', default="ncbi_metadata", required=True, help="Name of the database.")
@click.option('--collection-name', default="samples", required=True, help="Name of the collection.")
@click.option('--limit', default=5000000, help="Number of documents to fetch.",
              type=int)  # ~ 10 minutes for 5 million input rows plus startup and writing to duckdb
@click.option('--batch-size', default=500000, help="Number of documents to fetch per batch.", type=int)
@click.option('--duckdb-file', default="attributes.duckdb", help="Name of the DuckDB database file.")
@click.option('--table-name', default="attributes_table", help="Name of the table to store the data.")
def export_attributes(connection_string: str, db_name: str, collection_name: str, limit: int, batch_size: int,
                      duckdb_file: str, table_name: str) -> None:
    """
    Extracts the BioSample.Attributes.Attribute fields from documents in a MongoDB collection
    and exports them to a DuckDB table, processing in batches.

    :param connection_string: The MongoDB connection string.
    :param db_name: The name of the MongoDB database.
    :param collection_name: The name of the MongoDB collection.
    :param limit: The total number of documents to process.
    :param batch_size: The number of documents to process per batch.
    :param duckdb_file: The name of the DuckDB database file.
    :param table_name: The name of the table to store the data.
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

    # Define the expected columns
    expected_columns = {
        "accession", "id", "package_content",
        "attribute_name", "content",
        "display_name", "harmonized_name", "unit"
    }

    # Process documents in batches
    for i in range(0, limit, batch_size):
        # Fetch the current batch of documents
        documents = collection.find({}, {
            "BioSample.Attributes.Attribute": 1,
            "BioSample.accession": 1,
            "BioSample.id": 1,
            "BioSample.Package.content": 1,
            "_id": 0
        }).skip(i).limit(batch_size)

        # Extract the relevant fields with progress monitoring within the chunk
        attribute_fields = []
        for doc in tqdm(documents, total=batch_size,
                        desc=f"Processing batch {i // batch_size + 1} of {limit // batch_size}"):
            common_fields = {
                "accession": doc.get("BioSample", {}).get("accession"),
                "id": doc.get("BioSample", {}).get("id"),
                "package_content": doc.get("BioSample", {}).get("Package", {}).get("content")
            }
            if 'BioSample' in doc and 'Attributes' in doc['BioSample']:
                attributes = doc['BioSample']['Attributes'].get('Attribute', [])
                if isinstance(attributes, list):
                    for attribute in attributes:
                        if isinstance(attribute, dict):
                            # Combine common fields with each attribute dictionary
                            combined_fields = {**common_fields, **attribute}
                            attribute_fields.append(combined_fields)

                            # Check for unexpected columns
                            unexpected_columns = set(combined_fields.keys()) - expected_columns
                            if unexpected_columns:
                                click.echo(
                                    f"Warning: Unexpected columns detected in batch {i // batch_size + 1}: {unexpected_columns}",
                                    err=True
                                )

        # Create a DataFrame from the combined fields
        df = pd.DataFrame(attribute_fields)

        # Ensure the DataFrame has only the expected columns
        df = df.reindex(columns=sorted(expected_columns))

        # Append the batch DataFrame to the DuckDB table
        if i == 0:
            # For the first batch, create the table
            con.execute(f"CREATE TABLE IF NOT EXISTS {table_name} AS SELECT * FROM df")
        else:
            # For subsequent batches, insert the data
            con.execute(f"INSERT INTO {table_name} SELECT * FROM df")

    # Close DuckDB connection
    con.close()

    # Log end time
    end_time = datetime.now()
    duration = end_time - start_time
    click.echo(f"{limit} documents processed in {duration}. Completed at {end_time}")


if __name__ == "__main__":
    export_attributes()

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
@click.option('--limit', default=50000000, help="Number of documents to fetch.",
              type=int)  # 1.5 minutes for 1 million input rows plus startup and writing to duckdb
@click.option('--duckdb-file', default="attributes.duckdb", help="Name of the DuckDB database file.")
@click.option('--table-name', default="attributes_table", help="Name of the table to store the data.")
def export_attributes(connection_string: str, db_name: str, collection_name: str, limit: int, duckdb_file: str,
                      table_name: str) -> None:
    """
    Extracts the BioSample.Attributes.Attribute fields from documents in a MongoDB collection
    and exports them to a DuckDB table.

    :param connection_string: The MongoDB connection string.
    :param db_name: The name of the MongoDB database.
    :param collection_name: The name of the MongoDB collection.
    :param limit: The number of documents to process.
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

    # Fetch the documents with the additional fields
    documents = collection.find({}, {
        "BioSample.Attributes.Attribute": 1,
        "BioSample.accession": 1,
        "BioSample.id": 1,
        "BioSample.Package.content": 1,
        "_id": 0
    }).limit(limit)

    # Extract the relevant fields with tqdm progress monitoring
    attribute_fields = []
    for doc in tqdm(documents, total=limit, desc="Processing documents"):
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
                        attribute_fields.append({**common_fields, **attribute})

    # Create a DataFrame from the combined fields
    df = pd.DataFrame(attribute_fields)

    # Connect to DuckDB and export the DataFrame to a table
    con = duckdb.connect(duckdb_file)
    con.execute(f"CREATE TABLE IF NOT EXISTS {table_name} AS SELECT * FROM df")
    con.close()

    # Log end time
    end_time = datetime.now()
    duration = end_time - start_time
    click.echo(f"{limit} documents written in {duration}. Completed at {end_time}")


if __name__ == "__main__":
    export_attributes()

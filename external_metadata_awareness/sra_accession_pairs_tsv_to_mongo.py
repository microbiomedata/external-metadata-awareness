import pymongo
import csv
import click
import datetime
from typing import List
from external_metadata_awareness.mongodb_connection import get_mongo_client


def get_iso_timestamp() -> str:
    """Return the current timestamp in ISO 8601 format."""
    return datetime.datetime.now().isoformat()


@click.command()
@click.option("--file-path", type=click.Path(exists=True), required=True, help="Path to the TSV file.")
@click.option("--mongo-uri", type=str, required=True, help="MongoDB connection URI (including database name).")
@click.option("--env-file", type=str, help="Path to .env file with MongoDB credentials.")
@click.option("--collection", type=str, default="sra_biosamples_bioprojects", show_default=True,
              help="MongoDB collection name.")
@click.option("--batch-size", type=int, default=100000, show_default=True, help="Number of rows to insert per batch.")
@click.option("--report-interval", type=int, default=500000, show_default=True,
              help="Rows processed before showing progress.")
@click.option("--verbose", is_flag=True, help="Enable verbose output.")
@click.option("--biosample-column", default="biosample", help="Name of biosample column in TSV")
@click.option("--bioproject-column", default="bioproject", help="Name of bioproject column in TSV")
def load_tsv_to_mongo(
        file_path: str,
        mongo_uri: str,
        collection: str,
        batch_size: int,
        report_interval: int,
        env_file: str = None,
        verbose: bool = False,
        biosample_column: str = "biosample",
        bioproject_column: str = "bioproject"
) -> None:
    """
    Load a large TSV file into MongoDB.

    - Skips rows with missing biosample or bioproject values.
    - Uses batch insertion for performance.
    - Reports progress periodically.

    Args:
        file_path (str): Path to the input TSV file.
        mongo_uri (str): MongoDB connection URI.
        collection (str): MongoDB collection name.
        batch_size (int): Number of records to insert per batch.
        report_interval (int): Number of records to process before displaying progress.
        env_file (str, optional): Path to environment file with MongoDB credentials.
        verbose (bool, optional): Enable verbose output.
    """

    if verbose:
        print(f"[{get_iso_timestamp()}] Connecting to MongoDB using URI: {mongo_uri}")
        
    # MongoDB connection
    client = get_mongo_client(mongo_uri=mongo_uri, env_file=env_file, debug=verbose)
    
    # Extract database name from URI
    if '/' in mongo_uri:
        database = mongo_uri.split('/')[-1].split('?')[0]
    else:
        database = 'ncbi_metadata'  # Default database name
        
    if verbose:
        print(f"[{get_iso_timestamp()}] Using database: {database}")
        print(f"[{get_iso_timestamp()}] Using collection: {collection}")
    
    db = client[database]
    coll = db[collection]

    total_rows = 0
    batch: List[dict] = []

    with open(file_path, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter="\t")
        total_file_rows = sum(1 for _ in file) - 1  # Count total rows (excluding header)
        file.seek(0)  # Reset file pointer after counting

        next(reader)  # Skip header
        for row in reader:
            biosample = row[biosample_column].strip()
            bioproject = row[bioproject_column].strip()

            if biosample and bioproject:  # Ignore empty values
                batch.append({
                    "biosample_accession": biosample,
                    "bioproject_accession": bioproject
                })

            total_rows += 1

            # Insert batch into MongoDB
            if len(batch) >= batch_size:
                coll.insert_many(batch)
                batch.clear()

            # Show progress at intervals
            if total_rows % report_interval == 0:
                percentage = (total_rows / total_file_rows) * 100
                print(f"[{get_iso_timestamp()}] Processed {total_rows:,}/{total_file_rows:,} rows ({percentage:.2f}%)")

        # Insert remaining batch
        if batch:
            coll.insert_many(batch)

    print(f"[{get_iso_timestamp()}] Data successfully loaded! Processed {total_rows:,} rows.")


if __name__ == "__main__":
    load_tsv_to_mongo()

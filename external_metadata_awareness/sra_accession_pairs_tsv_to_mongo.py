import pymongo
import csv
import click
import datetime
from typing import List


def get_iso_timestamp() -> str:
    """Return the current timestamp in ISO 8601 format."""
    return datetime.datetime.now().isoformat()


@click.command()
@click.option("--file-path", type=click.Path(exists=True), required=True, help="Path to the TSV file.")
@click.option("--mongo-host", type=str, default="localhost", show_default=True, help="MongoDB host.")
@click.option("--mongo-port", type=int, default=27017, show_default=True, help="MongoDB port.")
@click.option("--database", type=str, default="biosamples", show_default=True, help="MongoDB database name.")
@click.option("--collection", type=str, default="biosamples_bioprojects", show_default=True,
              help="MongoDB collection name.")
@click.option("--batch-size", type=int, default=100000, show_default=True, help="Number of rows to insert per batch.")
@click.option("--report-interval", type=int, default=500000, show_default=True,
              help="Rows processed before showing progress.")
def load_tsv_to_mongo(
        file_path: str,
        mongo_host: str,
        mongo_port: int,
        database: str,
        collection: str,
        batch_size: int,
        report_interval: int
) -> None:
    """
    Load a large TSV file into MongoDB.

    - Skips rows with missing biosample or bioproject values.
    - Uses batch insertion for performance.
    - Reports progress periodically.

    Args:
        file_path (str): Path to the input TSV file.
        mongo_host (str): MongoDB server hostname or IP.
        mongo_port (int): MongoDB server port.
        database (str): MongoDB database name.
        collection (str): MongoDB collection name.
        batch_size (int): Number of records to insert per batch.
        report_interval (int): Number of records to process before displaying progress.
    """

    # MongoDB connection
    client = pymongo.MongoClient(host=mongo_host, port=mongo_port)
    db = client[database]
    collection = db[collection]

    total_rows = 0
    batch: List[dict] = []

    with open(file_path, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter="\t")
        total_file_rows = sum(1 for _ in file) - 1  # Count total rows (excluding header)
        file.seek(0)  # Reset file pointer after counting

        next(reader)  # Skip header
        for row in reader:
            biosample = row["biosample"].strip()
            bioproject = row["bioproject"].strip()

            if biosample and bioproject:  # Ignore empty values
                batch.append({
                    "biosample_accession": biosample,
                    "bioproject_accession": bioproject
                })

            total_rows += 1

            # Insert batch into MongoDB
            if len(batch) >= batch_size:
                collection.insert_many(batch)
                batch.clear()

            # Show progress at intervals
            if total_rows % report_interval == 0:
                percentage = (total_rows / total_file_rows) * 100
                print(f"[{get_iso_timestamp()}] Processed {total_rows:,}/{total_file_rows:,} rows ({percentage:.2f}%)")

        # Insert remaining batch
        if batch:
            collection.insert_many(batch)

    print(f"[{get_iso_timestamp()}] Data successfully loaded! Processed {total_rows:,} rows.")


if __name__ == "__main__":
    load_tsv_to_mongo()

import click
import pyarrow.parquet as pq
import datetime
import os
import pymongo
import time
from dotenv import load_dotenv

# Load .env file for MongoDB credentials
# todo specify source of .env file
#   not "as necessary" when running on NERSC Perlmutter?
load_dotenv()


def timestamp():
    """Returns the current time formatted for logs."""
    return f"[{time.strftime('%Y-%m-%d %H:%M:%S')}]"


def convert_dates(obj):
    """Recursively converts date objects to strings in nested structures."""
    if isinstance(obj, dict):
        return {k: convert_dates(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_dates(v) for v in obj]
    elif isinstance(obj, datetime.date):  # Convert dates to ISO format
        return obj.isoformat()
    else:
        return obj


def clean_record(record):
    """Removes 'jattr' and filters out fields where the value is None."""
    record.pop("jattr", None)  # Remove 'jattr' if present
    return {k: v for k, v in record.items() if v is not None}  # Remove None values


@click.command()
@click.option("--parquet-dir", type=click.Path(exists=True, file_okay=False), required=True,
              help="Path to the directory containing Parquet files")
@click.option("--nrows", default=None, type=int, help="Limit the number of records inserted per file (None = all)")
@click.option("--progress-interval", default=5000, type=int, help="Number of inserts between progress reports")
@click.option("--mongo-uri",
              default="mongodb://mam-ncbi:@mongo-ncbi-loadbalancer.mam.production.svc.spin.nersc.org:27017/admin?directConnection=true&authMechanism=SCRAM-SHA-256&authSource=admin",
              show_default=True, help="MongoDB connection URI")
@click.option("--mongo-db", default="ncbi_metadata", show_default=True, help="MongoDB database name")
@click.option("--mongo-collection", default="sra_metadata", show_default=True, help="MongoDB collection name")
@click.option("--drop-collection", is_flag=True, default=False,
              help="Drop the MongoDB collection before inserting new records")
def insert_parquet_to_mongo(parquet_dir, nrows, progress_interval, mongo_uri, mongo_db, mongo_collection,
                            drop_collection):
    """Insert Parquet records into MongoDB after processing, with controlled progress reporting."""

    # Inject password from .env into the MongoDB URI
    mongo_password = os.getenv("MONGO_PASSWORD")
    if not mongo_password:
        click.echo(f"{timestamp()} ERROR: MONGO_PASSWORD not found in .env file.", err=True)
        return

    mongo_uri = mongo_uri.replace("mam-ncbi:@", f"mam-ncbi:{mongo_password}@")

    # Connect to MongoDB
    client = pymongo.MongoClient(mongo_uri)
    db = client[mongo_db]
    collection = db[mongo_collection]

    # Drop collection if requested
    if drop_collection:
        click.echo(f"{timestamp()} Dropping collection '{mongo_collection}' in database '{mongo_db}'...")
        collection.drop()

    # List all files in the directory
    parquet_files = [os.path.join(parquet_dir, f) for f in os.listdir(parquet_dir) if
                     os.path.isfile(os.path.join(parquet_dir, f))]

    total_files = len(parquet_files)
    if total_files == 0:
        click.echo(f"{timestamp()} ERROR: No Parquet files found in the directory.")
        return

    click.echo(f"{timestamp()} Found {total_files} Parquet files. Starting processing.")

    start_time = time.time()  # Track total execution time
    total_inserted = 0  # Track total inserted rows

    # Process files one by one
    for i, file_path in enumerate(parquet_files):
        file_start = time.time()  # Track time per file
        parquet_file = os.path.basename(file_path)

        # Show immediate feedback before processing
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # Convert to MB
        click.echo(f"{timestamp()} [{i + 1}/{total_files}] Processing {parquet_file} ({file_size:.2f} MB)")

        # Open Parquet file
        reader = pq.ParquetFile(file_path)
        total_rows = sum(reader.metadata.row_group(i).num_rows for i in range(reader.num_row_groups))
        click.echo(f"{timestamp()}   - Total Rows: {total_rows}")

        # Apply `nrows` limit if set
        if nrows is not None:
            total_rows = min(nrows, total_rows)
            click.echo(f"{timestamp()}   - Applying row limit: {total_rows} rows")

        inserted_count = 0

        # Insert records one by one with controlled progress reporting
        for batch in reader.iter_batches(batch_size=1):  # Read one row at a time
            for record in [dict(zip(batch.to_pydict(), t)) for t in zip(*batch.to_pydict().values())]:
                record = convert_dates(clean_record(record))  # Remove jattr and filter out None values
                collection.insert_one(record)
                inserted_count += 1
                total_inserted += 1

                # Print progress at intervals
                if inserted_count % progress_interval == 0:
                    click.echo(
                        f"{timestamp()}   - Inserted: {inserted_count}/{total_rows} rows (File {i + 1}/{total_files}) | Total inserted: {total_inserted}")

                # Stop processing if we reached `nrows` limit
                if inserted_count >= total_rows:
                    break

        # File completed
        file_end = time.time()
        elapsed_time = file_end - file_start
        click.echo(f"{timestamp()} Done: {inserted_count} records inserted from {parquet_file} in {elapsed_time:.2f}s")

    total_time = time.time() - start_time
    click.echo(
        f"{timestamp()} Completed processing {total_files} files in {total_time / 60:.2f} minutes. Total inserted: {total_inserted} records.")


if __name__ == "__main__":
    insert_parquet_to_mongo()

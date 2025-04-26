import click
import pyarrow.parquet as pq
import datetime
import os
import time
from tqdm import tqdm
from itertools import islice

from external_metadata_awareness.mongodb_connection import get_mongo_client


def timestamp():
    return f"[{time.strftime('%Y-%m-%d %H:%M:%S')}]"


def convert_dates(obj):
    if isinstance(obj, dict):
        return {k: convert_dates(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_dates(v) for v in obj]
    elif isinstance(obj, datetime.date):
        return obj.isoformat()
    return obj


def clean_record(record):
    record.pop("jattr", None)
    return {k: v for k, v in record.items() if v is not None}


def get_parquet_files(parquet_dir):
    return [
        os.path.join(parquet_dir, f)
        for f in os.listdir(parquet_dir)
        if os.path.isfile(os.path.join(parquet_dir, f))
    ]


# Removed the maybe_inject_password function as it's replaced by get_mongo_client


@click.command()
@click.option("--parquet-dir", type=click.Path(exists=True, file_okay=False), required=True,
              help="Directory containing Parquet files")
@click.option("--nrows", default=None, type=int,
              help="Max total records to insert (across all files)")
@click.option("--progress-interval", default=5000, type=int,
              help="Print progress every N records")
@click.option("--mongo-uri", required=True,
              help="MongoDB connection URI (must start with mongodb:// and include database name)")
@click.option("--mongo-collection", default="sra_metadata", show_default=True,
              help="MongoDB collection name")
@click.option("--drop-collection", is_flag=True, default=False,
              help="Drop the MongoDB collection before inserting new records")
@click.option("--env-file", default=None,
              help="Path to .env file for credentials (should contain MONGO_USER and MONGO_PASSWORD)")
@click.option("--verbose", is_flag=True, help="Show verbose connection output")
def insert_parquet_to_mongo(parquet_dir, nrows, progress_interval,
                            mongo_uri, mongo_collection,
                            drop_collection, env_file, verbose):
    """Insert records from Parquet into MongoDB with optional row limit and progress bars."""
    # Use the unified MongoDB connection utility
    client = get_mongo_client(
        mongo_uri=mongo_uri,
        env_file=env_file,
        debug=verbose
    )
    
    # Extract database name from URI using pymongo's uri_parser
    from pymongo import uri_parser
    parsed = uri_parser.parse_uri(mongo_uri)
    db_name = parsed.get('database')
    
    if not db_name:
        tqdm.write(f"{timestamp()} ERROR: MongoDB URI must include a database name")
        raise click.Abort()
        
    collection = client[db_name][mongo_collection]

    if drop_collection:
        tqdm.write(f"{timestamp()} Dropping collection '{mongo_collection}'...")
        collection.drop()

    parquet_files = get_parquet_files(parquet_dir)
    if not parquet_files:
        tqdm.write(f"{timestamp()} ERROR: No Parquet files found.")
        raise click.Abort()

    tqdm.write(f"{timestamp()} Found {len(parquet_files)} files. Starting...")

    total_inserted = 0
    processed_files = 0
    start_time = time.time()

    for i, file_path in enumerate(tqdm(parquet_files, desc="Processing Parquet files")):
        if nrows is not None and total_inserted >= nrows:
            tqdm.write(f"{timestamp()} Reached global row limit ({nrows}). Stopping.")
            break

        processed_files += 1
        file_start = time.time()
        filename = os.path.basename(file_path)
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        tqdm.write(f"{timestamp()} [{i + 1}/{len(parquet_files)}] {filename} ({file_size_mb:.2f} MB)")

        reader = pq.ParquetFile(file_path)
        total_rows = sum(reader.metadata.row_group(i).num_rows for i in range(reader.num_row_groups))
        tqdm.write(f"{timestamp()}   - Total rows: {total_rows}")

        inserted_count = 0
        remaining_global = float('inf') if nrows is None else max(0, nrows - total_inserted)
        file_row_limit = min(total_rows, remaining_global)

        with tqdm(total=file_row_limit, desc=f"Inserting from {filename}", leave=False) as pbar:
            break_outer = False
            batch_size = min(500, file_row_limit)

            for batch in reader.iter_batches(batch_size=batch_size):
                records = [convert_dates(clean_record(r)) for r in batch.to_pylist()]

                if nrows is not None and total_inserted + len(records) > nrows:
                    records = records[: nrows - total_inserted]
                    break_outer = True

                if records:
                    collection.insert_many(records)
                    inserted_count += len(records)
                    total_inserted += len(records)
                    pbar.update(len(records))

                if break_outer:
                    break

        elapsed = time.time() - file_start
        tqdm.write(f"{timestamp()} Done: {inserted_count} from {filename} in {elapsed:.2f}s")

    total_elapsed = time.time() - start_time
    tqdm.write(
        f"{timestamp()} Finished {processed_files} file(s) in {total_elapsed / 60:.2f} min. Total inserted: {total_inserted}")


if __name__ == "__main__":
    insert_parquet_to_mongo()

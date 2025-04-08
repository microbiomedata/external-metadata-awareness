import click
import pyarrow.parquet as pq
import datetime
import os
import pymongo
import time
from dotenv import load_dotenv
from tqdm import tqdm
from itertools import islice


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


def maybe_inject_password(mongo_uri, dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)
    if "mam-ncbi:@" in mongo_uri:
        mongo_password = os.getenv("MONGO_PASSWORD")
        if not mongo_password:
            tqdm.write(f"{timestamp()} ERROR: MONGO_PASSWORD not found in .env file.")
            raise click.Abort()
        mongo_uri = mongo_uri.replace("mam-ncbi:@", f"mam-ncbi:{mongo_password}@")
    return mongo_uri


@click.command()
@click.option("--parquet-dir", type=click.Path(exists=True, file_okay=False), required=True,
              help="Directory containing Parquet files")
@click.option("--nrows", default=None, type=int,
              help="Max total records to insert (across all files)")
@click.option("--progress-interval", default=5000, type=int,
              help="Print progress every N records")
@click.option("--mongo-uri",
              default="mongodb://mam-ncbi:@mongo-ncbi-loadbalancer.mam.production.svc.spin.nersc.org:27017/admin?directConnection=true&authMechanism=SCRAM-SHA-256&authSource=admin",
              show_default=True, help="MongoDB URI")
@click.option("--mongo-db", default="ncbi_metadata", show_default=True,
              help="MongoDB database name")
@click.option("--mongo-collection", default="sra_metadata", show_default=True,
              help="MongoDB collection name")
@click.option("--drop-collection", is_flag=True, default=False,
              help="Drop the MongoDB collection before inserting new records")
@click.option("--dotenv-path", type=click.Path(exists=True, dir_okay=False), default=".env",
              show_default=True, help="Path to the .env file to load")
def insert_parquet_to_mongo(parquet_dir, nrows, progress_interval,
                            mongo_uri, mongo_db, mongo_collection,
                            drop_collection, dotenv_path):
    """Insert records from Parquet into MongoDB with optional row limit and progress bars."""
    mongo_uri = maybe_inject_password(mongo_uri, dotenv_path)
    client = pymongo.MongoClient(mongo_uri)
    collection = client[mongo_db][mongo_collection]

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

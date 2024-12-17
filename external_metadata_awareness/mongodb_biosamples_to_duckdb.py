import click
import pandas as pd
from datetime import datetime
import time
import pymongo
import duckdb

# does not account for
#   BioSample.Owner.Contacts (highly nested). we ARE processing BioSample.Owner.Name
#   BioSample.Description.Comment.Table (exclusively antibiograms)
legal_paths = [
    "BioSample",
    "BioSample.Attributes.Attribute",
    "BioSample.Curation",
    "BioSample.Description.Comment.Paragraph",
    "BioSample.Description.Organism",
    "BioSample.Description.Organism.OrganismName",
    "BioSample.Description.Synonym",
    "BioSample.Description.Title",
    "BioSample.Ids.Id",
    "BioSample.Links.Link",
    "BioSample.Models.Model",
    "BioSample.Owner.Name",
    "BioSample.Package",
    "BioSample.Status"
]


def create_duckdb_file(filename):
    """
    Creates a file-based DuckDB database and returns the connection.

    Args:
        filename: The name of the DuckDB database file to create.

    Returns:
        duckdb.DuckDBPyConnection: The DuckDB connection object.
    """
    conn = duckdb.connect(database=filename)
    return conn


def infer_duckdb_type(series, col_name):
    if col_name.lower() == "id":
        return "BIGINT"
    if pd.api.types.is_integer_dtype(series):
        return "BIGINT"
    elif pd.api.types.is_float_dtype(series):
        return "DOUBLE"
    elif pd.api.types.is_bool_dtype(series):
        return "BOOLEAN"
    return "TEXT"


def ensure_columns_exist(conn, table_name, df):
    table_info = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    existing_columns = {col[1].lower() for col in table_info}
    new_columns = [c for c in df.columns if c.lower() not in existing_columns]
    if new_columns:
        print(f"{datetime.now().isoformat()}: Adding {len(new_columns)} new column(s) to {table_name}.")
    for col in new_columns:
        dtype = infer_duckdb_type(df[col], col)
        alter_sql = f'ALTER TABLE {table_name} ADD COLUMN "{col}" {dtype}'
        conn.execute(alter_sql)


def insert_df(conn, table_name, df):
    table_info = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    existing_columns = [col[1] for col in table_info]

    for col in existing_columns:
        if col not in df.columns:
            df[col] = None

    df = df[existing_columns]

    conn.register("temp_df", df)
    conn.execute(f"INSERT INTO {table_name} SELECT * FROM temp_df")
    conn.unregister("temp_df")


def process_data(data, id_value):
    if isinstance(data, dict):
        scalar_data = {k: v for k, v in data.items() if isinstance(v, (str, int, float, bool))}
        scalar_data["id"] = int(id_value) if id_value is not None else None
        return pd.DataFrame([scalar_data])
    elif isinstance(data, list) and all(isinstance(item, dict) for item in data):
        all_scalar_data = []
        for item in data:
            scalar_data = {k: v for k, v in item.items() if isinstance(v, (str, int, float, bool))}
            scalar_data["id"] = int(id_value) if id_value is not None else None
            all_scalar_data.append(scalar_data)
        if all_scalar_data:
            return pd.DataFrame(all_scalar_data)
        else:
            return None
    else:
        return None


def extract_all_paths_data(collection, conn, paths, max_docs=None, client=None, batch_size=10000):
    """
    Process multiple paths in a single scan of the MongoDB collection.
    Provides verbose status updates:
      - A start message at the beginning.
      - Roughly every minute, prints how many docs have been processed so far.
      - Messages when flushing batches and at the end.
    """

    if client is None:
        raise ValueError("Client must be provided to start a session for no_cursor_timeout.")

    # Data structures to track per-path info
    path_info = {}
    for path in paths:
        table_name = path.split(".")[-1].replace("-", "_").replace(".", "_").lower()
        path_info[path] = {
            "table_name": table_name,
            "table_created": False,
            "batch": [],
            "processed_docs": 0  # how many docs contributed rows for this path
        }

    def flush_batch(path, combined_df):
        info = path_info[path]
        if not info["table_created"]:
            # Create table from the first batch
            schema_parts = []
            for col in combined_df.columns:
                dtype = infer_duckdb_type(combined_df[col], col)
                schema_parts.append(f'"{col}" {dtype}')
            schema_sql = ", ".join(schema_parts)
            conn.execute(f"CREATE TABLE {info['table_name']} ({schema_sql})")
            info["table_created"] = True
        else:
            ensure_columns_exist(conn, info['table_name'], combined_df)

        insert_df(conn, info['table_name'], combined_df)
        print(
            f"{datetime.now().isoformat()}: Flushed batch for {info['table_name']}, total {info['processed_docs']} docs processed for this path so far.")
        info["batch"].clear()

    # Print a start message
    print(f"{datetime.now().isoformat()}: Starting extraction for paths: {paths}")
    start_time = time.time()
    last_status_time = start_time

    with client.start_session() as session:
        cursor = collection.find({}, no_cursor_timeout=True, session=session)
        doc_count = 0
        for doc in cursor:
            if max_docs is not None and doc_count >= max_docs:
                break
            doc_count += 1

            # Extract data for each path
            for path in paths:
                if path == "BioSample":
                    # top-level
                    scalar_data = {k: v for k, v in doc.items() if isinstance(v, (str, int, float, bool))}
                    scalar_data["id"] = int(doc["id"]) if "id" in doc else None
                    df = pd.DataFrame([scalar_data]) if scalar_data else None
                else:
                    path_parts = path.split(".")[1:]
                    current_data = doc
                    for part in path_parts:
                        current_data = current_data.get(part)
                        if current_data is None:
                            break
                    if current_data is not None:
                        df = process_data(current_data, doc.get('id'))
                    else:
                        df = None

                if df is not None and not df.empty:
                    info = path_info[path]
                    info["batch"].append(df)
                    info["processed_docs"] += 1

                    # Check if we need to flush for this path
                    if len(info["batch"]) >= batch_size:
                        combined_df = pd.concat(info["batch"], ignore_index=True)
                        flush_batch(path, combined_df)

            # Periodic status update roughly every minute
            current_time = time.time()
            if (current_time - last_status_time) > 60:
                # Print a status message
                print(f"{datetime.now().isoformat()}: Processed {doc_count} documents so far.")
                for p, info in path_info.items():
                    print(
                        f"  Path: {p}, Table: {info['table_name']}, Docs for path: {info['processed_docs']}, Batch size: {len(info['batch'])}")
                last_status_time = current_time

        cursor.close()

    # Flush remaining batches
    for path, info in path_info.items():
        if info["batch"]:
            combined_df = pd.concat(info["batch"], ignore_index=True)
            flush_batch(path, combined_df)
            print(
                f"{datetime.now().isoformat()}: Final flush - total {info['processed_docs']} documents processed for {info['table_name']}.")

    # Print a completion message
    total_time = time.time() - start_time
    print(
        f"{datetime.now().isoformat()}: Completed extraction. Processed {doc_count} documents in {total_time:.2f} seconds.")
    for p, info in path_info.items():
        print(f"  Path: {p}, Table: {info['table_name']}, Total Docs: {info['processed_docs']}")


@click.group()
def cli():
    """CLI tool for processing and storing biosample data."""
    pass


@cli.command()
@click.option('--mongo_uri', '-m', type=str, required=True, help='MongoDB connection URI')
@click.option('--db_name', '-d', type=str, required=True, help='Name of the MongoDB database')
@click.option('--collection', '-c', type=str, required=True, help='Name of the MongoDB collection')
@click.option('--duckdb_file', '-f', type=click.Path(exists=False), required=True,
              help='Path to the DuckDB database file')
@click.option('--paths', '-p', type=click.Choice(legal_paths), multiple=True, required=False,
              help='List of paths to extract data from (e.g., BioSample, BioSample.Attributes.Attribute).')
@click.option('--max_docs', '-x', type=int, default=None,
              help='Maximum number of documents to process (default: no limit)')
@click.option('--batch_size', '-b', type=int, default=20000, help='Batch size for processing data (default: 20000)')
def extract(mongo_uri, db_name, collection, duckdb_file, paths, max_docs, batch_size):
    """Extract data from MongoDB and store it in a DuckDB database."""
    client = pymongo.MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection]

    duckdb_conn = create_duckdb_file(duckdb_file)

    if len(paths) == 0:
        paths = legal_paths

    extract_all_paths_data(collection, duckdb_conn, paths, max_docs, client, batch_size)

    duckdb_conn.close()
    client.close()

    print(f"Processing completed. See logs for details.")


if __name__ == '__main__':
    cli()

import duckdb
import click
import pandas as pd
from typing import Optional
from datetime import datetime


@click.command()
@click.option(
    '--db-path',
    required=True,
    type=str,
    help='Path to the DuckDB database file.'
)
@click.option(
    '--output-table',
    required=True,
    type=str,
    help='Name of the output table for storing pivot results.'
)
@click.option(
    '--max-id',
    required=False,
    type=int,
    default=None,
    help='Maximum id value to process (inclusive). If not set, processes all ids.'
)
@click.option(
    '--batch-size',
    required=False,
    type=int,
    default=100000,
    help='Number of ids to process per batch.'
)
@click.option(
    '--delimiter',
    required=False,
    type=str,
    default='|||',
    help='Delimiter used to concatenate multiple content values (default: "|||").'
)
@click.option(
    '--log-file',
    required=False,
    type=str,
    default='pivot_log.txt',
    help='Path to the log file for reporting multiple content values.'
)
def pivot_table(db_path: str, output_table: str, max_id: Optional[int], batch_size: int, delimiter: str, log_file: str):
    """
    Create a pivot table from ncbi_biosamples.main.attributes in DuckDB.

    Parameters:
    - db-path: Path to the DuckDB database file.
    - output-table: Name of the output table for storing pivot results.
    - max-id: Maximum id value to process (inclusive).
    - batch-size: Number of ids to process per batch.
    - delimiter: Delimiter used to concatenate multiple content values.
    - log-file: Path to the log file for reporting multiple content values.
    """
    # Check for file lock by attempting to connect
    try:
        con = duckdb.connect(db_path)
    except duckdb.IOException as e:
        print(
            f"Error: Unable to open DuckDB file at '{db_path}'. It may be locked by another process, such as DBeaver.")
        print(f"Details: {str(e)}")
        return
    except Exception as e:
        print(f"Unexpected error occurred while opening the DuckDB file: {str(e)}")
        return

    # Log start time and max_id
    print_log(f"Starting pivot table creation.", max_id, log_file)

    # Step 1: Check if the output table exists using PRAGMA show_tables
    existing_tables_query = "PRAGMA show_tables;"
    existing_tables = [table[0] for table in con.execute(existing_tables_query).fetchall()]

    if output_table in existing_tables:
        # Generate a new table name with a timestamp
        timestamp_suffix = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        new_output_table = f"{output_table}_{timestamp_suffix}"
        print_log(f"!!!! WARNING !!!!", max_id, log_file)
        print_log(f"Table '{output_table}' already exists.", max_id, log_file)
        print_log(f"Using new table name: '{new_output_table}'.", max_id, log_file)
        print_log(f"!!!!!!!!!!!!!!!!!!!", max_id, log_file)
        print("\n" + "=" * 80)
        print(f"NOTICE: Table '{output_table}' already exists.")
        print(f"Using new table name: '{new_output_table}'.")
        print("=" * 80 + "\n")
        output_table = new_output_table
    else:
        print_log(f"Using table '{output_table}' for output.", max_id, log_file)

    # Step 2: Determine all unique harmonized_name values to use as columns
    print_log("Fetching distinct harmonized_name values...", max_id, log_file)
    column_query = """
    SELECT DISTINCT harmonized_name
    FROM ncbi_biosamples.main.attributes
    WHERE harmonized_name IS NOT NULL AND harmonized_name != ''
    ORDER BY harmonized_name
    """
    harmonized_names = con.execute(column_query).fetchdf()['harmonized_name'].tolist()

    # Step 3: Create the table schema in DuckDB
    columns = ['id'] + harmonized_names
    column_definitions = ", ".join([f"{col} VARCHAR" for col in harmonized_names])
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {output_table} (
        id INTEGER,
        {column_definitions}
    );
    """
    con.execute(create_table_query)

    # Create an empty DataFrame with the correct columns
    empty_pivot_df = pd.DataFrame(columns=columns)

    # Step 4: Prepare the base query to filter rows
    base_query = f"""
    SELECT id, harmonized_name, content
    FROM ncbi_biosamples.main.attributes
    WHERE harmonized_name IS NOT NULL AND harmonized_name != '' 
      AND content IS NOT NULL AND content != ''
    """
    if max_id is not None:
        base_query += f" AND id <= {max_id}"

    # Step 5: Fetch minimum and maximum ids for the selected range
    min_id_query = f"SELECT MIN(id) FROM ({base_query})"
    max_id_query = f"SELECT MAX(id) FROM ({base_query})"
    min_id = con.execute(min_id_query).fetchone()[0]
    max_id = con.execute(max_id_query).fetchone()[0]

    # Log the ID range being processed
    print_log(f"Processing IDs from {min_id} to {max_id}.", max_id, log_file)

    # Step 6: Process ids in ranges defined by the batch size
    current_min_id = min_id
    while current_min_id <= max_id:
        current_max_id = min(current_min_id + batch_size - 1, max_id)
        print_log(f"Processing batch with ids from {current_min_id} to {current_max_id}...", max_id, log_file)

        # Fetch the data for the current range of IDs
        query = f"""
        SELECT id, harmonized_name, GROUP_CONCAT(content, '{delimiter}') AS combined_content
        FROM ({base_query}) as subquery
        WHERE id >= {current_min_id} AND id <= {current_max_id}
        GROUP BY id, harmonized_name
        """
        batch_df = con.execute(query).fetchdf()

        # Check for multiple content values and log if needed
        with open(log_file, 'a') as log:
            multiple_content_df = batch_df[batch_df['combined_content'].str.contains(delimiter)]
            if not multiple_content_df.empty:
                log.write(
                    f"{timestamp()} - Max ID: {max_id} - Multiple content values found for the following id and harmonized_name combinations:\n")
                log.write(multiple_content_df.to_string(index=False))
                log.write('\n\n')

        # Create a pivot table for the current batch
        pivot_df = batch_df.pivot(index='id', columns='harmonized_name', values='combined_content').reset_index()

        # Ensure all columns are strings, and replace NaN with None for SQL NULL
        pivot_df = pivot_df.astype(str).where(pd.notnull(pivot_df), None)

        # Align the pivot DataFrame with the predefined columns and fill missing columns
        pivot_df = pd.concat([empty_pivot_df, pivot_df], axis=0, ignore_index=True)[columns]

        # Write the pivot batch to the DuckDB table
        con.append(output_table, pivot_df)
        print_log(f"Batch with ids from {current_min_id} to {current_max_id} processed and inserted.", max_id, log_file)

        # Move to the next batch
        current_min_id = current_max_id + 1

    # Close the connection
    con.close()
    print_log(f"Pivot table created successfully in '{output_table}'.", max_id, log_file)


def timestamp() -> str:
    """Returns the current date and time as a formatted string."""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def print_log(message: str, max_id: Optional[int], log_file: str):
    """Prints a message with a timestamp, max id, and logs it to a file."""
    max_id_info = f"Max ID: {max_id if max_id is not None else 'No limit'}"
    message_with_time = f"{timestamp()} - {max_id_info} - {message}"
    print(message_with_time)
    # with open(log_file, 'a') as log:
    #     log.write(message_with_time + '\n')


if __name__ == '__main__':
    pivot_table()

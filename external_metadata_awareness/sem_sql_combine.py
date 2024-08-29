import sqlite3
import click


@click.command()
@click.option('--primary-db', required=True, type=click.Path(exists=True), help='Path to the primary SQLite database.')
@click.option('--secondary-db', required=True, type=click.Path(exists=True),
              help='Path to the secondary SQLite database.')
def merge_databases_with_deduplication(primary_db: str, secondary_db: str) -> None:
    """
    Merge tables from a secondary SQLite database into a primary SQLite database with full row deduplication.

    This script attaches a secondary SQLite database to a primary database,
    iterates over each table, and merges rows into the primary database
    while ensuring that only unique rows are inserted.

    :param primary_db: Path to the primary SQLite database.
    :param secondary_db: Path to the secondary SQLite database.
    """
    # Connect to the primary database
    primary_conn = sqlite3.connect(primary_db)
    primary_cursor = primary_conn.cursor()

    # Attach the secondary database
    primary_cursor.execute(f"ATTACH DATABASE '{secondary_db}' AS secondary_db")

    # Get a list of all tables in the primary database
    primary_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    primary_tables = primary_cursor.fetchall()

    # Iterate over each table and merge the data with deduplication
    for (table_name,) in primary_tables:
        print(f"Merging table: {table_name}")

        # Check if the table exists in the secondary database
        primary_cursor.execute(
            f"SELECT name FROM secondary_db.sqlite_master WHERE type='table' AND name='{table_name}'")
        if primary_cursor.fetchone():
            # Perform a UNION operation to combine and deduplicate rows
            primary_cursor.execute(f"""
                CREATE TEMP TABLE temp_table AS
                SELECT * FROM {table_name}
                UNION
                SELECT * FROM secondary_db.{table_name}
            """)

            # Delete all rows in the primary table
            primary_cursor.execute(f"DELETE FROM {table_name}")

            # Insert deduplicated rows back into the primary table
            primary_cursor.execute(f"INSERT INTO {table_name} SELECT * FROM temp_table")

            # Drop the temporary table
            primary_cursor.execute("DROP TABLE temp_table")

            print(f"Rows from {table_name} in secondary_db merged and deduplicated into primary_db.")

    # Commit changes and close the connection
    primary_conn.commit()
    primary_conn.close()
    print("All tables merged successfully with full row deduplication!")


if __name__ == '__main__':
    merge_databases_with_deduplication()

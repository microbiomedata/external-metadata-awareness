import click
import duckdb


@click.command()
@click.option('--db-path', required=True, type=click.Path(), help='Path to the DuckDB file.')
@click.option('--table-name', required=True, help='Name of the table to update.')
@click.option('--key', 'etl_key', required=True, help='Key to update or insert.')
@click.option('--value', 'etl_value', required=True, help='Value to set for the key.')
@click.option('--overwrite', is_flag=True, help='Overwrite the value if the key exists.')
def main(db_path: str, table_name: str, etl_key: str, etl_value: str, overwrite: bool) -> None:
    """
    Update or insert an etl_key-etl_value pair in the specified DuckDB table.

    Args:
        db_path (str): Path to the DuckDB file.
        table_name (str): Name of the table to update.
        etl_key (str): Key to update or insert.
        etl_value (str): Value to set for the key.
        overwrite (bool): Whether to overwrite the value if the key exists.
    """
    with duckdb.connect(db_path) as conn:
        # Ensure the table exists with the correct schema
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                etl_key STRING PRIMARY KEY,
                etl_value STRING
            )
        """)

        # Verify the column schema matches expectations
        columns = [col[0] for col in conn.execute(f"DESCRIBE {table_name}").fetchall()]
        if 'etl_key' not in columns or 'etl_value' not in columns:
            click.echo(f"Error: Table '{table_name}' does not have required columns 'etl_key' and 'etl_value'.")
            exit(1)

        # Check if the key already exists
        existing_key = conn.execute(
            f"SELECT 1 FROM {table_name} WHERE etl_key = ?", (etl_key,)
        ).fetchone()

        if existing_key and not overwrite:
            click.echo(f"Key '{etl_key}' already exists in '{table_name}'. Use --overwrite to update it.")
            return

        # Insert or update the row
        conn.execute(
            f"""
            INSERT INTO {table_name} (etl_key, etl_value)
            VALUES (?, ?)
            ON CONFLICT (etl_key) DO UPDATE SET etl_value = EXCLUDED.etl_value
            """,
            (etl_key, etl_value)
        )

        click.echo(f"Key '{etl_key}' updated in '{table_name}' with value '{etl_value}'.")


if __name__ == '__main__':
    main()

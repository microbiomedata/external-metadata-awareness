import click
import duckdb
import pandas as pd
from extract_all_ncbi_packages_fields import parse_xml, discover_not_appropriate_keys, process_package_nodes


def insert_dataframe_to_duckdb(
        df: pd.DataFrame, db_path: str, table_name: str, overwrite: bool
):
    """
    Insert the DataFrame into a DuckDB database.

    Args:
        df (pd.DataFrame): The DataFrame to insert.
        db_path (str): Path to the DuckDB file.
        table_name (str): Name of the table to insert data into.
        overwrite (bool): Whether to overwrite the table if it exists.
    """
    # Connect to the DuckDB database
    with duckdb.connect(db_path) as conn:
        # Check if the table exists
        table_exists = conn.execute(
            f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{table_name}'"
        ).fetchone()[0] > 0

        if table_exists and not overwrite:
            click.echo(f"Error: Table '{table_name}' already exists. Use --overwrite to overwrite it.")
            exit(1)

        if table_exists and overwrite:
            conn.execute(f"DROP TABLE {table_name}")

        # Create the table and insert the data
        conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM df LIMIT 0;")
        conn.register("df_view", df)
        conn.execute(f"INSERT INTO {table_name} SELECT * FROM df_view;")
        click.echo(f"Data inserted into table '{table_name}' in {db_path}")


@click.command()
@click.option('--xml-file', required=True, type=click.Path(exists=True), help='Path to the XML file.')
@click.option('--db-path', required=True, type=click.Path(), help='Path to the DuckDB file.')
@click.option('--table-name', required=True, help='Name of the table to insert data into.')
@click.option('--overwrite', is_flag=True, help='Overwrite the table if it exists.')
def main(xml_file: str, db_path: str, table_name: str, overwrite: bool):
    """
    Process an XML file and insert the resulting data into a DuckDB database.

    Args:
        xml_file (str): Path to the input XML file.
        db_path (str): Path to the DuckDB file.
        table_name (str): Name of the table to insert data into.
        overwrite (bool): Whether to overwrite the table if it exists.
    """
    # Parse the XML and process the packages
    root = parse_xml(xml_file)
    not_appropriate_keys = discover_not_appropriate_keys(root)
    df = process_package_nodes(root, not_appropriate_keys)

    # Insert the DataFrame into DuckDB
    insert_dataframe_to_duckdb(df, db_path, table_name, overwrite)


if __name__ == '__main__':
    main()

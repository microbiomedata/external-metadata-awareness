import click
import os
from sqlalchemy import create_engine
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join("local", ".env"))


@click.command()
@click.option('--sql-file', type=click.Path(exists=True), required=True, help="Path to the SQL query file.")
@click.option('--output-file', type=click.Path(), required=True, help="Path to the output TSV file.")
def run_query(sql_file: str, output_file: str):
    """
    Executes a SQL query from a file against a PostgreSQL database and saves the results to a TSV file.

    Args:
    sql_file (str): The file path to the SQL file containing the query.
    output_file (str): The file path where the TSV results should be saved.
    """
    # Extract the database connection URL from the environment variables
    database_url = os.getenv("BIOSAMPLES_PG_DATABASE_URL")
    if not database_url:
        click.echo("Database URL not found in environment variables.", err=True)
        return

    # Create an SQLAlchemy engine
    engine = create_engine(database_url)

    # Read SQL query from file
    try:
        with open(sql_file, 'r') as file:
            sql_query = file.read()
    except IOError as e:
        click.echo(f"Error reading the SQL file: {e}", err=True)
        return

    # Execute the SQL query using pandas to handle the results
    try:
        df = pd.read_sql(sql_query, engine)
        click.echo(f"Query executed successfully. Retrieved {len(df)} records.")
    except Exception as e:
        click.echo(f"Failed to execute query: {e}", err=True)
        return

    # Write the results to a TSV file using pandas
    try:
        df.to_csv(output_file, sep='\t', index=False)
        click.echo(f"Results saved to {output_file}.")
    except IOError as e:
        click.echo(f"Failed to write to TSV file: {e}", err=True)


if __name__ == '__main__':
    run_query()

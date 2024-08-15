import os
from dotenv import load_dotenv
import pandas as pd
import sqlalchemy as sa
import click

# Load environment variables from .env file
load_dotenv('local/.env')


@click.command()
@click.option('--tsv-file', type=click.Path(exists=True), required=True, help='Path to the TSV file to be loaded.')
@click.option('--table-name', type=str, required=True, help='Name of the table where data will be loaded.')
def load_tsv_to_postgres(tsv_file: str, table_name: str) -> None:
    """
    Reads a TSV file into a pandas DataFrame and loads it into a PostgreSQL database.

    :param tsv_file: Path to the TSV file to be loaded.
    :param table_name: Name of the table where data will be loaded.
    """
    try:
        # Read the connection string from the environment variable
        database_url = os.getenv('BIOSAMPLES_PG_DATABASE_URL')
        if not database_url:
            raise ValueError("The environment variable 'BIOSAMPLES_PG_DATABASE_URL' is not set.")

        # Read TSV file into DataFrame
        df = pd.read_csv(tsv_file, sep='\t')
        click.echo(f"Successfully read TSV file: {tsv_file}")

        # Create a SQLAlchemy engine
        engine = sa.create_engine(database_url)
        click.echo("Database engine created.")

        # Load DataFrame into PostgreSQL table
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        click.echo(f"Data successfully loaded into table '{table_name}'.")

    except Exception as e:
        click.echo(f"An error occurred: {e}")


if __name__ == '__main__':
    load_tsv_to_postgres()

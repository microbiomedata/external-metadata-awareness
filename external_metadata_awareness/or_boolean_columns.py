import pandas as pd
import click


@click.command()
@click.option('--input-file', type=str, help='Input TSV file name.')
@click.option('--output-file', type=str, help='Output TSV file name.')
@click.option('--column1', type=str, help='Name of the first boolean column.')
@click.option('--column2', type=str, help='Name of the second boolean column.')
def process_tsv(input_file: str, output_file: str, column1: str, column2: str):
    """
    Processes a TSV file to calculate the logical OR of two boolean columns.

    :param input_file: Name of the input TSV file.
    :param output_file: Name of the output TSV file where results will be saved.
    :param column1: Name of the first boolean column to consider.
    :param column2: Name of the second boolean column to consider.
    """
    # Load the data from TSV file
    df = pd.read_csv(input_file, sep='\t')

    # Validate that the specified columns exist
    if column1 not in df.columns or column2 not in df.columns:
        raise ValueError(f"Columns {column1} and/or {column2} not found in the input file.")

    # Calculate the OR of the two columns
    df[f'{column1}_or_{column2}'] = df[column1] | df[column2]

    # Save the new DataFrame to a TSV file
    df.to_csv(output_file, sep='\t', index=False)

    # Notify user of success
    click.echo(f'File processed and output saved to {output_file}')


if __name__ == '__main__':
    process_tsv()

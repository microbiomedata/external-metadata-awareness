import click
import pandas as pd
from typing import Dict, Set


def load_class_info(file_path: str, subset_label: str) -> Set[str]:
    """
    Load class info from a file and return a set of CURIEs for the specified subset.

    Args:
        file_path (str): Path to the class info file.
        subset_label (str): Label of the subset to filter for.

    Returns:
        Set[str]: Set of CURIEs belonging to the specified subset.
    """
    subset_curies = set()
    with open(file_path, 'r') as f:
        for line in f:
            parts = line.strip().split(' ! ')
            if len(parts) == 2:
                subset_curies.add(parts[0])
    return subset_curies


@click.command()
@click.option('--tsv-file', required=True, help='Path to the input tsv file')
@click.option('--class-info-file', required=True, help='Path to the class info file')
@click.option('--output-file', required=True, help='')
@click.option('--tsv-column-name', required=True, help='Name of the column to check in the tsv file')
@click.option('--subset-label', required=True, help='Label of the subset to filter for')
def process_tsv(tsv_file: str, class_info_file: str, tsv_column_name: str, subset_label: str, output_file: str):
    """
    Process a tsv file to determine if values in a specified column are in a given ontology subset.

    This script reads a tsv file and a class info file, checks if the values in the specified
    column of the tsv file are present in the given subset of the ontology, and adds a new
    boolean column to indicate the presence or absence in the subset.

    Args:
        tsv_file (str): Path to the input tsv file.
        class_info_file (str): Path to the class info file.
        tsv_column_name (str): Name of the column to check in the tsv file.
        subset_label (str): Label of the subset to filter for.
    """
    # Load the subset CURIEs
    subset_curies = load_class_info(class_info_file, subset_label)

    # Read the tsv file
    df = pd.read_csv(tsv_file, sep='\t')

    # Check if the specified column exists
    if tsv_column_name not in df.columns:
        click.echo(f"Error: Column '{tsv_column_name}' not found in the tsv file.")
        return

    # Create the new column name
    new_column_name = f"{tsv_column_name}_{subset_label}"

    # Add the new column with boolean values
    df[new_column_name] = df[tsv_column_name].isin(subset_curies)

    # Save the updated DataFrame to a new tsv file
    output_file = f"{output_file}"
    df.to_csv(output_file, index=False, sep='\t')
    click.echo(f"Updated tsv saved as: {output_file}")


if __name__ == '__main__':
    process_tsv()

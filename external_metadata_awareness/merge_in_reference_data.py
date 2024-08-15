import click
import pandas as pd
from typing import Tuple, Optional

pd.set_option('display.max_columns', None)


@click.command()
@click.option('--keep-file', type=click.Path(exists=True), required=True, help='Path to the keep CSV file')
@click.option('--reference-file', type=click.Path(exists=True), required=True, help='Path to the reference CSV file')
@click.option('--keep-key', type=str, required=True,
              help='Name of the key column in keep file for merging and null/blank check')
@click.option('--reference-key', type=str, required=True,
              help='Name of the key column in reference file for merging and null/blank check')
@click.option('--reference-addition', type=str, required=True,
              help='Name of the additional column from reference file to include in merge')
@click.option('--addition-rename', type=str, required=True,
              help='Name to rename the additional column in the merged file')
@click.option('--merged-file', type=click.Path(), required=True, help='Path to save the merged CSV file')
def process_csvs(keep_file: str, reference_file: str, keep_key: str, reference_key: str, reference_addition: str,
                 merged_file: str, addition_rename: str) -> None:
    """
    Read two CSV files (keep and reference), merge based on key columns, measure label similarity using Jaccard distance,
    and save the merged result with similarity metrics.

    Args:
        keep_file (str): Path to the keep CSV file.
        reference_file (str): Path to the reference CSV file.
        keep_key (str): Name of the key column in keep file for merging and null/blank check.
        reference_key (str): Name of the key column in reference file for merging and null/blank check.
        reference_addition (str): Name of the additional column from reference file to include in merge.
        merged_file (str): Path to save the merged CSV file.

    Returns:
        None
    """
    # Process keep file
    keep_notnull, keep_null = process_file(keep_file, keep_key, "keep")

    reference_notnull, reference_null = process_file(reference_file, reference_key, "reference")
    reference_notnull = reference_notnull.rename(columns={reference_addition: addition_rename})

    reference_notnull = reference_notnull[[reference_key, addition_rename]]

    merged_df = pd.merge(keep_notnull, reference_notnull, left_on=keep_key, right_on=reference_key, how='left')

    # Calculate Jaccard distance
    merged_df['jaccard_distance'] = merged_df.apply(
        lambda row: jaccard_distance(
            str(row['normalized_label']) if pd.notna(row['normalized_label']) else None,
            str(row[addition_rename]) if pd.notna(row[addition_rename]) else None
        ),
        axis=1
    )

    # Concatenate with null rows and save
    final_df = pd.concat([merged_df, keep_null], ignore_index=True)

    final_df.to_csv(merged_file, index=False)
    click.echo(f"Merged file saved to {merged_file}")


def process_file(input_file: str, key_column: str, file_type: str) -> Tuple[
    pd.DataFrame, pd.DataFrame]:
    """
    Process a single CSV file: read and split based on the key column.

    Args:
        input_file (str): Path to the input CSV file.
        key_column (str): Name of the key column to check for null/blank values.
        file_type (str): Type of file (keep or reference) for logging purposes.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: Two DataFrames, one with non-null values and one with null values.
    """
    # Read the CSV file
    df = pd.read_csv(input_file)

    # Check for normalized_curie column if it's the keep file
    if file_type == "keep" and key_column not in df.columns:
        raise ValueError("normalized_curie column not found in the keep file")

    # Split the DataFrame
    df_notnull, df_null = split_dataframe(df, key_column)

    click.echo(f"Split completed for {file_type} file.")

    return df_notnull, df_null


def split_dataframe(df: pd.DataFrame, key_column: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split a DataFrame into two based on whether a specified key column is null or blank.

    Args:
        df (pd.DataFrame): Input DataFrame.
        key_column (str): Name of the key column to check for null/blank values.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: Two DataFrames, one with non-null values and one with null values.
    """
    # Check if the column exists in the DataFrame
    if key_column not in df.columns:
        raise ValueError(f"Key column '{key_column}' not found in the DataFrame")

    # Split the DataFrame
    df_notnull = df[df[key_column].notna() & (df[key_column] != '')]
    df_null = df[df[key_column].isna() | (df[key_column] == '')]

    return df_notnull, df_null


def jaccard_distance(s1: Optional[str], s2: Optional[str]) -> Optional[float]:
    """Calculate Jaccard distance between two strings."""
    if not s1 or not s2:
        return None
    set1, set2 = set(s1.split()), set(s2.split())
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return 1 - (intersection / union) if union != 0 else 1


if __name__ == '__main__':
    process_csvs()

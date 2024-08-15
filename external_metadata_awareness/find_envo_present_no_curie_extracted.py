import pandas as pd
import click


def filter_dataframe(input_file: str, output_file: str) -> None:
    """
    Filter a DataFrame based on specific conditions and save the result to a CSV file.

    This function reads a CSV file into a DataFrame, applies a filter to select rows
    where the 'portion_parsed' column contains 'envo' (case-insensitive) and the
    'normalized_curie' column does not contain 'ENVO:'. The filtered DataFrame is
    printed and saved to a new CSV file.

    Args:
        input_file (str): Path to the input CSV file.
        output_file (str): Path to the output CSV file where the filtered data will be saved.

    Returns:
        None
    """
    # Read the CSV file
    df = pd.read_csv(input_file)

    # Apply the filter
    filtered_df = df[
        df['portion_parsed'].str.contains('envo', case=False, na=False) &
        ~df['normalized_curie'].str.contains('ENVO:', na=False)
        ]

    # Display the filtered rows
    print(filtered_df)

    # Save the filtered DataFrame to a new CSV file
    filtered_df.to_csv(output_file, index=False)


@click.command()
@click.option(
    '--input-file',
    type=click.Path(exists=True),
    default='normalized_data.csv',
    show_default=True,
    help='Path to the input CSV file.'
)
@click.option(
    '--output-file',
    type=click.Path(),
    default='filtered_output.csv',
    show_default=True,
    help='Path to the output CSV file.'
)
def main(input_file: str, output_file: str) -> None:
    """
    Command-line interface for filtering a DataFrame and saving the results to a CSV file.

    This script reads a CSV file, applies a filter, and saves the filtered data to a new CSV file.
    """
    filter_dataframe(input_file, output_file)


if __name__ == '__main__':
    main()

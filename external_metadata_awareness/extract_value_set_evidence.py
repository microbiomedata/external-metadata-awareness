import pprint

import click
import yaml
import pandas as pd
from typing import Optional, List, Dict
from oaklib import get_implementation_from_shorthand, get_adapter
# from oaklib.interfaces import BasicOntologyInterface
from oaklib.types import CURIE
from oaklib.datamodels.vocabulary import IS_A


# Example function to fetch labels for CURIEs
def fetch_labels_for_curies(my_adapter, curies: List[str]) -> Dict[str, Optional[str]]:
    labels = {}
    for curie in curies:
        try:
            labels[curie] = my_adapter.label(curie)
        except Exception as e:
            print(f"Error fetching label for {curie}: {e}")
            labels[curie] = None
    return labels


def add_labels_to_dataframe(df: pd.DataFrame, my_adapter) -> pd.DataFrame:
    curies = df['unique_id'].tolist()
    labels = fetch_labels_for_curies(my_adapter, curies)
    df['label'] = df['unique_id'].map(labels)
    return df


def add_biome_indicator(df: pd.DataFrame, biome_subclasses: set) -> pd.DataFrame:
    """Add a boolean column indicating if the unique_id is a biome."""
    df['is_biome'] = df['unique_id'].apply(lambda curie: curie in biome_subclasses)
    return df


def add_ontology_based_columns(df: pd.DataFrame, my_adapter,
                               class_curie_to_column_name: Dict[CURIE, str]) -> pd.DataFrame:
    """Add boolean columns indicating subclass relationships to specified ontology terms."""
    for class_curie, column_name in class_curie_to_column_name.items():
        # Retrieve subclasses using the 'is_a' relationship
        subclasses = set(my_adapter.descendants(class_curie, predicates=[IS_A]))
        # Add the boolean column to indicate subclass relationship
        df[column_name] = df['unique_id'].apply(lambda curie: curie in subclasses)
    obsolete_classes_in_envo = list(my_adapter.obsoletes())
    # print(obsolete_classes_in_envo)
    df['obsolete'] = df['unique_id'].apply(lambda curie: curie in obsolete_classes_in_envo)
    return df


@click.command()
@click.option('--config', required=True, type=click.Path(exists=True), help="Path to the YAML configuration file.")
@click.option('--output-file', required=True, type=click.Path(),
              help="Path to the output file where the final DataFrame will be saved.")
@click.option('--downsample-uncounted', is_flag=True, default=False,
              help="If true, frequencies for inputs without counts will be set to the average of non-zero values in other frequency columns. If false, they will be left as 1.")
def extract_columns(config: str, output_file: str, downsample_uncounted: bool) -> None:
    """
    Reads a YAML configuration file and extracts specified columns from tabular files.

    The YAML configuration should be structured as a list of dictionaries, each containing:
      - filename: The path to the tabular file.
      - data_column_name: The name of the data column to extract (required if header is true).
      - data_column_number: The 1-based index of the data column to extract (required if header is false).
      - count_column_name: (Optional) The name of the count column to extract (required if header is true).
      - count_column_number: (Optional) The 1-based index of the count column to extract (required if header is false).
      - header: Boolean indicating whether the file has a header row.
      - output_prefix: A prefix to use for naming the extracted columns and as the key in the resulting dictionary.

    The script determines the delimiter based on the file extension ('.csv', '.tsv', or '.txt').

    :param config: Path to the YAML configuration file.
    :param output_file: Path to the output file where the final DataFrame will be saved.
    :param downsample_uncounted: If true, frequencies for inputs without counts will be downsampled.
    """
    with open(config, 'r') as file:
        inputs = yaml.safe_load(file)

    dataframes_dict = {}
    default_count_sources = []

    for entry in inputs:
        filename: str = entry['filename']
        data_column_name: Optional[str] = entry.get('data_column_name')
        data_column_number: Optional[int] = entry.get('data_column_number')
        count_column_name: Optional[str] = entry.get('count_column_name')
        count_column_number: Optional[int] = entry.get('count_column_number')
        header: bool = entry['header']
        output_prefix: str = entry['output_prefix']

        # Determine the delimiter based on the file extension
        if filename.endswith(('.tsv', '.txt')):
            sep = '\t'
        elif filename.endswith('.csv'):
            sep = ','
        else:
            raise ValueError(
                f"Invalid file extension for file {filename}. Supported extensions are .csv, .tsv, and .txt.")

        if header:
            if data_column_name is None:
                raise ValueError(f"data_column_name is required for file {filename} when header is true.")
            if data_column_number is not None:
                raise ValueError(f"data_column_number should not be provided for file {filename} when header is true.")
            header_option = 0
        else:
            if data_column_number is None:
                raise ValueError(f"data_column_number is required for file {filename} when header is false.")
            if data_column_name is not None:
                raise ValueError(f"data_column_name should not be provided for file {filename} when header is false.")
            header_option = None

        df = pd.read_csv(filename, sep=sep, header=header_option)

        # Convert 1-based to 0-based indexing for column numbers
        if not header:
            data_column = df.columns[data_column_number - 1]
            count_column = df.columns[count_column_number - 1] if count_column_number is not None else None
        else:
            data_column = data_column_name
            count_column = count_column_name

        # Rename the columns based on the output_prefix
        columns_to_extract = [data_column]
        columns_rename = {data_column: f"{output_prefix}_id"}

        # Check if no count column is provided; set counts to 1 in that case
        if count_column is None:
            df['temp_count'] = 1
            count_column = 'temp_count'
            default_count_sources.append(f"{output_prefix}_frequency")  # Track this as a default count source
        columns_to_extract.append(count_column)
        columns_rename[count_column] = f"{output_prefix}_count"

        extracted_data = df[columns_to_extract].rename(columns=columns_rename)

        # Remove rows with any NaN values
        extracted_data = extracted_data.dropna()

        # Handle duplicated IDs by summing counts
        if f"{output_prefix}_count" in extracted_data.columns:
            extracted_data = extracted_data.groupby(f"{output_prefix}_id", as_index=False).sum()

        # Add the cleaned DataFrame to the dictionary
        dataframes_dict[output_prefix] = extracted_data

    # Create a set of all unique IDs across all DataFrames
    all_ids = set()
    for df in dataframes_dict.values():
        all_ids.update(df.iloc[:, 0])

    # Convert the set of unique IDs into a single-column DataFrame
    final_df = pd.DataFrame(sorted(all_ids), columns=['unique_id'])

    # Merge each dataframe into the final_df based on the ID
    for key, df in dataframes_dict.items():
        final_df = pd.merge(final_df, df, left_on='unique_id', right_on=f"{key}_id", how='outer')
        final_df.drop(columns=[f"{key}_id"], inplace=True)

    # Convert all NaNs to 0
    final_df.fillna(0, inplace=True)

    # Normalize counts and create frequency columns
    for key in dataframes_dict.keys():
        count_column = f"{key}_count"
        freq_column = f"{key}_frequency"
        if count_column in final_df.columns:
            final_df[freq_column] = final_df[count_column] / final_df[count_column].max()

    frequency_columns = [col for col in final_df.columns if
                         col.endswith('_frequency') and col not in default_count_sources]

    if downsample_uncounted:
        # Calculate the average of non-zero values in all frequency columns from explicit count sources

        avg_non_zero_frequency = final_df[frequency_columns].replace(0, pd.NA).mean(axis=1, skipna=True).fillna(0)
        avg_non_zero_frequency_mean = avg_non_zero_frequency.mean()
        print(f"\nAverage of non-zero frequencies in explicit count sources: {avg_non_zero_frequency_mean}")

        # Assign this average to the frequency columns where no count column was provided
        for freq_column in default_count_sources:
            print(f"Assigning average non-zero frequency to {freq_column} where count is 1")
            final_df[freq_column] = final_df.apply(
                lambda row: avg_non_zero_frequency_mean if row[freq_column.replace('_frequency',
                                                                                   '_count')] == 1 else 0,
                axis=1
            )

    # Create an 'all_evidence' column as the sum of all frequency columns
    final_df['all_evidence'] = final_df[frequency_columns + default_count_sources].sum(axis=1)

    # Re-normalize the 'all_evidence' column
    final_df['all_evidence'] = final_df['all_evidence'] / final_df['all_evidence'].max()

    my_adapter = get_adapter("sqlite:obo:envo")

    # Add labels to the final DataFrame
    final_df_with_labels = add_labels_to_dataframe(final_df, my_adapter)

    # Define the CURIEs and corresponding column names to add
    class_curie_to_column_name = {
        'BFO:0000015': 'is_process',  # Process
        'BFO:0000019': 'is_quality',  # Quality
        'CHEBI:24431': 'is_chemical_entity',  # Chemical entity
        'ENVO:00000428': 'is_biome',  # Biome
        'ENVO:00002030': 'is_aquatic_biome',  # Biome
        'ENVO:00000446': 'is_terrestrial_biome',  # Biome
        'ENVO:00010483': 'is_environmental_material',  # Environmental material
        'ENVO:00001998': 'is_soil',
        'ENVO:00003082': 'is_enriched_soil',
    }

    # Add boolean columns based on ontology subclass relationships
    final_df_with_labels = add_ontology_based_columns(final_df_with_labels, my_adapter, class_curie_to_column_name)

    # Reorder columns
    columns = list(final_df_with_labels.columns)
    columns.insert(1, columns.pop(columns.index('label')))
    columns.insert(2, columns.pop(columns.index('all_evidence')))

    columns.insert(3, columns.pop(columns.index('is_process')))
    columns.insert(4, columns.pop(columns.index('is_quality')))
    columns.insert(5, columns.pop(columns.index('is_chemical_entity')))
    columns.insert(6, columns.pop(columns.index('is_biome')))
    columns.insert(7, columns.pop(columns.index('is_aquatic_biome')))
    columns.insert(8, columns.pop(columns.index('is_terrestrial_biome')))
    columns.insert(9, columns.pop(columns.index('is_environmental_material')))
    columns.insert(10, columns.pop(columns.index('is_soil')))
    columns.insert(11, columns.pop(columns.index('is_enriched_soil')))
    columns.insert(12, columns.pop(columns.index('obsolete')))
    final_df_with_labels = final_df_with_labels[columns]

    # Save the final DataFrame to the specified output file
    final_df_with_labels.to_csv(output_file, index=False, sep='\t' if output_file.endswith('.tsv') else ',')

    print(f"\nFinal DataFrame saved to {output_file}")


if __name__ == "__main__":
    extract_columns()

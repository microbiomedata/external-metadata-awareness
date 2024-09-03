import json

import pandas as pd
import click
from oaklib import get_adapter
from oaklib.datamodels.vocabulary import IS_A

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from scipy.sparse import hstack

import numpy as np

# Initialize cache dictionaries
ancestor_cache = {}
descendant_cache = {}


def generate_percentage_heterogeneity_report(df, study_column='part_of',
                                             prediction_column='predicted_normalized_env_package',
                                             study_metadata=None):
    """
    Generates a report where each row corresponds to a study and each column corresponds to a possible
    predicted_normalized_env_package value. The value in each cell is the percentage of rows with that study
    in part_of that have that predicted_normalized_env_package value. Includes study metadata.

    Args:
        df (pd.DataFrame): The input DataFrame containing study data.
        study_column (str): The column name that identifies different studies.
        prediction_column (str): The column name that contains the predicted normalized_env_package values.
        study_metadata (dict): Dictionary with study metadata.

    Returns:
        pd.DataFrame: A DataFrame where rows are studies and columns are predicted_normalized_env_package values,
                      including a metadata column.
    """
    # Create a cross-tabulation of the study and the predicted normalized_env_package
    crosstab = pd.crosstab(df[study_column], df[prediction_column], normalize='index') * 100

    # Rename 'part_of' to 'study'
    crosstab.rename_axis('study', axis='index', inplace=True)

    # Add study metadata
    if study_metadata:
        # Create the 'study_metadata' column based on the index and study metadata
        study_metadata_col = crosstab.index.map(lambda x:
                                                f"{study_metadata.get(x, {}).get('title', 'Unknown')} ; {study_metadata.get(x, {}).get('name', 'Unknown')}"
                                                )
        # Sort columns for consistent ordering
        crosstab = crosstab.sort_index(axis=1)

        # Insert 'study_metadata' as the first column (after the index)
        crosstab.insert(0, 'study_title_name', study_metadata_col)
    return crosstab


def vectorize_terms(df, column):
    """
    Vectorize the ancestor or descendant terms for a given column.

    Args:
        df (pd.DataFrame): The input dataframe.
        column (str): The column name to vectorize.

    Returns:
        sparse matrix: The vectorized term matrix.
    """
    vectorizer = CountVectorizer()
    return vectorizer.fit_transform(
        df[column].apply(lambda x: ' '.join([str(term) for term in x if term is not None]) if x is not None else '')
    )


def get_hierarchy_terms(curie: str, adapter) -> dict:
    """
    Extract ancestor and descendant terms from the ontology for a given CURIE,
    using caching to improve performance and filtering by 'is_a' relationships.

    Args:
        curie (str): CURIE identifier for the ontology term.
        adapter: Ontology adapter.

    Returns:
        dict: Dictionary containing lists of ancestor and descendant terms.
    """
    if curie in ancestor_cache:
        ancestors = ancestor_cache[curie]
    else:
        try:
            ancestors = list(adapter.ancestors(curie, predicates=[IS_A]))
            ancestor_cache[curie] = [adapter.label(ancestor) for ancestor in ancestors if ancestor]
        except Exception as e:
            print(f"Error retrieving ancestors for {curie}: {e}")
            ancestor_cache[curie] = []

    if curie in descendant_cache:
        descendants = descendant_cache[curie]
    else:
        try:
            descendants = list(adapter.descendants(curie, predicates=[IS_A]))
            descendant_cache[curie] = [adapter.label(descendant) for descendant in descendants if descendant]
        except Exception as e:
            print(f"Error retrieving descendants for {curie}: {e}")
            descendant_cache[curie] = []

    return {
        'ancestors': ancestor_cache[curie],
        'descendants': descendant_cache[curie],
    }


@click.command()
@click.option('--input-file', required=True, type=click.Path(exists=True), help="Path to the input TSV file.")
@click.option('--output-file', required=True, type=click.Path(), help="Path to save the output TSV file.")
@click.option('--heterogeneity-file', required=True, type=click.Path(),
              help="Path to save a report of heterogeneity of env_package use by studies.")
@click.option('--oak-adapter-string', default="sqlite:obo:envo", show_default=True,
              help="OAK adapter string (default is 'sqlite:obo:envo').")
@click.option('--override-file', type=click.Path(exists=True), help="Optional path to an override TSV file.")
@click.option('--override-biosample-column', type=str, help="Column with Biosample ids.")
@click.option('--override-env-package-column', type=str, help="Column with curated env_package values.")
@click.option('--studies-json', type=click.Path(exists=True), help="Path to a JSON file with study metadata.")
def predict_env_package(input_file: str, output_file: str, oak_adapter_string: str,
                        heterogeneity_file: str, override_file: str = None, override_biosample_column: str = None,
                        override_env_package_column: str = None, studies_json: str = None) -> None:
    """
    Merge authoritative labels into a TSV file based on ontology CURIE identifiers.

    This script reads a TSV file with CURIE identifiers, retrieves the authoritative
    labels from the specified ontology, and saves the result to a new TSV file.

    Args:
        input_file (str): Path to the input TSV file.
        output_file (str): Path to save the output TSV file.
        heterogeneity_file (str): Path to save a report of heterogeneity of env_package use by studies.
        oak_adapter_string (str): OAK adapter string for accessing the ontology.
        override_file (str): Optional path to an override TSV file.
        override_biosample_column (str): Column with Biosample ids.
        override_env_package_column (str): Column with curated env_package values.
        studies_json (str): Path to a JSON file with study metadata.
    """
    # Load the TSV file into a DataFrame
    df = pd.read_csv(input_file, sep='\t')

    # Add 'normalized_env_package' column
    df['normalized_env_package'] = df['env_package_has_raw_value'].apply(
        lambda x: 'soil' if x == 'ENVO:00001998' else x
    )  # todo shouldn't be hard coded

    df['curated_env_package'] = df['normalized_env_package']

    if override_file and override_biosample_column and override_env_package_column:
        # Load the override TSV file into a DataFrame
        df_override = pd.read_csv(override_file, sep='\t')
        df_override = df_override[[override_biosample_column, override_env_package_column]]
        df_override.columns = ['override_biosample_id', 'override_env_package']

        # Merge the 'df' DataFrame with 'df_override' on the matching 'id' and 'override_biosample_id'
        df = pd.merge(df, df_override, how='left', left_on='id', right_on='override_biosample_id')

        # Replace values in 'env_package_with_curation' where 'override_env_package' is not null
        df['curated_env_package'] = df['override_env_package'].combine_first(df['curated_env_package'])

        # Drop the columns from the merge that are no longer needed
        df.drop(columns=['override_biosample_id', 'override_env_package'], inplace=True)

    df.to_csv(output_file, sep='\t', index=False)

    # print a value count for the curated_env_package column
    print("Value counts for curated_env_package column:")
    print(df['curated_env_package'].value_counts(dropna=False))

    # Initialize the ontology adapter
    adapter = get_adapter(oak_adapter_string)

    # Apply the function to the relevant columns
    for column in ['env_broad_scale_id', 'env_local_scale_id', 'env_medium_id']:
        df[f'{column}_ancestors'] = df[column].apply(lambda x: get_hierarchy_terms(x, adapter)['ancestors'])
        df[f'{column}_descendants'] = df[column].apply(lambda x: get_hierarchy_terms(x, adapter)['descendants'])

    # Vectorize each set of terms separately
    broad_scale_ancestors = vectorize_terms(df, 'env_broad_scale_id_ancestors')
    broad_scale_descendants = vectorize_terms(df, 'env_broad_scale_id_descendants')

    local_scale_ancestors = vectorize_terms(df, 'env_local_scale_id_ancestors')
    local_scale_descendants = vectorize_terms(df, 'env_local_scale_id_descendants')

    medium_ancestors = vectorize_terms(df, 'env_medium_id_ancestors')
    medium_descendants = vectorize_terms(df, 'env_medium_id_descendants')

    # Combine all feature matrices
    X = hstack([
        broad_scale_ancestors,
        broad_scale_descendants,
        local_scale_ancestors,
        local_scale_descendants,
        medium_ancestors,
        medium_descendants
    ])

    # Filter the DataFrame to only include non-null rows for the target column
    df_filtered = df[df['curated_env_package'].notnull()]

    # Extract the target variable
    y = df_filtered['curated_env_package']

    # Ensure X corresponds to the filtered rows
    X_filtered = X[df_filtered.index]

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X_filtered, y, test_size=0.3, random_state=42)

    # Train a Random Forest Classifier
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)

    # Make predictions on the test set
    y_pred = clf.predict(X_test)

    # Evaluate the model
    print(classification_report(y_test, y_pred))

    # Predict the curated_env_package for all rows
    df['predicted_curated_env_package'] = clf.predict(X)

    # If you want to add confidence scores for each class
    class_probabilities = clf.predict_proba(X)

    # Get the class labels from the model
    class_labels = clf.classes_

    # Add a column for each class with the corresponding confidence score
    for i, class_label in enumerate(class_labels):
        df[f'confidence_{class_label}'] = class_probabilities[:, i]

    # Save the updated DataFrame back to a new TSV file
    df.to_csv(output_file, sep='\t', index=False)

    # Load the study metadata from the JSON file
    if studies_json:
        with open(studies_json, 'r') as f:
            study_metadata = json.load(f)

        # Create a dictionary for quick lookup
        study_metadata_dict = {study['id']: study for study in study_metadata}
    else:
        study_metadata_dict = None

    # Generate the heterogeneity report with the study metadata included
    heterogeneity_report = generate_percentage_heterogeneity_report(
        df, study_column='part_of',
        prediction_column='predicted_curated_env_package',
        study_metadata=study_metadata_dict
    )

    heterogeneity_report.to_csv(heterogeneity_file, sep='\t')


if __name__ == '__main__':
    predict_env_package()

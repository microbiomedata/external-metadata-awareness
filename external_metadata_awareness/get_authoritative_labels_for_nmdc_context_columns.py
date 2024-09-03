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
                                             prediction_column='predicted_normalized_env_package'):
    """
    Generates a report where each row corresponds to a study and each column corresponds to a possible
    predicted_normalized_env_package value. The value in each cell is the percentage of rows with that study
    in part_of that have that predicted_normalized_env_package value.

    Args:
        df (pd.DataFrame): The input DataFrame containing study data.
        study_column (str): The column name that identifies different studies.
        prediction_column (str): The column name that contains the predicted normalized_env_package values.

    Returns:
        pd.DataFrame: A DataFrame where rows are studies and columns are predicted_normalized_env_package values.
    """
    # Create a cross-tabulation of the study and the predicted normalized_env_package
    crosstab = pd.crosstab(df[study_column], df[prediction_column], normalize='index') * 100

    # Sort columns for consistent ordering
    crosstab = crosstab.sort_index(axis=1)

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


def get_ontology_label(curie: str, adapter) -> str:
    """
    Retrieve the authoritative label for a given CURIE from the ontology.

    Args:
        curie (str): The CURIE identifier for the ontology term.
        adapter: The ontology adapter used to fetch the term label.

    Returns:
        str: The authoritative label for the given CURIE, or None if not found.
    """
    try:
        return adapter.label(curie)
    except Exception as e:
        print(f"Error retrieving label for {curie}: {e}")
        return None


@click.command()
@click.option('--input-file', required=True, type=click.Path(exists=True), help="Path to the input TSV file.")
@click.option('--output-file', required=True, type=click.Path(), help="Path to save the output TSV file.")
@click.option('--oak-adapter-string', default="sqlite:obo:envo", show_default=True,
              help="OAK adapter string (default is 'sqlite:obo:envo').")
def merge_authoritative_labels(input_file: str, output_file: str, oak_adapter_string: str) -> None:
    """
    Merge authoritative labels into a TSV file based on ontology CURIE identifiers.

    This script reads a TSV file with CURIE identifiers, retrieves the authoritative
    labels from the specified ontology, and saves the result to a new TSV file.

    Args:
        input_file (str): Path to the input TSV file.
        output_file (str): Path to save the output TSV file.
        oak_adapter_string (str): OAK adapter string for accessing the ontology.
    """
    # Load the TSV file into a DataFrame
    df = pd.read_csv(input_file, sep='\t')

    # Add 'normalized_env_package' column
    df['normalized_env_package'] = df['env_package_has_raw_value'].apply(
        lambda x: 'soil' if x == 'ENVO:00001998' else x
    )  # todo shouldn't be hard coded

    # Initialize the ontology adapter
    adapter = get_adapter(oak_adapter_string)

    # Apply the function to the relevant columns
    df['env_broad_scale_authoritative_label'] = df['env_broad_scale_id'].apply(lambda x: get_ontology_label(x, adapter))
    df['env_local_scale_authoritative_label'] = df['env_local_scale_id'].apply(lambda x: get_ontology_label(x, adapter))
    df['env_medium_authoritative_label'] = df['env_medium_id'].apply(lambda x: get_ontology_label(x, adapter))

    # Apply the function to the relevant columns
    for column in ['env_broad_scale_id', 'env_local_scale_id', 'env_medium_id']:
        df[f'{column}_ancestors'] = df[column].apply(lambda x: get_hierarchy_terms(x, adapter)['ancestors'])
        df[f'{column}_descendants'] = df[column].apply(lambda x: get_hierarchy_terms(x, adapter)['descendants'])

    # # Save the updated DataFrame back to a new TSV file
    # df.to_csv(output_file, sep='\t', index=False)

    print(f"Authoritative labels merged and saved to {output_file}")

    # Print out the unique value counts for 'env_package_has_raw_value'
    unique_values_counts = df['normalized_env_package'].value_counts(dropna=False)
    print("\nUnique value counts for 'normalized_env_package':")
    print(unique_values_counts)

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

    # print(type(X)) # <class 'scipy.sparse._csr.csr_matrix'

    # np.savetxt("vectorized_matrix.txt", X.toarray(), fmt="%d")

    # Assuming your DataFrame is already loaded into df and X is your feature matrix

    # Filter the DataFrame to only include non-null rows for the target column
    df_filtered = df[df['normalized_env_package'].notnull()]

    # Extract the target variable
    y = df_filtered['normalized_env_package']

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

    # # Optionally, save the trained model for later use
    # import joblib
    # joblib.dump(clf, 'random_forest_model.pkl')

    # Assuming clf is your trained RandomForestClassifier and df is your DataFrame

    # Predict the normalized_env_package for all rows
    df['predicted_normalized_env_package'] = clf.predict(X)

    # If you want to add confidence scores for each class
    class_probabilities = clf.predict_proba(X)

    # Get the class labels from the model
    class_labels = clf.classes_

    # Add a column for each class with the corresponding confidence score
    for i, class_label in enumerate(class_labels):
        df[f'confidence_{class_label}'] = class_probabilities[:, i]

    # Exclude the feature columns from the final output
    # Assuming the feature columns were derived from specific columns like 'env_broad_scale_id', 'env_local_scale_id', etc.
    columns_to_exclude = ['env_broad_scale_id_ancestors', 'env_broad_scale_id_descendants',
                          'env_local_scale_id_ancestors', 'env_local_scale_id_descendants',
                          'env_medium_id_ancestors', 'env_medium_id_descendants']
    df_final = df.drop(columns=columns_to_exclude)

    # # Optionally, save the updated DataFrame to a new TSV file
    # df_final.to_csv('updated_dataframe_with_predictions.tsv', sep='\t', index=False)

    # Save the updated DataFrame back to a new TSV file
    df_final.to_csv(output_file, sep='\t', index=False)

    print("Predicted normalized_env_package and confidence scores added to the DataFrame, excluding feature columns.")

    # # Assuming df_final is your final DataFrame after predictions
    # heterogeneity_report = generate_heterogeneity_report(df_final, study_column='part_of',
    #                                                      prediction_column='predicted_normalized_env_package')
    #
    # # Optionally, save the report to a CSV file
    # heterogeneity_report.to_csv('heterogeneity_report.csv', index=False)
    #
    # # Print the report to the console
    # if heterogeneity_report.empty:
    #     print("All studies are homogeneous for predicted_normalized_env_package.")
    # else:
    #     print("Heterogeneous studies found:")
    #     print(heterogeneity_report)

    # Assuming df_final is your final DataFrame after predictions
    heterogeneity_report = generate_percentage_heterogeneity_report(df_final, study_column='part_of',
                                                                    prediction_column='predicted_normalized_env_package')

    # Optionally, save the report to a CSV file
    heterogeneity_report.to_csv('heterogeneity_percentage_report.csv')

    # Print the report to the console
    print("Heterogeneity report with percentage of predictions by study:")
    print(heterogeneity_report)


if __name__ == '__main__':
    merge_authoritative_labels()

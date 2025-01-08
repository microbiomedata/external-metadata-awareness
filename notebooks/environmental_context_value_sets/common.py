import pandas as pd
from linkml_runtime import SchemaView
import requests

from typing import Dict, Any
import csv

from sklearn.feature_extraction.text import CountVectorizer  # from scikit-learn

import re


# todo is filling memory with things like this a good idea? for understandability? or performance?
# todo they should be aggregated somewhere, as specified by the config.yaml
# todo or should we going straight to data frames? in which case a dlist of dicts might be preferable
def get_curie_descendants_label_dict(my_curie, predicates, adapter):
    curie_label_dict = {}
    for descendant in adapter.descendants(my_curie, predicates=predicates):
        curie_label_dict[descendant] = adapter.label(descendant)
    return curie_label_dict


def curie_descendants_label_dict_to_lod(curie_label_dict):
    return [{'curie': k, 'label': v} for k, v in curie_label_dict.items()]


def curie_descendants_label_lod_to_df(curie_label_lod):
    return pd.DataFrame(curie_label_lod)


def get_schemaview_from_source(source):
    return SchemaView(source)


def parse_hierarchically_underscored_strings(hierarchically_underscored_string_list):
    result = []
    for item in hierarchically_underscored_string_list:
        # Remove leading underscores for label, split on '[' to separate curie
        label, my_curie = item.lstrip('_').split(' [')
        # Remove the trailing ']' from curie
        my_curie = my_curie.rstrip(']')
        # Append dictionary with label and curie
        result.append({'label': label.strip(), 'curie': my_curie.strip()})
    return result


def dedupe_underscoreless_pvs(underscoreless_pvs):
    # Dictionary to store CURIE as key and list of unique labels as values
    curie_to_labels = {}

    for item in underscoreless_pvs:
        my_curie = item['curie']
        label = item['label']

        # Initialize the list if curie is not yet a key
        if my_curie not in curie_to_labels:
            curie_to_labels[my_curie] = []

        # Add label if it is not already in the list for this curie
        if label not in curie_to_labels[my_curie]:
            curie_to_labels[my_curie].append(label)
    return curie_to_labels


def validate_curie_label_list_dict(curie_label_dict, adapter, print_flag=False):
    problem_curies = []
    valid_curies = []
    for my_curie, labels in curie_label_dict.items():
        true_label = adapter.label(my_curie)
        if true_label not in labels:
            problem_curies.append(my_curie)
            if print_flag:
                print(f"Error: {my_curie} has true label {true_label} which doesn't appear in {labels}")
        else:
            valid_curies.append({"curie": my_curie, "label": true_label})
    return {"problems": problem_curies, "valids": valid_curies}


# todo could pre-determine the collection sizes
# todo could report elapsed time

def get_docs_from_nmdc_collection(base_url, collection_name, max_page_size=1000, stop_after=None):
    """
    Fetch all documents from a paginated API. Defaults to fetching a large number of documents per page.
    Optionally stop after a specified number of documents.

    Parameters:
    - base_url: The base URL of the API endpoint (e.g., 'https://api.microbiomedata.org/nmdcschema/').
    - collection_name: The name of the collection to fetch (e.g., 'biosample_set').
    - max_page_size: The maximum number of items to retrieve per page (default 1000).
    - stop_after: Optional parameter to stop fetching after a certain number of documents (default None).

    Returns:
    - A list of documents fetched from the API.
    """
    documents = []
    page_token = None
    total_documents = 0
    page_count = 0

    # Construct the full URL with the collection name
    url = f"{base_url}{collection_name}"

    while True:
        page_count += 1
        # Prepare the query parameters
        params = {
            'collection_name': collection_name,
            'max_page_size': max_page_size,  # Set large max_page_size to reduce pagination
        }

        if page_token:
            params['page_token'] = page_token  # Add the page token for pagination

        # Send the request to the API
        response = requests.get(url, params=params)

        if response.status_code != 200:
            print(f"Error fetching data: {response.status_code}")
            break

        data = response.json()

        # Add the current page of documents to the list
        num_documents_on_page = len(data['resources'])
        documents.extend(data['resources'])
        total_documents += num_documents_on_page

        # Status reporting
        print(f"Fetched page {page_count} with {num_documents_on_page} documents. Total fetched: {total_documents}")

        # If stop_after is provided, stop fetching after reaching the specified number of documents
        if stop_after and total_documents >= stop_after:
            documents = documents[:stop_after]  # Trim to the required number
            print(f"Reached stop_after limit of {stop_after} documents.")
            break

        # Check if there is a next page
        page_token = data.get('next_page_token')
        if not page_token:
            print("All documents fetched.")
            break  # Exit the loop if no more pages are available

    return documents


def get_name_or_rawval(env_scale: Dict[str, Any]) -> str:
    """Safely extract label from environmental scale data."""
    if env_scale:
        term = env_scale.get('term')
        if term:
            return term.get('name', term.get('has_raw_value', ''))
    return ''


def tsv_to_dict_of_dicts(tsv_file, outer_key_column):
    """
    Reads a TSV file into a dictionary of dictionaries.

    :param tsv_file: Path to the TSV file.
    :param outer_key_column: The column name or index to be used as the key for the outer dictionary.
    :return: A dictionary of dictionaries, with outer keys being the values from the specified column.
    """
    with open(tsv_file, newline='', encoding='utf-8') as my_f:
        reader = csv.DictReader(my_f, delimiter='\t')

        result = {}

        for my_row in reader:
            outer_key = my_row[outer_key_column]
            result[outer_key] = {key: value for key, value in my_row.items() if key != outer_key_column}

    return result


# todo only gets authoritative labels from the passed adapter, which is presumably EnvO only
# todo would benefit from caching of labels

def biosamples_lod_context_extractor(biosamples_lod, adapter, my_env_pacakge_overrides=None):
    new_lod = []
    for biosample in biosamples_lod:
        insdc_identifiers = biosample.get('insdc_biosample_identifiers', [])

        env_broad_scale_label = get_name_or_rawval(biosample.get('env_broad_scale'))
        env_local_scale_label = get_name_or_rawval(biosample.get('env_local_scale'))
        env_medium_label = get_name_or_rawval(biosample.get('env_medium'))

        # Extracting optional scalar env_package.has_raw_value
        env_package_has_raw_value = biosample.get('env_package', {}).get('has_raw_value', '')

        # Extracting required multivalued part_of
        associated_studies = '|'.join(biosample.get('associated_studies', []))  # Assuming part_of is a list of strings

        my_row: Dict[str, str] = {
            'id': biosample['id'],
            'insdc_biosample_identifiers': '|'.join(insdc_identifiers) if insdc_identifiers else '',

            'env_broad_scale_id': biosample['env_broad_scale']['term']['id'],
            'env_broad_scale_mongo_label': env_broad_scale_label,
            'env_broad_scale_auth_label': adapter.label(biosample['env_broad_scale']['term']['id']),

            'env_local_scale_id': biosample['env_local_scale']['term']['id'],
            'env_local_scale_mongo_label': env_local_scale_label,
            'env_local_scale_auth_label': adapter.label(biosample['env_local_scale']['term']['id']),

            'env_medium_id': biosample['env_medium']['term']['id'],
            'env_medium_mongo_label': env_medium_label,
            'env_medium_auth_label': adapter.label(biosample['env_medium']['term']['id']),

            'env_package_has_raw_value': env_package_has_raw_value,
            'normalized_env_package': 'soil' if env_package_has_raw_value == 'ENVO:00001998' else env_package_has_raw_value.lower(),
            # todo abstract this though label search, or at least providing a lookup structure

            'associated_studies': associated_studies
        }

        if my_env_pacakge_overrides and biosample['id'] in my_env_pacakge_overrides:
            # print(
            #     f"Overriding env_package for biosample {biosample['id']} from {my_row['normalized_env_package']} to {my_env_pacakge_overrides[biosample['id']]['mam_inferred_env_package']}")
            my_row['normalized_env_package'] = my_env_pacakge_overrides[biosample['id']]['mam_inferred_env_package']

        new_lod.append(my_row)
    return new_lod


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


def parse_curie_label(text, my_approved_prefixes=['ENVO', 'PO']):
    # Case-insensitive pattern for matching approved prefixes followed by an ID
    pattern = r'\b(?:' + '|'.join(my_approved_prefixes) + r')\s*[:_]\s*(\d+)\b'
    curie_match = re.search(pattern, text, re.IGNORECASE)

    if curie_match:
        my_curie = f"{my_approved_prefixes[0].upper()}:{curie_match.group(1)}"  # standardize prefix to 'ENVO:ID'
        label = re.sub(pattern, "", text).strip("[]() ")
        # replace any colons in the label with a whitespace
        return pd.Series([label, my_curie])
    else:
        label = re.sub(r':', ' ', text)
        return pd.Series([label, None])  # No CURIE found, return original label and None for CURIE


def get_longest_annotation_curie(text, adapter, min_annotation_len):
    annotations = adapter.annotate_text(text)
    if not annotations:  # Check if annotations list is empty
        return None
    try:
        longest_annotation = max(annotations, key=lambda x: x.subject_end - x.subject_start)

        if longest_annotation.subject_end - longest_annotation.subject_start < min_annotation_len:
            return None
        return longest_annotation.object_id
    except ValueError:
        return None  # Return None if there's an unexpected issue with finding the max


# Create a new DataFrame summarizing each stretch_id with the most common longest_annotation_curie
def summarize_stretch_groups(df):
    summary_rows = []

    # Iterate through each group of rows by stretch_id
    for stretch_id, group in df.dropna(subset=['stretch_id']).groupby('stretch_id'):
        # Calculate the most common longest_annotation_curie and its fraction
        most_common_curie = group['longest_annotation_curie'].value_counts().idxmax()
        fraction = group['longest_annotation_curie'].value_counts(normalize=True).max()

        # Append the summary row
        summary_rows.append({
            'stretch_id': stretch_id,
            'most_common_longest_annotation_curie': most_common_curie,
            'fraction': fraction
        })

    # Convert the summary rows into a new DataFrame
    return pd.DataFrame(summary_rows)


def find_consecutive_stretches_dict(series):
    """
    Detect consecutive stretches of integer values in a pandas Series.
    Returns a dictionary where the keys are serial numbers (starting at 0),
    and the values are lists of consecutive integers.
    """
    # Ensure the series is clean: drop NaN, duplicates, and non-integer values
    series = series.dropna().drop_duplicates()
    series = series[series.apply(lambda x: isinstance(x, (int, float)) and (x == int(x)))].astype(int)
    series = series.sort_values()

    my_stretches_dict = {}
    current_stretch = []
    stretch_index = 1

    for i in range(len(series)):
        if i == 0 or series.iloc[i] - series.iloc[i - 1] == 1:
            current_stretch.append(series.iloc[i])
        else:
            if len(current_stretch) >= 3:
                my_stretches_dict[stretch_index] = current_stretch
                stretch_index += 1
            current_stretch = [series.iloc[i]]

    if len(current_stretch) >= 3:
        my_stretches_dict[stretch_index] = current_stretch

    return my_stretches_dict


# Function to convert stretches dict to long-format DataFrame
def stretches_dict_to_long_dataframe(my_stretches_dict):
    """
    Convert a dictionary of consecutive stretches into a long-format DataFrame.
    Each row corresponds to an individual integer value in a stretch, with:
    - 'stretch_id': The key from the dictionary.
    - 'value': The integer value within the stretch.
    """
    rows = []
    for stretch_id, stretch_values in my_stretches_dict.items():
        for value in stretch_values:
            rows.append({'stretch_id': stretch_id, 'value': int(value)})  # Ensure integers only
    return pd.DataFrame(rows)

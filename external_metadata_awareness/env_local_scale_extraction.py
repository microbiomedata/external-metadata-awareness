from typing import List

import yaml
import click
from oaklib import get_adapter
from oaklib.query import onto_query, FunctionQuery, FunctionEnum, SimpleQueryTerm


def load_configs(oak_config_file, extraction_config_file):
    with open(oak_config_file, 'r') as file:
        oak_config = yaml.safe_load(file)
    with open(extraction_config_file, 'r') as file:
        extraction_config = yaml.safe_load(file)
    return oak_config, extraction_config


def create_exclusion_list(term_labels, adapter) -> List[str]:
    """
    Creates a combined FunctionQuery to exclude specific terms and their descendants.

    :param term_labels: List of term labels to exclude.
    :param adapter: The ontology adapter.
    :return: Combined FunctionQuery to exclude all specified terms and their descendants.
    """
    all_ids_to_exclude = []
    for label in term_labels:
        # Find the CURIE for the label
        term_curies = onto_query(SimpleQueryTerm(term=label), adapter)
        if term_curies:
            term_curie = term_curies[0]  # Assuming one CURIE per label
            # Create a descendant exclusion query for the term
            list_to_exclude = onto_query([".desc//p=i", term_curie], adapter)
            all_ids_to_exclude.extend(list_to_exclude)
    return list(set(all_ids_to_exclude))


def create_text_exclusion_query(text_exclusions, adapter):
    """
    Creates a combined FunctionQuery to exclude specific terms based on text matching.

    :param text_exclusions: List of text patterns to exclude.
    :param adapter: The ontology adapter.
    :return: Combined FunctionQuery to exclude all specified text matches.
    """

    all_ids_to_exclude = []

    for text in text_exclusions:
        # Find the CURIE for the label
        list_to_exclude = onto_query(["l~"+text], adapter)
        all_ids_to_exclude.extend(list_to_exclude)
    return list(set(all_ids_to_exclude))


def exclude_terms(full_list, exclusion_list):
    """
    Returns a list of items from the full list with the items in the exclusion list removed.

    :param full_list: List of items to be filtered.
    :param exclusion_list: List of items to exclude from the full list.
    :return: A list with items from exclusion_list removed.
    """
    return [item for item in full_list if item not in exclusion_list]


def process_ontology(oak_config_file, extraction_config):
    # Load the ontology using the get_adapter function
    oak_adapter = get_adapter(oak_config_file)

    # Get the entity and exclusions from the config
    initial_term_label = extraction_config['entity']
    initial_term_list = onto_query([".desc//p=i", initial_term_label], oak_adapter)
    print("length of initial term list", len(initial_term_list))

    exclusion_terms = extraction_config.get('term_exclusions', [])
    exclusion_texts = extraction_config.get('text_exclusions', [])

    exclusion_terms_and_children = create_exclusion_list(exclusion_terms, oak_adapter)
    exclusion_terms_from_text = create_text_exclusion_query(exclusion_texts, oak_adapter)
    exclusion_list = exclusion_terms_and_children + exclusion_terms_from_text
    print("length of excluded terms", len(exclusion_terms_and_children))
    print("length of excluded terms from text", len(exclusion_terms_from_text))

    remaining_items = exclude_terms(initial_term_list, exclusion_list)
    print(len(remaining_items))


@click.command()
@click.option('--extraction-config-file', required=True, help='Path to the extraction YAML configuration file.')
@click.option('--oak-config-file', required=True, help='Path to the extraction YAML configuration file.')
def cli(extraction_config_file, oak_config_file):
    """
    CLI tool to process an ontology based on the provided YAML configuration file.
    """
    _, extraction_config = load_configs(oak_config_file, extraction_config_file)
    process_ontology(oak_config_file, extraction_config)


if __name__ == "__main__":
    cli()
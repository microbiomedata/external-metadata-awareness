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


def create_text_exclusion_list(text_exclusions, adapter):
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


def create_exclude_solo_terms(exlusion_terms: List[str], adapter) -> List[str]:
    """
    Creates a list of CURIEs to exclude based on the provided list of terms.

    :param exlusion_terms: List of term labels to exclude.
    :param envo: The ontology adapter.

    """

    all_ids_to_exclude = []

    for term_label in exlusion_terms:
        # Find the CURIE for the label
        list_to_exclude = onto_query([term_label], adapter)
        all_ids_to_exclude.extend(list_to_exclude)
    return list(set(all_ids_to_exclude))
    pass


def extract_terms_to_file(oak_config_file, extraction_config):
    # Load the ontology using the get_adapter function
    envo = get_adapter(oak_config_file)

    # Get the entity and exclusions from the config
    initial_term_label = extraction_config['entity']
    initial_term_list = onto_query([".desc//p=i", initial_term_label], envo)
    print("length of initial term list", len(initial_term_list))

    exclusion_terms_and_children = create_exclusion_list(extraction_config.get('term_and_descendant_exclusions', []),
                                                         envo)

    exclusion_terms_from_text = create_text_exclusion_list(extraction_config.get('text_exclusions', []),
                                                           envo)
    excluded_terms = create_exclude_solo_terms(extraction_config.get('term_exclusions', []), envo)

    exclusion_list = exclusion_terms_and_children + exclusion_terms_from_text + excluded_terms
    print("length of excluded terms", len(exclusion_terms_and_children))
    print("length of excluded terms from text", len(exclusion_terms_from_text))
    print("length of excluded terms from solo terms", len(excluded_terms))

    remaining_items = exclude_terms(initial_term_list, exclusion_list)
    print("length of remaining items", len(remaining_items))

    results = onto_query(remaining_items, envo, labels=True)

    # Write the results to the output file specified in the extraction config
    output_file_path = extraction_config['output']
    with open(output_file_path, 'w') as output_file:
        for curie, label in results:
            output_file.write(f"{curie}: {label}\n")

    print(f"Results written to {output_file_path}")


@click.command()
@click.option('--extraction-config-file', required=True, help='Path to the extraction YAML configuration file.')
@click.option('--oak-config-file', required=True, help='Path to the extraction YAML configuration file.')
def cli(extraction_config_file, oak_config_file):
    """
    CLI tool to process an ontology based on the provided YAML configuration file.
    """
    _, extraction_config = load_configs(oak_config_file, extraction_config_file)
    extract_terms_to_file(oak_config_file, extraction_config)


if __name__ == "__main__":
    cli()

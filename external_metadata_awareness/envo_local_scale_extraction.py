import logging
from typing import List
import yaml
import click
from oaklib import get_adapter
from oaklib.query import onto_query, SimpleQueryTerm

# Configure logging
logging.basicConfig(level=logging.WARN, format='%(asctime)s - %(levelname)s - %(message)s')


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


def retrieve_individual_terms(terms_to_retrieve: List[str], adapter) -> List[str]:
    """
    Creates a list of CURIEs based on the provided list of term labels.

    :param terms_to_retrieve: List of term labels.
    :param envo: The ontology adapter.
    """
    all_ids = []

    for term_label in terms_to_retrieve:
        # Find the CURIE for the label
        list_to_exclude = onto_query([term_label], adapter)
        print("term_label", term_label)
        print("list_to_exclude", list_to_exclude)
        all_ids.extend(list_to_exclude)
    return list(set(all_ids))


def extract_terms_to_file(oak_config_file, extraction_config):
    # Load the ontology using the get_adapter function
    envo = get_adapter(oak_config_file)

    # Get the entity and exclusions from the config
    initial_term_label = extraction_config['entity']
    initial_term_list = onto_query([".desc//p=i", initial_term_label], envo)
    logging.info(f"Length of initial term list: {len(initial_term_list)}")

    exclusion_terms_and_children = create_exclusion_list(extraction_config.get('term_and_descendant_exclusions', []),
                                                         envo)

    exclusion_terms_from_text = create_text_exclusion_list(extraction_config.get('text_exclusions', []),
                                                           envo)

    exclude_single_terms = retrieve_individual_terms(extraction_config.get('exclude_single_terms', []), envo)
    solo_inclusion_terms = extraction_config.get('post_process_inclusion_single_terms', [])
    logging.info("solo_inclusion_terms", solo_inclusion_terms)
    post_process_inclusion_single_terms = retrieve_individual_terms(extraction_config.get('post_process_inclusion_single_terms', []), envo)
    logging.info("post_process_inclusion_terms", post_process_inclusion_single_terms)


    exclusion_list = exclusion_terms_and_children + exclusion_terms_from_text + exclude_single_terms
    logging.info(f"Length of excluded terms and descendants: {len(exclusion_terms_and_children)}")
    logging.info(f"Length of excluded terms from text: {len(exclusion_terms_from_text)}")
    logging.info(f"Length of excluded terms from solo terms: {len(post_process_inclusion_single_terms)}")

    remaining_items = exclude_terms(initial_term_list, exclusion_list)
    logging.info(f"Length of remaining items: {len(remaining_items)}")

    final_list_to_retrieve = post_process_inclusion_single_terms + remaining_items

    results = onto_query(final_list_to_retrieve, envo, labels=True)

    # Write the results to the output file specified in the extraction config
    output_file_path = extraction_config['output']
    with open(output_file_path, 'w') as output_file:
        for curie, label in results:
            output_file.write(f"{curie}: {label}\n")

    logging.info(f"Results written to {output_file_path}")


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

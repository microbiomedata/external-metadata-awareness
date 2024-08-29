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


def create_exclusion_query(term_labels, adapter):
    """
    Creates a combined FunctionQuery to exclude specific terms and their descendants.

    :param term_labels: List of term labels to exclude.
    :param adapter: The ontology adapter.
    :return: Combined FunctionQuery to exclude all specified terms and their descendants.
    """
    exclusion_queries = []

    for label in term_labels:
        # Find the CURIE for the label
        term_curies = onto_query(SimpleQueryTerm(term=label), adapter)
        if term_curies:
            term_curie = term_curies[0]  # Assuming one CURIE per label
            # Create a descendant exclusion query for the term
            exclusion_query = FunctionQuery(
                function=FunctionEnum.DESCENDANT,
                argument=term_curie,
                description=f"Descendants of {label}"
            )
            exclusion_queries.append(exclusion_query)

    # Combine all exclusion queries into one using the OR (|) operator
    if exclusion_queries:
        combined_exclusion_query = exclusion_queries[0]
        for query in exclusion_queries[1:]:
            combined_exclusion_query = combined_exclusion_query | query
        return combined_exclusion_query
    else:
        return None


def create_text_exclusion_query(text_exclusions, adapter):
    """
    Creates a combined FunctionQuery to exclude specific terms based on text matching.

    :param text_exclusions: List of text patterns to exclude.
    :param adapter: The ontology adapter.
    :return: Combined FunctionQuery to exclude all specified text matches.
    """
    text_exclusion_queries = []

    for text in text_exclusions:
        exclusion_query = SimpleQueryTerm(term=text)
        text_exclusion_queries.append(exclusion_query)

    # Combine all exclusion queries into one using the OR (|) operator
    if text_exclusion_queries:
        combined_text_exclusion_query = text_exclusion_queries[0]
        for query in text_exclusion_queries[1:]:
            combined_text_exclusion_query = combined_text_exclusion_query | query
        return combined_text_exclusion_query
    else:
        return None


def process_ontology(oak_config_file, extraction_config):
    # Load the ontology using the get_adapter function
    oak_adapter = get_adapter(oak_config_file)

    # Get the entity and exclusions from the config
    initial_term_label = extraction_config['entity']
    initial_term_curies = onto_query(SimpleQueryTerm(term=initial_term_label), oak_adapter)

    if not initial_term_curies:
        raise ValueError(f"Entity '{initial_term_label}' not found in the ontology.")

    initial_term_curie = initial_term_curies[0]
    print("initial_term_curie", initial_term_curie)

    # Create exclusion queries from terms
    term_exclusion_query = create_exclusion_query(extraction_config.get('term_exclusions', []), oak_adapter)

    # Create exclusion queries from text patterns
    text_exclusion_query = create_text_exclusion_query(extraction_config.get('text_exclusions', []), oak_adapter)

    # Combine term and text exclusion queries
    combined_exclusion_query = None
    if term_exclusion_query and text_exclusion_query:
        combined_exclusion_query = term_exclusion_query | text_exclusion_query
    elif term_exclusion_query:
        combined_exclusion_query = term_exclusion_query
    elif text_exclusion_query:
        combined_exclusion_query = text_exclusion_query

    # Main query for descendants of the specified entity
    material_entity_query = FunctionQuery(
        function=FunctionEnum.DESCENDANT,
        argument=initial_term_curie,  # Assuming one CURIE for the entity
        description=f"Descendants of {initial_term_label}"
    )

    # Combine the main query with the exclusion query
    if combined_exclusion_query:
        final_query = material_entity_query - combined_exclusion_query
    else:
        final_query = material_entity_query

    # Execute the final query
    result = onto_query(final_query, oak_adapter)

    # Write the results to the output file
    with open(extraction_config['output'], 'w') as output_file:
        for curie in result:
            label = oak_adapter.label(curie)
            output_file.write(f"{curie}: {label}\n")
            print(curie, label)


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
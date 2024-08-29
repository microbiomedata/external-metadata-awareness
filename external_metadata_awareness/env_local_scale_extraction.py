import yaml
import click
from oaklib import get_adapter


def load_configs(oak_config_file, extraction_config_file):
    with open(oak_config_file, 'r') as file:
        oak_config = yaml.safe_load(file)
    with open(extraction_config_file, 'r') as file:
        extraction_config = yaml.safe_load(file)
    return oak_config, extraction_config


def process_ontology(oak_config_file, extraction_config):
    # Load the ontology using the get_adapter function
    oak_adapter = get_adapter(oak_config_file)

    # Get the entity and exclusions from the config
    initial_term_label = extraction_config['entity']
    initial_term_curie = oak_adapter.curies_by_label(label=initial_term_label)
    exclusion_labels = extraction_config['exclusions']

    # Get all descendants of the initial term
    descendants = oak_adapter.descendants(initial_term_curie)

    # Filter out the excluded terms
    filtered_descendants = [
        term for term in descendants
        if not any(oak_adapter.label(term) == exclusion for exclusion in exclusion_labels)
    ]

    # Write the results to the output file
    with open(extraction_config['output'], 'w') as output_file:
        for term in filtered_descendants:
            output_file.write(f"{term}: {oak_adapter.label(term)}\n")


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

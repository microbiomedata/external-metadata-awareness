import yaml
import click
from oaklib import get_adapter


def load_config(config_file):
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    return config


def process_ontology(config):
    # Load the ontology using the get_adapter function
    ontology = get_adapter(config['input'])

    # Get the entity and exclusions from the config
    initial_term = config['entity']
    exclusions = config['exclusions']

    # Get all descendants of the initial term
    descendants = ontology.descendants(initial_term)

    # Filter out the excluded terms
    filtered_descendants = [
        term for term in descendants
        if not any(ontology.label(term) == exclusion for exclusion in exclusions)
    ]

    # Write the results to the output file
    with open(config['output'], 'w') as output_file:
        for term in filtered_descendants:
            output_file.write(f"{term}: {ontology.label(term)}\n")


@click.command()
@click.argument('config_file')
def cli(config_file):
    """
    CLI tool to process an ontology based on the provided YAML configuration file.
    """
    config = load_config(config_file)
    process_ontology(config)


if __name__ == "__main__":
    cli()

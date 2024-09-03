import pandas as pd
import click
from oaklib import get_adapter


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
def lookup_authoritative_labels(input_file: str, output_file: str, oak_adapter_string: str) -> None:
    """
    Perform authoritative label lookup for CURIEs in a TSV file and save the results.

    Args:
        input_file (str): Path to the input TSV file.
        output_file (str): Path to save the output TSV file.
        oak_adapter_string (str): OAK adapter string for accessing the ontology.
    """
    # Load the TSV file into a DataFrame
    df = pd.read_csv(input_file, sep='\t')

    # Initialize the ontology adapter
    adapter = get_adapter(oak_adapter_string)

    # Perform label lookup for each relevant column
    df['env_broad_scale_authoritative_label'] = df['env_broad_scale_id'].apply(lambda x: get_ontology_label(x, adapter))
    df['env_local_scale_authoritative_label'] = df['env_local_scale_id'].apply(lambda x: get_ontology_label(x, adapter))
    df['env_medium_authoritative_label'] = df['env_medium_id'].apply(lambda x: get_ontology_label(x, adapter))

    # Save the updated DataFrame back to a new TSV file
    df.to_csv(output_file, sep='\t', index=False)

    print(f"Authoritative labels have been looked up and saved to {output_file}")


if __name__ == '__main__':
    lookup_authoritative_labels()

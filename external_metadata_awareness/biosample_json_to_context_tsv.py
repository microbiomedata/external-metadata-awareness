import json
import csv
from typing import Dict, Any, List
import click


@click.command()
@click.option('--input-file', '-i', type=click.Path(exists=True), required=True,
              help='Path to the input JSON file containing biosample data.')
@click.option('--output-file', '-o', type=click.Path(), required=True,
              help='Path to the output TSV file to be created.')
def create_biosample_table(input_file: str, output_file: str) -> None:
    """
    Create a TSV table of biosample data from a JSON file.

    This script reads a JSON file containing biosample data and creates a TSV (Tab-Separated Values)
    file with selected fields for each biosample. The environmental scale fields use term.id for values
    and prefer term.name (falling back to has_raw_value) for labels. Additional fields for
    env_package.has_raw_value and part_of are also included.
    """
    with open(input_file, 'r') as file:
        # data: Dict[str, Any] = json.load(file)
        data = json.load(file)

    fieldnames: List[str] = [
        'id', 'insdc_biosample_identifiers',
        'env_broad_scale_id', 'env_broad_scale_label',
        'env_local_scale_id', 'env_local_scale_label',
        'env_medium_id', 'env_medium_label',
        'env_package_has_raw_value', 'part_of'
    ]

    with open(output_file, 'w', newline='') as tsvfile:
        writer = csv.DictWriter(tsvfile, fieldnames=fieldnames, delimiter='\t')

        writer.writeheader()

        biosamples_written = 0
        # for biosample in data['resources']:
        for biosample in data:
            insdc_identifiers = biosample.get('insdc_biosample_identifiers', [])
            env_broad_scale_label = get_label(biosample.get('env_broad_scale'))
            env_local_scale_label = get_label(biosample.get('env_local_scale'))
            env_medium_label = get_label(biosample.get('env_medium'))

            # Extracting optional scalar env_package.has_raw_value
            env_package_has_raw_value = biosample.get('env_package', {}).get('has_raw_value', '')

            # Extracting required multivalued part_of
            part_of = '|'.join(biosample.get('part_of', []))  # Assuming part_of is a list of strings

            row: Dict[str, str] = {
                'id': biosample['id'],
                'insdc_biosample_identifiers': '|'.join(insdc_identifiers) if insdc_identifiers else '',
                'env_broad_scale_id': biosample['env_broad_scale']['term']['id'],
                'env_broad_scale_label': env_broad_scale_label,
                'env_local_scale_id': biosample['env_local_scale']['term']['id'],
                'env_local_scale_label': env_local_scale_label,
                'env_medium_id': biosample['env_medium']['term']['id'],
                'env_medium_label': env_medium_label,
                'env_package_has_raw_value': env_package_has_raw_value,
                'part_of': part_of
            }
            writer.writerow(row)
            biosamples_written += 1

    click.echo(f"TSV file has been created: {output_file}")
    click.echo(f"Total biosamples written: {biosamples_written}")


def get_label(env_scale: Dict[str, Any]) -> str:
    """Safely extract label from environmental scale data."""
    if env_scale:
        term = env_scale.get('term')
        if term:
            return term.get('name', term.get('has_raw_value', ''))
    return ''


if __name__ == '__main__':
    create_biosample_table()

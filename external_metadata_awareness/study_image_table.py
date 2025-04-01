import json
import csv
import click
from typing import List, Dict, Any


def load_json(file_path: str) -> List[Dict[str, Any]]:
    """Load JSON data from a file."""
    with open(file_path, 'r') as file:
        return json.load(file)


def extract_study_data(studies: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Extract relevant fields from the study data."""
    extracted_data = []
    for study in studies:
        study_id = study.get('id', '')
        principal_investigator = study.get('principal_investigator', {}).get('profile_image_url', '')
        study_images = study.get('study_image', [])
        study_image_urls = ', '.join([image.get('url', '') for image in study_images])

        extracted_data.append({
            'id': study_id,
            'principal_investigator.profile_image_url': principal_investigator,
            'study_image': study_image_urls
        })
    return extracted_data


def write_tsv(output_file: str, data: List[Dict[str, str]]) -> None:
    """Write extracted data to a TSV file."""
    headers = ['id', 'principal_investigator.profile_image_url', 'study_image']

    with open(output_file, 'w', newline='') as tsvfile:
        writer = csv.DictWriter(tsvfile, fieldnames=headers, delimiter='\t')
        writer.writeheader()
        for row in data:
            writer.writerow(row)


@click.command()
@click.option('--input-file', '-i', type=click.Path(exists=True), required=True, help="Path to the input JSON file.")
@click.option('--output-file', '-o', type=click.Path(), required=True, help="Path to the output TSV file.")
def generate_tsv_report(input_file: str, output_file: str) -> None:
    """
    Generate a TSV report from a JSON file containing study data.

    The report will include one line for each study, including columns for
    the id, principal_investigator.profile_image_url, and study_image value(s).
    """
    data = load_json(input_file)
    extracted_data = extract_study_data(data)
    write_tsv(output_file, extracted_data)
    click.echo(f"TSV report generated: {output_file}")


if __name__ == '__main__':
    generate_tsv_report()

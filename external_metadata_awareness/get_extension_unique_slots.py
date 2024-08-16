# with open('mixs_extensions_with_slots.json', 'r') as file:

import json
import click


@click.command()
@click.option('--input-file', 'input_file', type=click.Path(exists=True), required=True,
              help='The path to the input JSON file with extension data.')
@click.option('--output-file', 'output_file', type=click.Path(), required=True,
              help='The path to the output JSON file where results will be saved.')
def process_json(input_file: str, output_file: str):
    """
    Load JSON data from a file, process it to find unique slots per extension,
    and save the results to another JSON file.

    Args:
    input_file (str): The path to the input JSON file with extension data.
    output_file (str): The path to the output JSON file where results will be saved.
    """
    # Load the JSON data from the file
    with open(input_file, 'r') as file:
        data = json.load(file)

    # Dictionary to store all slots across extensions for comparison
    all_slots = {}

    # Populate the all_slots dictionary with counts of occurrences for each slot
    for extension, details in data.items():
        for slot in details['slots']:
            if slot in all_slots:
                all_slots[slot] += 1
            else:
                all_slots[slot] = 1

    # Dictionary to store unique slots for each extension
    unique_slots_per_extension = {}

    # Populate unique_slots_per_extension with slots that only appear once in all_slots
    for extension, details in data.items():
        unique_slots = [slot for slot in details['slots'] if all_slots[slot] == 1]
        unique_slots_per_extension[extension] = sorted(unique_slots)

    # Sort the extensions dictionary
    sorted_extensions = dict(sorted(unique_slots_per_extension.items()))

    # Save the sorted unique slots per extension into a JSON file
    with open(output_file, 'w') as outfile:
        json.dump(sorted_extensions, outfile, indent=4)


if __name__ == "__main__":
    process_json()

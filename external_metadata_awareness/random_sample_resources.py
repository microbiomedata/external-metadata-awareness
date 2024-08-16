import json
import random
import click


@click.command()
@click.option('--input-file', required=True, type=str, help='Path to the input JSON file.')
@click.option('--output-file', required=True, type=str,
              help='Path to the output JSON file where the downsampled data will be saved.')
@click.option('--sample-percentage', required=True, type=float,
              help='Percentage of the data to keep (e.g., 10 for 10%).')
def downsample_json_resources(input_file: str, output_file: str, sample_percentage: float):
    """
    Downsample a JSON file containing a list of resources under a 'resources' key.

    Args:
    input_file (str): Path to the input JSON file.
    output_file (str): Path to the output JSON file.
    sample_percentage (float): Percentage of the data to keep.

    This function loads a JSON file, randomly selects a subset of the data under the 'resources' key based on the specified percentage, and writes the downsampled data to a new file.
    """
    # Load the original JSON file
    with open(input_file, 'r') as file:
        data = json.load(file)

    # # Extract the list of resources
    # resources = data['resources']

    resources = data

    # Calculate the number of resources to keep
    number_to_keep = int(len(resources) * (sample_percentage / 100))

    # Randomly select a subset of resources
    downsampled_resources = random.sample(resources, number_to_keep)

    # # Create the new JSON structure with the downsampled resources
    # new_data = {'resources': downsampled_resources}

    new_data = downsampled_resources

    # Write the downsampled data to a new JSON file
    with open(output_file, 'w') as file:
        json.dump(new_data, file, indent=4)


if __name__ == '__main__':
    downsample_json_resources()

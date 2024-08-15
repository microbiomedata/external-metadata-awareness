import xml.etree.ElementTree as ET
import csv
import click


@click.command()
@click.option('--xml-file', required=True, type=click.Path(exists=True), help='Path to the XML file.')
@click.option('--output-file', required=True, type=click.Path(), help='Path to the output CSV file.')
def xml_to_csv(xml_file: str, output_file: str):
    """
    This script reads an XML file and extracts the name, package group,
    and environmental package for each node, then writes this data to a CSV file.

    Parameters:
        xml_file (str): Path to the XML file.
        output_file (str): Path to the output CSV file.
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()

    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Name', 'Package Group', 'Env Package'])

        for package in root.findall('.//Package'):
            name = package.find('Name').text if package.find('Name') is not None else ''
            package_group = package.get('group', '')
            env_package = package.find('EnvPackage').text if package.find(
                'EnvPackage') is not None else ''

            writer.writerow([name, package_group, env_package])


if __name__ == '__main__':
    xml_to_csv()

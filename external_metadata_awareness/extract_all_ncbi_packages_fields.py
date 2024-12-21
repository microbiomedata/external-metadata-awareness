import click
import pandas as pd
from xml.etree import ElementTree as ET
import re


def parse_xml(xml_file_path: str) -> ET.Element:
    """Load and parse the XML file.

    Args:
        xml_file_path (str): Path to the XML file.

    Returns:
        ET.Element: Parsed XML root element.
    """
    tree = ET.parse(xml_file_path)
    return tree.getroot()


def to_snake_case(name: str) -> str:
    """Convert an UpperCamelCase string to lower_snake_case.

    Args:
        name (str): String in UpperCamelCase.

    Returns:
        str: String in lower_snake_case.
    """
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()


def discover_not_appropriate_keys(root: ET.Element) -> set:
    """Discover unique keys from NotAppropriateFor nodes.

    Args:
        root (ET.Element): Root element of the parsed XML.

    Returns:
        set: Unique keys in NotAppropriateFor nodes.
    """
    not_appropriate_keys = set()
    for package in root.findall('.//Package'):
        not_appropriate_for_node = package.find('NotAppropriateFor')
        if not_appropriate_for_node is not None and not_appropriate_for_node.text:
            for value in not_appropriate_for_node.text.split(';'):
                not_appropriate_keys.add(value.strip())
    return not_appropriate_keys


def process_package_nodes(root: ET.Element, not_appropriate_keys: set) -> pd.DataFrame:
    """Process package nodes to extract data for TSV projection.

    Args:
        root (ET.Element): Root element of the parsed XML.
        not_appropriate_keys (set): Unique NotAppropriateFor keys.

    Returns:
        pd.DataFrame: DataFrame containing the processed data.
    """
    tsv_data = []

    for package in root.findall('.//Package'):
        package_data = {}

        # Add package attributes
        for attr, value in package.attrib.items():
            # Skip any attribute whose lower-cased name includes 'antibiogram'
            if 'antibiogram' in attr.lower():
                continue
            package_data[to_snake_case(attr)] = value

        # Add child node content, explicitly skipping Antibiogram subnodes
        for child in package:
            if 'antibiogram' in child.tag.lower():
                continue  # Skip Antibiogram subnodes entirely
            if child.tag == 'NotAppropriateFor':
                # Handle NotAppropriateFor values dynamically
                not_appropriate_values = {key: 0 for key in not_appropriate_keys}
                if child.text:
                    for value in child.text.split(';'):
                        clean_value = value.strip()
                        if clean_value in not_appropriate_values:
                            not_appropriate_values[clean_value] = 1

                # Add atomized NotAppropriateFor values
                for key, val in not_appropriate_values.items():
                    package_data[f'{key}_inappropriate'] = "true" if val else None
            else:
                # Add all other child nodes dynamically
                package_data[to_snake_case(child.tag)] = child.text.strip() if child.text else ''

        # Add antibiogram association based solely on the 'antibiogram' attribute being explicitly "true"
        if package.attrib.get('antibiogram') == 'true':
            package_data['antibiogram'] = "true"

        tsv_data.append(package_data)

    # Create a DataFrame for the TSV projection
    df_tsv_projection = pd.DataFrame(tsv_data)

    # Ensure boolean columns retain consistency for presence/absence
    boolean_columns = [col for col in df_tsv_projection.columns if
                       col.endswith('_inappropriate') or col == 'antibiogram']
    for col in boolean_columns:
        df_tsv_projection[col] = df_tsv_projection[col].where(df_tsv_projection[col] == "true", None)

    return df_tsv_projection


@click.command()
@click.option('--xml-file', required=True, type=click.Path(exists=True), help='Path to the XML file.')
@click.option('--output-file', required=True, type=click.Path(), help='Path to save the output TSV file.')
def main(xml_file: str, output_file: str) -> None:
    """Process an XML file of packages and export the data to a TSV file.

    Args:
        xml_file (str): Path to the input XML file.
        output_file (str): Path to save the output TSV file.
    """
    root = parse_xml(xml_file)
    not_appropriate_keys = discover_not_appropriate_keys(root)
    df_tsv_projection = process_package_nodes(root, not_appropriate_keys)

    # Save the DataFrame to a TSV file
    df_tsv_projection.to_csv(output_file, sep='\t', index=False)
    click.echo(f"TSV projection saved to {output_file}")


if __name__ == '__main__':
    main()

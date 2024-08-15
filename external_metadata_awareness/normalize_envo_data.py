import re
import csv
from typing import List, Tuple
import click


@click.command()
@click.option('--input-file', type=click.File('r'), required=True, help='Path to the file containing the raw data.')
@click.option('--output-file', type=str, default='normalized_data.csv', help='Output CSV file name.')
@click.option('--ontology-prefix', type=str, default='ENVO', help='Ontology prefix to normalize, default is ENVO.')
@click.option('--additional-column-name', type=str, help='Name of an additional column to add to every row.')
@click.option('--additional-column-value', type=str, help='Static value to put in the additional column for every row.')
@click.option('--val-col-name', type=str, help='Column name containing the values to parse in CSV input.')
@click.option('--count-col-name', type=str, help='Column name containing the counts in CSV input.')
def main(input_file, output_file, ontology_prefix, additional_column_name, additional_column_value, val_col_name,
         count_col_name):
    """
    Processes a file containing environment ontology labels and CURIEs, normalizes the data,
    and writes the normalized data to a CSV file with configurable ontology prefix handling,
    optional additional column, and support for CSV input with specific value and count columns.
    """
    if val_col_name:
        normalized_data = process_csv(input_file, ontology_prefix, val_col_name, count_col_name)
        if count_col_name:
            header = ['raw_text', 'portion_parsed', 'normalized_curie', 'normalized_label', 'count']
        else:
            header = ['raw_text', 'portion_parsed', 'normalized_curie', 'normalized_label']
    else:
        lines = input_file.readlines()
        normalized_data = process_lines(lines, ontology_prefix)
        header = ['raw_text', 'portion_parsed', 'normalized_curie', 'normalized_label']

    if additional_column_name and additional_column_value is not None:
        normalized_data = [line + (additional_column_value,) for line in normalized_data]
        header.append(additional_column_name)

    write_to_csv(normalized_data, output_file, header)
    click.echo(f"Data processed and written to {output_file}")


def normalize_text(text: str, curie: str) -> str:
    """
    Normalizes the textual label by removing CURIEs, brackets, leading underscores, exclamation points,
    and trimming whitespace.

    Args:
        text: The raw label text.
        curie: The extracted CURIE to be removed from the text.

    Returns:
        A normalized label string without CURIEs, brackets, and exclamation points.
    """
    # Remove the specific CURIE and any enclosing brackets or parentheses
    text = re.sub(rf'[\[\]()]*{re.escape(curie)}[\[\]()]*', '', text)
    # Remove leading underscores, exclamation points, and trim whitespace
    text = re.sub(r'^_+|!+', '', text).strip()
    return text


def normalize_curie(curie: str, prefix: str) -> str:
    if not curie:
        return ''
    # Remove brackets and normalize separators
    curie = re.sub(r'[\[\]()]', '', curie)
    curie = re.sub(r'[_\s]', ':', curie)
    # Match the prefix (case-insensitive) and digits
    match = re.search(rf'({re.escape(prefix)})[:_\s]?(\d{{7,8}})', curie, re.IGNORECASE)
    if match:
        matched_prefix, digits = match.groups()
        return f"{prefix.upper()}:{digits}"
    return ''


def process_csv(input_file, ontology_prefix: str, val_col_name: str, count_col_name: str) -> List[
    Tuple[str, str, str, str, int]]:
    data = []
    # Updated regex pattern to handle spaces after the prefix
    prefix_pattern = rf'({re.escape(ontology_prefix)})[:_\s]?\d{{7,8}}'
    reader = csv.DictReader(input_file)

    for row in reader:
        raw_value = row[val_col_name].strip()
        count = int(row[count_col_name]) if count_col_name else 1

        # Split the value on pipes
        portions = raw_value.split('|')
        for portion in portions:
            portion = portion.strip()
            if not portion:
                continue

            curie_matches = list(re.finditer(prefix_pattern, portion, re.IGNORECASE))
            if curie_matches:
                for match in curie_matches:
                    raw_curie = match.group(0)
                    normalized_curie = normalize_curie(raw_curie, ontology_prefix)
                    label_part = re.sub(rf'\s*[\[\]()]*{re.escape(raw_curie)}[\[\]()]*\s*', '', portion).strip()
                    normalized_label = normalize_text(label_part, raw_curie)
                    data.append((raw_value, portion, normalized_curie, normalized_label, count))
            else:
                # Append a row even if CURIE is not found but prefix is present
                data.append((raw_value, portion, '', normalize_text(portion, ''), count))

    return data


def process_lines(lines: List[str], ontology_prefix: str) -> List[Tuple[str, str, str, str]]:
    """
    Processes each line of input data to extract and normalize CURIEs and labels based on the ontology prefix.

    Args:
        lines: List of raw input lines.
        ontology_prefix: The ontology prefix for normalization.

    Returns:
        A list of tuples containing the raw text, portion parsed, normalized CURIE, and normalized label.
    """
    data = []
    # Updated regex pattern to handle spaces after the prefix
    prefix_pattern = rf'({ontology_prefix}|{ontology_prefix.lower()}): ?\d{{7,8}}'
    for line in lines:
        original_line = line.strip()
        if not original_line:
            continue

        # Split the line on pipes
        portions = original_line.split('|')

        for portion in portions:
            portion = portion.strip()
            if not portion:
                continue

            # Match any occurrence of the prefix, with or without ID
            curie_match = re.search(rf'(\[{prefix_pattern}\]|\b{prefix_pattern}\b)', portion)
            if curie_match:
                raw_curie = curie_match.group(1)
                label_part = re.sub(rf'\s*[\[\]()]*{re.escape(raw_curie)}[\[\]()]*\s*', '', portion)
            else:
                raw_curie = ''
                label_part = portion

            normalized_curie = normalize_curie(raw_curie, ontology_prefix)
            normalized_label = normalize_text(label_part, raw_curie)
            data.append((original_line, portion, normalized_curie, normalized_label))

    return data


def write_to_csv(data: List[Tuple[str, ...]], filename: str, header: List[str]) -> None:
    """
    Writes the processed data to a CSV file.

    Args:
        data: A list of tuples containing the processed data.
        filename: The name of the CSV file to write the data to.
        header: A list of column headers for the CSV file.
    """
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(data)


if __name__ == "__main__":
    main()

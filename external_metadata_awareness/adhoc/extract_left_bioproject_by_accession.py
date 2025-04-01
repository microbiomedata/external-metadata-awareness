#!/usr/bin/env python3
"""
Extract specific BioProject records from large XML files using iterative parsing.

This script demonstrates memory-efficient XML processing by using lxml's iterparse
feature to handle very large XML files without loading them entirely into memory.
"""

import sys
from typing import Optional
import click
from lxml import etree


def extract_project(xml_file: str, accession: str, output_file: Optional[str] = None) -> bool:
    """
    Extract a specific BioProject record using iterative parsing.

    This function processes the XML file as a stream, which means it only needs
    enough memory to hold one Project element at a time, regardless of how large
    the input file is.

    Args:
        xml_file: Path to the input XML file
        accession: The BioProject accession to find (e.g., "PRJNA230403")
        output_file: Optional path to save the extracted XML. If None, prints to stdout.

    Returns:
        bool: True if the record was found and extracted, False otherwise
    """
    # Create an iterative parser that only looks for Project elements
    context = etree.iterparse(
        xml_file,
        events=("end",),
        tag="Project"  # Only process Project elements
    )

    found = False
    for event, elem in context:
        try:
            # Look for our target accession in this Project
            archive_id = elem.find(".//ArchiveID")
            if archive_id is not None and archive_id.get("accession") == accession:
                # We found our target project! Let's save it.
                found = True

                # Convert to string with nice formatting
                xml_string = etree.tostring(
                    elem,
                    pretty_print=True,
                    encoding='utf-8'
                ).decode('utf-8')

                # Either save to file or print to stdout
                if output_file:
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(xml_string)
                    print(f"Extracted project {accession} to {output_file}")
                else:
                    print(xml_string)

                # We found what we wanted, no need to continue
                break

        finally:
            # Memory cleanup - very important!
            # Clear the current element from memory
            elem.clear()

            # Remove references from root node to the cleaned element
            parent = elem.getparent()
            if parent is not None:
                # Clear all previous siblings of this element
                while elem.getprevious() is not None:
                    del parent[0]

    # Report if we didn't find the record
    if not found:
        print(f"No project found with accession {accession}", file=sys.stderr)

    return found


@click.command()
@click.option(
    '--input-file', '-i',
    type=click.Path(exists=True, dir_okay=False, path_type=str),
    required=True,
    help="Path to the input BioProject XML file"
)
@click.option(
    '--accession', '-a',
    type=str,
    required=True,
    help="BioProject accession number to extract (e.g., PRJNA230403)"
)
@click.option(
    '--output-file', '-o',
    type=click.Path(dir_okay=False, writable=True, path_type=str),
    help="Path to save the extracted XML (optional, defaults to stdout)"
)
def main(input_file: str, accession: str, output_file: Optional[str]):
    """
    Extract a BioProject record from a large XML file using memory-efficient parsing.

    This tool uses iterative parsing to handle very large XML files efficiently,
    making it suitable for extracting even the largest BioProject records without
    running into memory limitations.

    Example usage:
        python extract_bioproject.py -i bioproject.xml -a PRJNA230403 -o project_230403.xml
    """
    extract_project(input_file, accession, output_file)


if __name__ == "__main__":
    main()

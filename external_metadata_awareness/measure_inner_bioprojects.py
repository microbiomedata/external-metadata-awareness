#!/usr/bin/env python3
"""
Iterate through a large BioProject XML file to find "leaf" <Project> elements
(that do not contain any nested <Project>), estimate their JSON-based size
for MongoDB, and track the largest record found so far.
"""

import sys
import datetime
import time
from typing import Optional

import click
from lxml import etree
import xmltodict
import json


def is_leaf_project(element: etree._Element) -> bool:
    """
    Determine if 'element' is a <Project> that has NO nested <Project> children.

    :param element: An lxml.etree element with tag == "Project".
    :return: True if this Project node has no child <Project> elements, False otherwise.
    """
    # Check for any <Project> descendants
    child = element.find(".//Project")
    return (child is None)


def get_accession(element: etree._Element) -> Optional[str]:
    """
    Extract the 'accession' from:
        <ProjectID>
          <ArchiveID accession="XYZ" .../>
        </ProjectID>
    within the current Project element.

    :param element: An lxml.etree element (tag == "Project").
    :return: The accession string if found, or None.
    """
    archive_id_elem = element.find(".//ArchiveID")
    if archive_id_elem is not None:
        return archive_id_elem.get("accession")
    return None


def estimate_mongodb_size(element: etree._Element) -> int:
    """
    Estimate the size of this Project node if stored as JSON in MongoDB.
    We do this by:
      1) Converting the <Project> subtree to raw XML (bytes).
      2) Parsing that XML to a Python dict with xmltodict.
      3) Dumping that dict to JSON and measuring its byte length.

    :param element: An lxml.etree element.
    :return: Integer size in bytes of the JSON representation.
    """
    raw_xml = etree.tostring(element, encoding="utf-8")
    doc_dict = xmltodict.parse(raw_xml)
    json_bytes = json.dumps(doc_dict, ensure_ascii=False).encode("utf-8")
    return len(json_bytes)


@click.command()
@click.option(
    "--xml-file",
    "xml_file",
    type=click.Path(exists=True, dir_okay=False),
    required=True,
    help="Path to the input BioProject XML file."
)
@click.option(
    "--progress-interval",
    type=int,
    default=10000,
    help="Report progress after parsing this many leaf-level <Project> elements."
)
def cli(xml_file: str, progress_interval: int) -> None:
    """
    Find leaf-level <Project> nodes in a BioProject XML file, estimate their
    JSON-based size, and track/report the largest record found so far.
    """
    context = etree.iterparse(xml_file, events=("end",), tag="Project")

    leaf_count = 0
    largest_size_so_far = 0
    largest_accession = None

    start_time = time.time()

    for _, elem in context:
        # Each time we encounter the end of a <Project>, check if it's a leaf
        if is_leaf_project(elem):
            leaf_count += 1
            # Estimate size in a naive JSON approach
            doc_size = estimate_mongodb_size(elem)
            # Extract accession
            accession = get_accession(elem)

            # If this is bigger than anything we've seen, record it
            if doc_size > largest_size_so_far:
                largest_size_so_far = doc_size
                largest_accession = accession

            # Print periodic progress
            if leaf_count % progress_interval == 0:
                now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
                click.echo(
                    f"{now_iso} - Processed {leaf_count} leaf <Project> nodes so far. "
                    f"Largest size: {largest_size_so_far} bytes (Accession: {largest_accession})"
                )

        # Clear the element from memory to avoid huge usage
        elem.clear()
        parent = elem.getparent()
        while parent is not None and elem.getprevious() is not None:
            del parent[0]

    total_time = time.time() - start_time
    click.echo(f"Done. Found {leaf_count} leaf-level <Project> nodes in {total_time:.2f}s.")
    click.echo(
        f"Largest record size: {largest_size_so_far} bytes (Accession: {largest_accession})"
    )


if __name__ == "__main__":
    cli()

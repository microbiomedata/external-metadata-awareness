#!/usr/bin/env python3
"""
Enhanced version of the BioProject XML analyzer that tracks size distribution
and identifies projects that would exceed MongoDB's 16MB limit.
"""

import sys
import datetime
import time
from typing import Optional, Dict, List
from collections import defaultdict

import click
from lxml import etree
import xmltodict
import json

# MongoDB's BSON document size limit in bytes
MONGODB_SIZE_LIMIT = 16 * 1024 * 1024  # 16MB


def analyze_size_distribution(sizes: List[int]) -> Dict:
    """
    Analyze the distribution of document sizes.

    :param sizes: List of document sizes in bytes
    :return: Dictionary with distribution statistics
    """
    if not sizes:
        return {}

    sizes.sort()
    total = len(sizes)

    return {
        'min': sizes[0],
        'max': sizes[-1],
        'median': sizes[total // 2],
        'mean': sum(sizes) / total,
        'p95': sizes[int(total * 0.95)],
        'p99': sizes[int(total * 0.99)],
        'total_records': total
    }


def get_size_bucket(size: int) -> str:
    """
    Get the appropriate size bucket for a document size.

    :param size: Size in bytes
    :return: String describing the size bucket
    """
    kb = size / 1024
    mb = kb / 1024

    if mb >= 1:
        return f"{mb:.1f}MB"
    elif kb >= 1:
        return f"{kb:.1f}KB"
    else:
        return f"{size}B"


@click.command()
@click.option(
    "--xml-file",
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
    Analyze leaf-level <Project> nodes in a BioProject XML file with enhanced
    size distribution tracking and identification of problematic records.
    """
    context = etree.iterparse(xml_file, events=("end",), tag="Project")

    leaf_count = 0
    problem_records = []  # Records exceeding MongoDB limit
    all_sizes = []
    size_distribution = defaultdict(int)

    start_time = time.time()

    for _, elem in context:
        if is_leaf_project(elem):
            leaf_count += 1
            doc_size = estimate_mongodb_size(elem)
            accession = get_accession(elem)

            # Track size distribution
            size_bucket = get_size_bucket(doc_size)
            size_distribution[size_bucket] += 1
            all_sizes.append(doc_size)

            # Track problematic records
            if doc_size > MONGODB_SIZE_LIMIT:
                problem_records.append((accession, doc_size))

            if leaf_count % progress_interval == 0:
                now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
                click.echo(
                    f"{now_iso} - Processed {leaf_count} leaf <Project> nodes. "
                    f"Found {len(problem_records)} records exceeding MongoDB limit."
                )

        # Memory management
        elem.clear()
        parent = elem.getparent()
        while parent is not None and elem.getprevious() is not None:
            del parent[0]

    # Calculate and display final statistics
    stats = analyze_size_distribution(all_sizes)

    click.echo("\nSize Distribution Statistics:")
    for stat, value in stats.items():
        if stat.startswith('p'):
            click.echo(f"{stat}: {get_size_bucket(value)}")
        elif stat in ['min', 'max', 'median', 'mean']:
            click.echo(f"{stat}: {get_size_bucket(value)}")
        else:
            click.echo(f"{stat}: {value}")

    click.echo("\nSize Distribution Buckets:")
    for bucket, count in sorted(size_distribution.items()):
        click.echo(f"{bucket}: {count} records")

    if problem_records:
        click.echo("\nRecords exceeding MongoDB 16MB limit:")
        for accession, size in problem_records:
            click.echo(f"Accession: {accession}, Size: {get_size_bucket(size)}")

    total_time = time.time() - start_time
    click.echo(f"\nProcessing completed in {total_time:.2f}s")  # !/usr/bin/env python3


"""
Enhanced version of the BioProject XML analyzer that tracks size distribution
and identifies projects that would exceed MongoDB's 16MB limit.
"""

import sys
import datetime
import time
from typing import Optional, Dict, List
from collections import defaultdict

import click
from lxml import etree
import xmltodict
import json

# MongoDB's BSON document size limit in bytes
MONGODB_SIZE_LIMIT = 16 * 1024 * 1024  # 16MB


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


def analyze_size_distribution(sizes: List[int]) -> Dict:
    """
    Analyze the distribution of document sizes.

    :param sizes: List of document sizes in bytes
    :return: Dictionary with distribution statistics
    """
    if not sizes:
        return {}

    sizes.sort()
    total = len(sizes)

    return {
        'min': sizes[0],
        'max': sizes[-1],
        'median': sizes[total // 2],
        'mean': sum(sizes) / total,
        'p95': sizes[int(total * 0.95)],
        'p99': sizes[int(total * 0.99)],
        'total_records': total
    }


def get_size_bucket(size: int) -> str:
    """
    Get the appropriate size bucket for a document size.
    Returns a human-readable string representation of the size.

    :param size: Size in bytes
    :return: String describing the size bucket (e.g., "1.5MB" or "500KB")
    """
    kb = size / 1024
    mb = kb / 1024

    if mb >= 1:
        return f"{mb:.1f}MB"
    elif kb >= 1:
        return f"{kb:.1f}KB"
    else:
        return f"{size}B"


@click.command()
@click.option(
    "--xml-file",
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
    Analyze leaf-level <Project> nodes in a BioProject XML file with enhanced
    size distribution tracking and identification of problematic records.
    """
    context = etree.iterparse(xml_file, events=("end",), tag="Project")

    leaf_count = 0
    problem_records = []  # Records exceeding MongoDB limit
    all_sizes = []
    size_distribution = defaultdict(int)

    start_time = time.time()

    for _, elem in context:
        if is_leaf_project(elem):
            leaf_count += 1
            doc_size = estimate_mongodb_size(elem)
            accession = get_accession(elem)

            # Track size distribution
            size_bucket = get_size_bucket(doc_size)
            size_distribution[size_bucket] += 1
            all_sizes.append(doc_size)

            # Track problematic records
            if doc_size > MONGODB_SIZE_LIMIT:
                problem_records.append((accession, doc_size))

            if leaf_count % progress_interval == 0:
                now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
                click.echo(
                    f"{now_iso} - Processed {leaf_count} leaf <Project> nodes. "
                    f"Found {len(problem_records)} records exceeding MongoDB limit."
                )

        # Memory management
        elem.clear()
        parent = elem.getparent()
        while parent is not None and elem.getprevious() is not None:
            del parent[0]

    # Calculate and display final statistics
    stats = analyze_size_distribution(all_sizes)

    click.echo("\nSize Distribution Statistics:")
    for stat, value in stats.items():
        if stat.startswith('p'):
            click.echo(f"{stat}: {get_size_bucket(value)}")
        elif stat in ['min', 'max', 'median', 'mean']:
            click.echo(f"{stat}: {get_size_bucket(value)}")
        else:
            click.echo(f"{stat}: {value}")

    click.echo("\nSize Distribution Buckets:")
    for bucket, count in sorted(size_distribution.items()):
        click.echo(f"{bucket}: {count} records")

    if problem_records:
        click.echo("\nRecords exceeding MongoDB 16MB limit:")
        for accession, size in problem_records:
            click.echo(f"Accession: {accession}, Size: {get_size_bucket(size)}")

    total_time = time.time() - start_time
    click.echo(f"\nProcessing completed in {total_time:.2f}s")


if __name__ == "__main__":
    cli()

if __name__ == "__main__":
    cli()

#!/usr/bin/env python3
"""
Streaming analysis of a large XML file, computing average and maximum
size of each XML path using lxml.etree.iterparse, with progress reporting.
"""

import time
import datetime
from typing import Dict, Any, List, Optional

import click
from lxml import etree


def get_subtree_size(element: etree._Element) -> int:
    """
    Return the size (in bytes) of the element's entire subtree.

    :param element: An lxml.etree element (root of the subtree).
    :return: The size of this element (including all children) in bytes.
    """
    return len(etree.tostring(element, encoding="utf-8"))


def record_stat(stats: Dict[str, Dict[str, Any]], path: str, size: int) -> None:
    """
    Record size information for a given XML path in the stats dictionary.

    :param stats: A dictionary maintaining path-based statistics.
    :param path: The XML path (e.g., 'Project/ProjectDescr').
    :param size: The size (in bytes) for this path instance.
    """
    if path not in stats:
        stats[path] = {
            "count": 0,
            "total_size": 0,
            "max_size": 0,
        }
    stats[path]["count"] += 1
    stats[path]["total_size"] += size
    if size > stats[path]["max_size"]:
        stats[path]["max_size"] = size


@click.command()
@click.option(
    "--xml-file",
    "xml_file",
    type=click.Path(exists=True, dir_okay=False),
    required=True,
    help="Path to the input XML file (e.g., bioproject.xml)."
)
@click.option(
    "--root-tag",
    "root_tag",
    default=None,
    help=(
            "Optional name of a root-level element to parse (e.g. 'Project'). "
            "If set, we will track the count of these elements to report progress. "
            "If not set, all elements are processed, but you won't get a doc-level count."
    )
)
@click.option(
    "--print-limit",
    "print_limit",
    type=int,
    default=0,
    help=(
            "If greater than 0, limit the number of distinct paths printed. "
            "E.g., --print-limit=100 will show the top 100 (by path sort). "
            "Default is 0 (no limit)."
    )
)
@click.option(
    "--expected-docs",
    "expected_docs",
    type=int,
    default=0,
    help=(
            "Optional expected number of documents for the root tag. "
            "Used for progress reporting. If 0, progress is shown without percentage."
    )
)
@click.option(
    "--progress-interval",
    "progress_interval",
    type=int,
    default=10000,
    help="How many root documents to process before printing a progress message."
)
def cli(
        xml_file: str,
        root_tag: Optional[str],
        print_limit: int,
        expected_docs: int,
        progress_interval: int
) -> None:
    """
    Streaming analysis of a large XML file, computing average and maximum
    size of each XML path, with periodic progress reporting.

    - Parses the file in a streaming fashion (lxml.etree.iterparse).
    - Clears processed elements to keep memory usage low.
    - Prints ISO8601 timestamps and counts for every N (progress_interval) root documents.
    """
    stats: Dict[str, Dict[str, Any]] = {}
    path_stack: List[str] = []

    context = etree.iterparse(xml_file, events=("start", "end"))

    # Variables for progress tracking
    root_count = 0
    start_time = time.time()

    for event, elem in context:
        if event == "start":
            path_stack.append(elem.tag)
        else:  # event == "end"
            path_str = "/".join(path_stack)

            # Measure subtree size
            size = get_subtree_size(elem)
            record_stat(stats, path_str, size)

            # If this element is the root_tag, we've completed one "document"
            if root_tag and elem.tag == root_tag:
                root_count += 1
                if root_count % progress_interval == 0:
                    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
                    if expected_docs > 0:
                        percentage = (root_count / expected_docs) * 100
                        click.echo(
                            f"{now_iso} - Processed {root_count} / {expected_docs} "
                            f"({percentage:.2f}%) {root_tag} elements..."
                        )
                    else:
                        click.echo(
                            f"{now_iso} - Processed {root_count} {root_tag} elements..."
                        )

            # Clear element to free memory
            elem.clear()

            # Also clear references from the parent so we don't hold the entire tree
            parent = elem.getparent()
            while parent is not None and elem.getprevious() is not None:
                del parent[0]

            # Pop the current tag from stack
            path_stack.pop()

    # Finished parsing
    total_time = time.time() - start_time
    click.echo(f"Done parsing in {total_time:.2f} seconds.")

    # Print summary
    # Sort by path (alphabetically).
    sorted_paths = sorted(stats.keys())

    if print_limit > 0:
        sorted_paths = sorted_paths[:print_limit]

    for path_str in sorted_paths:
        path_stats = stats[path_str]
        count = path_stats["count"]
        max_size = path_stats["max_size"]
        avg_size = path_stats["total_size"] / count if count > 0 else 0
        click.echo(
            f"Path: {path_str} | count: {count}, avg_size: {avg_size:.2f}, max_size: {max_size}"
        )


if __name__ == "__main__":
    cli()

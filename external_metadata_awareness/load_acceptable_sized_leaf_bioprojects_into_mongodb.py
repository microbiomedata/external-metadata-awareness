#!/usr/bin/env python3
"""
Load BioProject XML records into MongoDB, handling the hierarchical nature of
the data structure. This script processes each unique Project exactly once,
preserving parent-child relationships while avoiding duplicate processing.
"""

import sys
import time
import json
from typing import Optional, Dict, Any
from datetime import datetime

import click
from pymongo import MongoClient, ASCENDING
from pymongo.collection import Collection
from lxml import etree
import xmltodict


def connect_mongodb(host: str, port: int, database: str, collection: str) -> Collection:
    """
    Establish connection to MongoDB and return the specified collection.
    Creates an index on accession for faster lookups and uniqueness constraints.
    """
    client = MongoClient(host, port)
    db = client[database]
    coll = db[collection]

    # Create an index on accession for faster lookups and uniqueness
    coll.create_index(
        [("ProjectID.ArchiveID.accession", ASCENDING)],
        unique=True,
        background=True
    )

    return coll


def get_child_project_accessions(element: etree._Element) -> list[str]:
    """
    Extract accession numbers from all immediate child Project elements.
    This helps us maintain the project hierarchy without embedding entire projects.
    """
    child_accessions = []

    # Find all immediate child Project elements
    for child in element.findall(".//Project"):
        # Don't include deeper nested projects
        if any(parent.tag == "Project" for parent in child.iterancestors() if parent != element):
            continue

        # Get the accession from this child project
        archive_id = child.find(".//ArchiveID")
        if archive_id is not None and archive_id.get("accession"):
            child_accessions.append(archive_id.get("accession"))

    return child_accessions


def transform_document(doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform a dictionary by:
    1. Removing '@' prefixes from field names
    2. Renaming '#text' fields to 'content'
    3. Flattening the Project structure to the root level

    This ensures consistent field naming and structure in MongoDB.
    """

    def clean_key(key: str) -> str:
        """
        Clean up field names by:
        - Removing '@' prefix if present
        - Replacing '#text' with 'content'
        """
        if key.startswith('@'):
            return key[1:]
        elif key == '#text':
            return 'content'
        return key

    def process_dict(d: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively process a dictionary to clean all key names."""
        result = {}
        for key, value in d.items():
            clean_key_name = clean_key(key)

            if isinstance(value, dict):
                result[clean_key_name] = process_dict(value)
            elif isinstance(value, list):
                result[clean_key_name] = [
                    process_dict(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                result[clean_key_name] = value
        return result

    # First, process the entire document to clean key names
    cleaned = process_dict(doc)

    # If there's a Project key at the root, move its contents to root level
    if 'Project' in cleaned:
        return cleaned['Project']
    return cleaned


def is_nested_project(element: etree._Element) -> bool:
    """
    Determine if this Project element is nested inside another Project.
    This helps us avoid processing the same Project multiple times.
    We check the ancestors of the current element to see if any of them
    are also Project elements.
    """
    parent = element.getparent()
    while parent is not None:
        if parent.tag == "Project":
            return True
        parent = parent.getparent()
    return False


def validate_project(doc: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate a project document before insertion.
    Returns (is_valid, error_message).

    A valid project must have:
    1. A non-null accession number
    2. A properly structured ProjectID section
    """
    try:
        accession = get_accession(doc)
        if not accession:
            return False, "Missing accession number"

        if "ProjectID" not in doc:
            return False, "Missing ProjectID section"

        if "ArchiveID" not in doc["ProjectID"]:
            return False, "Missing ArchiveID in ProjectID"

        return True, None

    except Exception as e:
        return False, f"Validation error: {str(e)}"


def create_minimal_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a minimal version of a BioProject document containing only the ProjectID
    path and an oversize flag. This preserves essential identifying information
    while keeping the document size well under MongoDB limits.
    """
    return {
        "ProjectID": doc["ProjectID"],
        "oversize": True,
        # Include child_bioprojects if present
        **({"child_bioprojects": doc["child_bioprojects"]} if "child_bioprojects" in doc else {})
    }


def get_accession(doc: Dict) -> Optional[str]:
    """Extract the accession from a Project dictionary."""
    try:
        return doc["ProjectID"]["ArchiveID"]["accession"]
    except (KeyError, TypeError):
        return None


def estimate_record_size(doc: Dict) -> int:
    """
    Estimate the size this record would occupy in MongoDB by converting to a string
    and measuring its UTF-8 encoded size.
    """
    return len(str(doc).encode('utf-8'))


def process_project(
        element: etree._Element,
        collection: Collection,
        size_limit: int
) -> Optional[Dict[str, Any]]:
    """
    Process a single Project element and store it in MongoDB.
    Returns None for empty documents (which should be ignored by the caller),
    otherwise returns a dictionary with processing results.
    """
    try:
        # Convert to dictionary format that MongoDB can store
        xml_string = etree.tostring(element, encoding="utf-8")
        doc = xmltodict.parse(
            xml_string,
            process_namespaces=True,
            dict_constructor=dict
        )

        # Transform the document structure to match requirements
        doc = transform_document(doc)

        # Skip completely empty documents silently
        if not doc or (len(doc) == 1 and "ProjectID" in doc and not doc["ProjectID"]):
            return None

        # Get any child project accessions
        child_accessions = get_child_project_accessions(element)

        # Add child projects if any were found
        if child_accessions:
            doc["child_bioprojects"] = child_accessions

        # Validate the document
        is_valid, error_msg = validate_project(doc)
        if not is_valid:
            return {
                "accession": get_accession(doc),
                "size": None,
                "status": "invalid",
                "reason": error_msg,
                "child_count": len(child_accessions) if child_accessions else 0
            }

        # Get the accession for logging (we know it exists now)
        accession = get_accession(doc)

        # Estimate size
        estimated_size = estimate_record_size(doc)

        result = {
            "accession": accession,
            "size": estimated_size,
            "status": "success",
            "reason": None,
            "child_count": len(child_accessions) if child_accessions else 0
        }

        # For oversized records, store minimal version
        if estimated_size > size_limit:
            minimal_doc = create_minimal_doc(doc)
            collection.insert_one(minimal_doc)
            result["reason"] = "stored_minimal"
            result["stored_size"] = estimate_record_size(minimal_doc)
        else:
            # Store complete document
            collection.insert_one(doc)
            result["stored_size"] = estimated_size

    except Exception as e:
        result = {
            "accession": accession if 'accession' in locals() else None,
            "size": estimated_size if 'estimated_size' in locals() else None,
            "status": "error",
            "reason": str(e),
            "child_count": len(child_accessions) if 'child_accessions' in locals() else 0
        }

    return result


@click.command()
@click.option(
    '--input-file', '-i',
    type=click.Path(exists=True, dir_okay=False, path_type=str),
    required=True,
    help="Path to the input BioProject XML file"
)
@click.option(
    '--host',
    default='localhost',
    help="MongoDB host address"
)
@click.option(
    '--port',
    default=27017,
    help="MongoDB port number"
)
@click.option(
    '--database',
    default='biosamples',
    help="MongoDB database name"
)
@click.option(
    '--collection',
    default='bioprojects',
    help="MongoDB collection name"
)
@click.option(
    '--size-limit',
    default=15_000_000,  # 15MB to be safe
    help="Size threshold in bytes for creating minimal records"
)
@click.option(
    '--progress-interval',
    default=1000,
    help="How often to print progress updates"
)
@click.option(
    '--debug/--no-debug',
    default=False,
    help="Print detailed error messages for failed records"
)
def main(
        input_file: str,
        host: str,
        port: int,
        database: str,
        collection: str,
        size_limit: int,
        progress_interval: int,
        debug: bool
):
    """
    Load BioProject XML records into MongoDB.

    This tool:
    - Processes each Project exactly once (avoiding nested duplicates)
    - Preserves project hierarchies via child_bioprojects field
    - Creates minimal records for oversized projects
    - Removes '@' prefixes from field names
    - Renames '#text' fields to 'content'
    - Flattens Project content to root level
    """
    # Connect to MongoDB
    mongo_collection = connect_mongodb(host, port, database, collection)

    # Statistics to track progress
    stats = {
        "processed": 0,
        "success": 0,
        "minimal": 0,
        "invalid": 0,
        "errors": 0,
        "start_time": time.time()
    }

    # Keep track of the last few errors for debugging
    recent_errors = []

    # Create iterator for Project elements
    context = etree.iterparse(input_file, events=("end",), tag="Project")

    try:
        for event, elem in context:
            # Skip if this is a nested Project - we'll handle it through its parent
            if is_nested_project(elem):
                # Clean up this element
                elem.clear()
                parent = elem.getparent()
                if parent is not None:
                    while elem.getprevious() is not None:
                        del parent[0]
                continue

            # Process the record - if None is returned, silently skip it
            result = process_project(elem, mongo_collection, size_limit)
            if result is None:
                # Memory cleanup for skipped record
                elem.clear()
                parent = elem.getparent()
                if parent is not None:
                    while elem.getprevious() is not None:
                        del parent[0]
                continue

            # Only increment processed count for non-empty documents
            stats["processed"] += 1

            # Update statistics
            if result["status"] == "success":
                if result.get("reason") == "stored_minimal":
                    stats["minimal"] += 1
                else:
                    stats["success"] += 1
            elif result["status"] == "invalid":
                stats["invalid"] += 1
            else:
                stats["errors"] += 1

            if debug and result["status"] in ["error", "invalid"]:
                recent_errors.append(
                    f"{result['status'].title()} with accession {result['accession']}: {result['reason']}"
                )
                if len(recent_errors) > 5:  # Keep only recent errors
                    recent_errors.pop(0)

            # Print progress periodically
            if stats["processed"] % progress_interval == 0:
                elapsed = time.time() - stats["start_time"]
                rate = stats["processed"] / elapsed
                print(
                    f"{datetime.now().isoformat()} - "
                    f"Processed: {stats['processed']:,} | "
                    f"Full Records: {stats['success']:,} | "
                    f"Minimal Records: {stats['minimal']:,} | "
                    f"Invalid: {stats['invalid']:,} | "
                    f"Errors: {stats['errors']:,} | "
                    f"Rate: {rate:.1f} records/sec"
                )

                if debug and recent_errors:
                    print("\nRecent issues:")
                    for error in recent_errors:
                        print(f"  {error}")
                    print()

            # Memory management
            elem.clear()
            parent = elem.getparent()
            if parent is not None:
                while elem.getprevious() is not None:
                    del parent[0]

    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Saving final statistics...")

    finally:
        # Print final statistics
        elapsed = time.time() - stats["start_time"]
        print("\nFinal Statistics:")
        print(f"Total time: {elapsed:.1f} seconds")
        print(f"Total processed: {stats['processed']:,}")
        print(f"Successfully loaded (full): {stats['success']:,}")
        print(f"Successfully loaded (minimal): {stats['minimal']:,}")
        print(f"Invalid records: {stats['invalid']:,}")
        print(f"Errors: {stats['errors']:,}")
        print(f"Average rate: {stats['processed'] / elapsed:.1f} records/sec")


if __name__ == "__main__":
    main()

import click
import lxml.etree as ET
import xmltodict
from pymongo import MongoClient
import bson
import time
from datetime import datetime

MAX_BSON_SIZE = 16 * 1024 * 1024  # MongoDB max document size (16MB)


def clean_dict(d):
    """Recursively clean dictionary keys by removing '@' and '#' prefixes."""
    if isinstance(d, dict):
        new_dict = {}
        for key, value in d.items():
            clean_key = key.lstrip("@#")  # Remove '@' or '#' from field names
            new_dict[clean_key] = clean_dict(value)  # Recursively clean values
        return new_dict
    elif isinstance(d, list):
        return [clean_dict(item) for item in d]  # Clean each item in lists
    else:
        return d  # Base case: return value unchanged


def get_accession(project_dict):
    """Extract the ProjectID.ArchiveID.accession value from the document, if present."""
    try:
        return project_dict["ProjectID"]["ArchiveID"]["accession"]
    except KeyError:
        return "UNKNOWN_ACCESSION"


def reduce_oversized_record(project_dict):
    """Keep only `ProjectID` and add `oversize: true` when a record is too large."""
    return {
        "ProjectID": project_dict.get("ProjectID", {}),
        "oversize": True
    }


def parse_and_insert(xml_file, mongo_uri, db_name, collection_name, progress_interval):
    """Parses an NCBI BioProject XML file and inserts ONLY `/PackageSet/Package/Project/Project` documents into MongoDB."""

    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    context = ET.iterparse(xml_file, events=("start", "end"))
    parent_stack = []
    inserted_count = 0
    oversize_count = 0
    total_projects_processed = 0
    start_time = time.time()

    for event, elem in context:
        if event == "start":
            parent_stack.append(elem.tag)

        elif event == "end":
            if parent_stack[-1] == "Project" and len(parent_stack) >= 4 and parent_stack[-4:] == ["PackageSet",
                                                                                                  "Package", "Project",
                                                                                                  "Project"]:
                total_projects_processed += 1

                # Convert XML to dictionary using xmltodict
                project_dict = xmltodict.parse(ET.tostring(elem, encoding="utf-8"))

                # Get rid of root tag wrapping
                project_dict = project_dict.get("Project", {})

                # Clean field names to remove leading '@' or '#'
                project_dict = clean_dict(project_dict)

                if not project_dict:  # Skip empty projects
                    elem.clear()
                    parent_stack.pop()
                    continue

                # Estimate BSON size
                bson_size = sum(len(str(value)) for value in project_dict.values()) + 500  # Approximate size
                if bson_size > MAX_BSON_SIZE:
                    oversize_count += 1
                    accession = get_accession(project_dict)  # Extract accession ID
                    click.echo(
                        f"[{datetime.utcnow().isoformat()}] Oversized document ({bson_size} bytes), Accession: {accession}")

                    # Reduce the document to just ProjectID + `oversize: true`
                    reduced_doc = reduce_oversized_record(project_dict)
                    collection.insert_one(reduced_doc)

                else:
                    collection.insert_one(project_dict)
                    inserted_count += 1

                elem.clear()

            parent_stack.pop()

        if time.time() - start_time >= progress_interval:
            timestamp = datetime.utcnow().isoformat()
            click.echo(
                f"[{timestamp}] Inserted: {inserted_count}, Oversized (modified): {oversize_count}, Total Processed: {total_projects_processed}")
            start_time = time.time()

    click.echo(
        f"Final Summary: Inserted {inserted_count}, Oversized (modified) {oversize_count}, Total Processed: {total_projects_processed}")


@click.command()
@click.argument("xml_file", type=click.Path(exists=True))
@click.option("--mongo-uri", default="mongodb://localhost:27017/", help="MongoDB connection URI.")
@click.option("--db-name", default="ncbi_bioprojects", help="MongoDB database name.")
@click.option("--collection-name", default="projects", help="MongoDB collection name.")
@click.option("--progress-interval", default=10, type=int, help="Progress report interval in seconds.")
def main(xml_file, mongo_uri, db_name, collection_name, progress_interval):
    """Command-line interface to process and insert NCBI BioProject XML data into MongoDB with periodic progress updates."""
    parse_and_insert(xml_file, mongo_uri, db_name, collection_name, progress_interval)


if __name__ == "__main__":
    main()

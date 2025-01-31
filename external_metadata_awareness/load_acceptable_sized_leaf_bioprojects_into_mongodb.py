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


def remove_inner_projects(project_dict):
    """Removes inner `<Project>` nodes from `/PackageSet/Package/Project` before inserting into `submission`."""
    project_dict.pop("Project", None)  # Remove nested Project nodes
    return project_dict


def parse_and_insert(xml_file, mongo_uri, db_name, project_collection, submission_collection, progress_interval):
    """Parses an NCBI BioProject XML file and inserts both `/PackageSet/Package/Project/Project` and `/PackageSet/Package/Project` paths into MongoDB."""

    client = MongoClient(mongo_uri)
    db = client[db_name]
    project_col = db[project_collection]
    submission_col = db[submission_collection]

    context = ET.iterparse(xml_file, events=("start", "end"))
    parent_stack = []
    inserted_projects = 0
    inserted_submissions = 0
    oversize_projects = 0
    oversize_submissions = 0
    total_projects_processed = 0
    total_submissions_processed = 0
    start_time = time.time()

    for event, elem in context:
        if event == "start":
            parent_stack.append(elem.tag)

        elif event == "end":
            # Handle /PackageSet/Package/Project/Project (Project collection)
            if parent_stack[-1] == "Project" and len(parent_stack) >= 4 and parent_stack[-4:] == ["PackageSet",
                                                                                                  "Package", "Project",
                                                                                                  "Project"]:
                total_projects_processed += 1

                # Convert XML to dictionary using xmltodict
                project_dict = xmltodict.parse(ET.tostring(elem, encoding="utf-8"))

                # Get rid of root tag wrapping
                project_dict = project_dict.get("Project", {})

                # Clean field names
                project_dict = clean_dict(project_dict)

                if not project_dict:  # Skip empty projects
                    elem.clear()
                    parent_stack.pop()
                    continue

                # Estimate BSON size
                bson_size = sum(len(str(value)) for value in project_dict.values()) + 500
                if bson_size > MAX_BSON_SIZE:
                    oversize_projects += 1
                    accession = get_accession(project_dict)
                    click.echo(
                        f"[{datetime.utcnow().isoformat()}] Oversized project ({bson_size} bytes), Accession: {accession}")

                    # Store reduced record
                    reduced_doc = reduce_oversized_record(project_dict)
                    project_col.insert_one(reduced_doc)

                else:
                    project_col.insert_one(project_dict)
                    inserted_projects += 1

                elem.clear()

            # Handle /PackageSet/Package/Project (Submission collection)
            elif parent_stack[-1] == "Project" and len(parent_stack) >= 3 and parent_stack[-3:] == ["PackageSet",
                                                                                                    "Package",
                                                                                                    "Project"]:
                total_submissions_processed += 1

                # Convert XML to dictionary
                submission_dict = xmltodict.parse(ET.tostring(elem, encoding="utf-8"))

                # Get rid of root tag wrapping
                submission_dict = submission_dict.get("Project", {})

                # Clean field names
                submission_dict = clean_dict(submission_dict)

                # Remove inner <Project> nodes
                submission_dict = remove_inner_projects(submission_dict)

                if not submission_dict:  # Skip empty submissions
                    elem.clear()
                    parent_stack.pop()
                    continue

                # Estimate BSON size
                bson_size = sum(len(str(value)) for value in submission_dict.values()) + 500
                if bson_size > MAX_BSON_SIZE:
                    oversize_submissions += 1
                    accession = get_accession(submission_dict)
                    click.echo(
                        f"[{datetime.utcnow().isoformat()}] Oversized submission ({bson_size} bytes), Accession: {accession}")
                    # Do not insert oversized submission documents (per your request)
                else:
                    submission_col.insert_one(submission_dict)
                    inserted_submissions += 1

                elem.clear()

            parent_stack.pop()

        # Progress reporting
        if time.time() - start_time >= progress_interval:
            timestamp = datetime.utcnow().isoformat()
            click.echo(
                f"[{timestamp}] Projects Inserted: {inserted_projects}, Oversized Projects: {oversize_projects}, "
                f"Submissions Inserted: {inserted_submissions}, Oversized Submissions: {oversize_submissions}, "
                f"Total Processed: Projects={total_projects_processed}, Submissions={total_submissions_processed}")
            start_time = time.time()

    # Final summary
    click.echo(f"Final Summary: Projects Inserted {inserted_projects}, Oversized Projects {oversize_projects}, "
               f"Submissions Inserted {inserted_submissions}, Oversized Submissions {oversize_submissions}, "
               f"Total Processed: Projects={total_projects_processed}, Submissions={total_submissions_processed}")


@click.command()
@click.argument("xml_file", type=click.Path(exists=True))
@click.option("--mongo-uri", default="mongodb://localhost:27017/", help="MongoDB connection URI.")
@click.option("--db-name", default="ncbi_bioprojects", help="MongoDB database name.")
@click.option("--project-collection", default="projects",
              help="MongoDB collection for /PackageSet/Package/Project/Project.")
@click.option("--submission-collection", default="submissions",
              help="MongoDB collection for /PackageSet/Package/Project.")
@click.option("--progress-interval", default=10, type=int, help="Progress report interval in seconds.")
def main(xml_file, mongo_uri, db_name, project_collection, submission_collection, progress_interval):
    """CLI to process NCBI BioProject XML into MongoDB: both projects and submissions."""
    parse_and_insert(xml_file, mongo_uri, db_name, project_collection, submission_collection, progress_interval)


if __name__ == "__main__":
    main()

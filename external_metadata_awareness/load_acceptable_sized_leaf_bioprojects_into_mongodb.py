import click
import lxml.etree as ET
import xmltodict
import json
import os
from pymongo import MongoClient
import bson
import time
from datetime import datetime
from pathlib import Path

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


def get_submission_id(submission_dict):
    """Extracts the submission_id from the Submission node if present."""
    try:
        return submission_dict["Submission"]["submission_id"]
    except KeyError:
        return None  # No submission_id found


def get_project_id(project_dict):
    """Extracts the project ID from the ProjectID node if present."""
    try:
        archive_id = project_dict.get("ProjectID", {}).get("ArchiveID", {})
        accession = archive_id.get("accession")
        if accession:
            return accession
        return str(archive_id.get("id", "unknown"))
    except (KeyError, AttributeError):
        return "unknown"  # No ProjectID found


def ensure_dir_exists(directory):
    """Ensure a directory exists, creating it if necessary."""
    Path(directory).mkdir(parents=True, exist_ok=True)


def save_to_json_file(data, directory, filename):
    """Save data to a JSON file in the specified directory."""
    ensure_dir_exists(directory)
    filepath = os.path.join(directory, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return filepath


def parse_and_insert(xml_file, mongo_uri, db_name, project_collection, submission_collection, progress_interval, oversize_dir):
    """Parses an NCBI BioProject XML file and inserts both `/PackageSet/Package/Project/Project` and `/PackageSet/Package/Project` paths into MongoDB."""

    client = MongoClient(mongo_uri)
    db = client[db_name]
    project_col = db[project_collection]
    submission_col = db[submission_collection]
    
    # Ensure oversize directories exist
    oversize_project_dir = os.path.join(oversize_dir, "projects")
    oversize_submission_dir = os.path.join(oversize_dir, "submissions")
    ensure_dir_exists(oversize_project_dir)
    ensure_dir_exists(oversize_submission_dir)

    context = ET.iterparse(xml_file, events=("start", "end"))
    parent_stack = []
    inserted_projects = 0
    inserted_submissions = 0
    oversize_projects = 0
    oversize_submissions = 0
    total_projects_processed = 0
    total_submissions_processed = 0
    start_time = time.time()
    
    # Dictionary to track bioproject accessions for each package
    # Key: Package identifier (using element id or path)
    # Value: List of bioproject accessions
    package_bioprojects = {}
    current_package_id = None
    
    for event, elem in context:
        if event == "start":
            parent_stack.append(elem.tag)
            
            # When we start a new Package, create a new entry for tracking bioprojects
            if elem.tag == "Package" and len(parent_stack) == 2 and parent_stack[-2:] == ["PackageSet", "Package"]:
                current_package_id = elem.get("id", str(id(elem)))  # Use element's id attribute or object id
                package_bioprojects[current_package_id] = []

        elif event == "end":
            # Handle /PackageSet/Package/Project/Project (Project collection)
            if parent_stack[-1] == "Project" and len(parent_stack) >= 4 and parent_stack[-4:] == ["PackageSet",
                                                                                                 "Package", "Project",
                                                                                                 "Project"]:
                total_projects_processed += 1

                project_dict = xmltodict.parse(ET.tostring(elem, encoding="utf-8")).get("Project", {})
                project_dict = clean_dict(project_dict)

                if not project_dict:
                    elem.clear()
                    parent_stack.pop()
                    continue
                
                # Extract project accession and add to the package's list
                project_id = get_project_id(project_dict)
                if current_package_id and project_id != "unknown":
                    package_bioprojects[current_package_id].append(project_id)

                bson_size = sum(len(str(value)) for value in project_dict.values()) + 500
                if bson_size > MAX_BSON_SIZE:
                    oversize_projects += 1
                    
                    # Save oversized project to file
                    filename = f"project_{project_id}_{int(time.time())}.json"
                    saved_path = save_to_json_file(project_dict, oversize_project_dir, filename)
                    
                    # Insert reference to the file in MongoDB
                    project_col.insert_one({
                        "ProjectID": project_dict.get("ProjectID", {}),
                        "oversize": True,
                        "file_path": saved_path,
                        "size_bytes": bson_size
                    })
                    click.echo(f"[{datetime.utcnow().isoformat()}] Oversized project (ID: {project_id}), saved to {filename}")
                else:
                    project_col.insert_one(project_dict)
                    inserted_projects += 1

                elem.clear()

            # Handle /PackageSet/Package/Project (Submission collection)
            elif parent_stack[-1] == "Project" and len(parent_stack) >= 3 and parent_stack[-3:] == ["PackageSet",
                                                                                                   "Package",
                                                                                                   "Project"]:
                total_submissions_processed += 1

                submission_dict = xmltodict.parse(ET.tostring(elem, encoding="utf-8")).get("Project", {})
                submission_dict = clean_dict(submission_dict)

                if not submission_dict:
                    elem.clear()
                    parent_stack.pop()
                    continue
                
                # Add bioproject_accessions field to the submission document
                if current_package_id and current_package_id in package_bioprojects:
                    submission_dict["bioproject_accessions"] = package_bioprojects[current_package_id]

                bson_size = sum(len(str(value)) for value in submission_dict.values()) + 500
                if bson_size > MAX_BSON_SIZE:
                    oversize_submissions += 1
                    submission_id = get_submission_id(submission_dict)
                    
                    # Extract bioproject accessions for the reference document
                    bioproject_accessions = []
                    if current_package_id and current_package_id in package_bioprojects:
                        bioproject_accessions = package_bioprojects[current_package_id]

                    if submission_id:
                        # Save oversized submission to file
                        filename = f"submission_{submission_id}_{int(time.time())}.json"
                        saved_path = save_to_json_file(submission_dict, oversize_submission_dir, filename)
                        
                        # Insert reference to the file in MongoDB
                        submission_col.insert_one({
                            "submission_id": submission_id,
                            "bioproject_accessions": bioproject_accessions,
                            "oversize": True,
                            "file_path": saved_path,
                            "size_bytes": bson_size
                        })
                        click.echo(f"[{datetime.utcnow().isoformat()}] Oversized submission (ID: {submission_id}), saved to {filename}")
                    else:
                        # Even without submission_id, save the file with a timestamp
                        timestamp = int(time.time())
                        filename = f"submission_unknown_{timestamp}.json"
                        saved_path = save_to_json_file(submission_dict, oversize_submission_dir, filename)
                        
                        # Insert reference to the file in MongoDB
                        submission_col.insert_one({
                            "timestamp": timestamp,
                            "bioproject_accessions": bioproject_accessions,
                            "oversize": True,
                            "file_path": saved_path,
                            "size_bytes": bson_size
                        })
                        click.echo(f"[{datetime.utcnow().isoformat()}] Oversized submission without ID, saved to {filename}")
                else:
                    submission_col.insert_one(submission_dict)
                    inserted_submissions += 1

                elem.clear()
                
            # When a Package element ends, clean up its tracking entry to save memory
            elif elem.tag == "Package" and len(parent_stack) == 2 and parent_stack[-2:] == ["PackageSet", "Package"]:
                if current_package_id and current_package_id in package_bioprojects:
                    del package_bioprojects[current_package_id]
                current_package_id = None

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
@click.option("--oversize-dir", default="local/oversize", 
              help="Directory to save oversized projects and submissions.")
@click.option("--clear-collections", is_flag=True, default=False,
              help="Clear the project and submission collections before inserting new data.")
def main(xml_file, mongo_uri, db_name, project_collection, submission_collection, progress_interval, oversize_dir, clear_collections):
    """CLI to process NCBI BioProject XML into MongoDB: both projects and submissions.
    
    NOTE: This script does NOT clear collections by default! Use --clear-collections to drop
    the target collections before inserting new data, or manually clear them with:
    
    mongosh --eval "db.getSiblingDB('db_name').collection_name.drop()"
    """
    if clear_collections:
        client = MongoClient(mongo_uri)
        db = client[db_name]
        click.echo(f"Clearing collection: {project_collection}")
        db[project_collection].drop()
        click.echo(f"Clearing collection: {submission_collection}")
        db[submission_collection].drop()
        
    parse_and_insert(xml_file, mongo_uri, db_name, project_collection, submission_collection, progress_interval, oversize_dir)


if __name__ == "__main__":
    main()

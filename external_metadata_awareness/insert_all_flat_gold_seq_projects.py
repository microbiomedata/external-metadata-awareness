#!/usr/bin/env python
"""
Standalone Script for Flattening Gold Seq Projects

This script performs the following tasks:
  1. Connects to a MongoDB instance (database configurable via CLI).
     - Supports both authenticated and unauthenticated connections
     - Loads connection parameters from .env file if available
     - Allows override of connection parameters via command line arguments
     - Verifies connection and authentication status
  2. Clears the destination collections.
  3. Fetches seq_projects documents from the source collection.
  4. Flattens each document (ignoring complex fields like contacts, publications, experiments). This produces keys such as:
         projectGoldId, projectName, description, studyGoldId, biosampleGoldId, etc.
  5. Extracts seq_projects contacts, publications, and experiments.
  6. Inserts the processed seq_projects and related data into target collections.

Environment Variables (can be set in .env file):
  - MONGO_HOST: MongoDB server hostname (default: localhost)
  - MONGO_PORT: MongoDB server port (default: 27017)
  - MONGO_USERNAME: Username for MongoDB authentication (optional)
  - MONGO_PASSWORD: Password for MongoDB authentication (optional)
  - MONGO_AUTH_SOURCE: Authentication database (default: admin)
  - MONGO_DB: Target database name (default: gold_metadata)
"""

import json
import os
import click
from pymongo import MongoClient
from tqdm import tqdm
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs, urlunparse
from external_metadata_awareness.mongodb_connection import get_mongo_client

def parse_mongo_uri(uri):
    """
    Parse a MongoDB URI into its component parts.
    
    Args:
        uri: MongoDB URI string
        
    Returns:
        Dictionary containing parsed URI components (host, port, auth_source, etc.)
    """
    result = urlparse(uri)
    
    # Extract host and port
    host = result.hostname or "localhost"
    port = result.port or 27017
    
    # Extract database from path if present
    database = result.path.lstrip('/') if result.path else None
    
    # Extract query parameters
    query_params = parse_qs(result.query)
    
    # Get auth params, using the first value if there are multiple
    auth_source = query_params.get('authSource', ['admin'])[0] if 'authSource' in query_params else 'admin'
    auth_mechanism = query_params.get('authMechanism', [None])[0]
    direct_connection = query_params.get('directConnection', ['true'])[0].lower() == 'true' if 'directConnection' in query_params else True
    
    return {
        'host': host,
        'port': port,
        'database': database,
        'auth_source': auth_source,
        'auth_mechanism': auth_mechanism,
        'direct_connection': direct_connection
    }


# ------------------------------------------------------------
# Document flattening and cleaning functions
# ------------------------------------------------------------

def flatten_document(doc, known_skips=None):
    """
    Flattens a document by extracting scalar fields.
    Lists of scalars are joined with a pipe ('|').
    Dictionaries with all scalar values are flattened using dot-notation.
    """
    if known_skips is None:
        known_skips = set()
    scalar_doc = {}
    for key, value in doc.items():
        if key in known_skips:
            continue
        if isinstance(value, (str, int, float, bool)) or value is None:
            scalar_doc[key] = value
        elif isinstance(value, list) and all(
                isinstance(item, (str, int, float, bool)) or item is None for item in value):
            scalar_doc[key] = "|".join(map(str, value))
        elif isinstance(value, dict):
            if all(isinstance(v, (str, int, float, bool)) or v is None for v in value.values()):
                # Flatten each scalar key inside the dictionary
                for subkey, subval in value.items():
                    scalar_doc[f"{key}_{subkey}"] = subval
            else:
                scalar_doc[key] = json.dumps(value, sort_keys=True)
        else:
            scalar_doc[key] = str(value)
    return scalar_doc


def extract_gold_contacts_from_doc(doc, idcol):
    """
    Extracts contacts from a seq_projects document.
    """
    extracted = []
    record_id = doc.get(idcol)
    contacts = doc.get("contacts", [])
    for contact in contacts:
        if isinstance(contact, dict):
            entry = {
                idcol: record_id,
                "name": contact.get("name", ""),
                "email": contact.get("email", ""),
                "jgiSsoId": contact.get("jgiSsoId", ""),
                "roles": "|".join(sorted(contact.get("roles", [])))
            }
            extracted.append(entry)
    return extracted


def extract_publications_from_doc(doc, idcol):
    """
    Extracts publications from a seq_projects document.
    Handles both genomePublications and otherPublications arrays.
    """
    extracted = []
    record_id = doc.get(idcol)
    
    # Extract genome publications
    genome_pubs = doc.get("genomePublications", [])
    for pub in genome_pubs:
        if isinstance(pub, dict):
            entry = {
                idcol: record_id,
                "publication_type": "genome",
                "title": pub.get("title", ""),
                "authors": pub.get("authors", ""),
                "journal": pub.get("journal", ""),
                "doi": pub.get("doi", ""),
                "pmid": pub.get("pmid", ""),
                "year": pub.get("year", "")
            }
            extracted.append(entry)
    
    # Extract other publications
    other_pubs = doc.get("otherPublications", [])
    for pub in other_pubs:
        if isinstance(pub, dict):
            entry = {
                idcol: record_id,
                "publication_type": "other",
                "title": pub.get("title", ""),
                "authors": pub.get("authors", ""),
                "journal": pub.get("journal", ""),
                "doi": pub.get("doi", ""),
                "pmid": pub.get("pmid", ""),
                "year": pub.get("year", "")
            }
            extracted.append(entry)
    
    return extracted


def extract_experiments_from_doc(doc, idcol):
    """
    Extracts SRA experiments from a seq_projects document.
    """
    extracted = []
    record_id = doc.get(idcol)
    experiments = doc.get("sraExperiments", [])
    
    for exp in experiments:
        if isinstance(exp, dict):
            entry = {
                idcol: record_id,
                "sra_experiment_id": exp.get("experimentId", ""),
                "sra_run_id": exp.get("runId", ""),
                "platform": exp.get("platform", ""),
                "instrument": exp.get("instrument", ""),
                "library_strategy": exp.get("libraryStrategy", ""),
                "library_source": exp.get("librarySource", ""),
                "library_selection": exp.get("librarySelection", ""),
                "library_layout": exp.get("libraryLayout", ""),
                "spot_count": exp.get("spotCount", ""),
                "base_count": exp.get("baseCount", "")
            }
            extracted.append(entry)
    
    return extracted


# ------------------------------------------------------------
# Main function: Fetch, process, and insert documents
# ------------------------------------------------------------

@click.command()
@click.option('--mongo-uri', default=None, help='MongoDB URI (overrides individual connection params except username/password from .env)')
@click.option('--mongo-host', default=None, help='MongoDB host (overrides .env)')
@click.option('--mongo-port', default=None, type=int, help='MongoDB port (overrides .env)')
@click.option('--mongo-username', default=None, help='MongoDB username for authentication (overrides .env)')
@click.option('--mongo-password', default=None, help='MongoDB password for authentication (overrides .env)')
@click.option('--mongo-auth-source', default=None, help='MongoDB authentication source (overrides .env)')
@click.option('--db-name', default=None, help='MongoDB database name (overrides .env)')
@click.option('--source-collection', default='seq_projects', help='Source collection name')
@click.option('--target-collection', default='flattened_seq_projects', help='Target collection for flattened seq_projects')
@click.option('--contacts-collection', default='flattened_seq_projects_contacts', help='Target collection for contacts')
@click.option('--publications-collection', default='flattened_seq_projects_publications', help='Target collection for publications')
@click.option('--experiments-collection', default='flattened_seq_projects_experiments', help='Target collection for SRA experiments')
@click.option('--dotenv-path', default='local/.env', help='Path to .env file with MongoDB connection details')
def main(mongo_uri, mongo_host, mongo_port, mongo_username, mongo_password, mongo_auth_source, 
         db_name, source_collection, target_collection, contacts_collection, publications_collection, 
         experiments_collection, dotenv_path):
    """Flatten GOLD seq_projects from MongoDB."""
    
    # Load environment variables from .env file if it exists
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path=dotenv_path)
    
    # Get credentials from env file regardless of connection method
    env_username = os.getenv('MONGO_USERNAME')
    env_password = os.getenv('MONGO_PASSWORD')
    
    # Determine connection method (URI or individual parameters)
    if mongo_uri:
        # Parse URI to extract database if specified
        uri_parts = parse_mongo_uri(mongo_uri)
        
        # Use database from URI path if provided, otherwise from parameter or env
        if uri_parts['database'] and not db_name:
            db_name = uri_parts['database']
        else:
            db_name = db_name or os.getenv('MONGO_DB', 'gold_metadata')
        
        # Print connection information
        print(f"Using MongoDB URI: {mongo_uri}")
        
        # Connect using the imported get_mongo_client function
        client = get_mongo_client(
            mongo_uri=mongo_uri,
            env_file=dotenv_path if os.path.exists(dotenv_path) else None,
            debug=True
        )
    else:
        # Construct a MongoDB URI from individual components
        mongo_host = mongo_host or os.getenv('MONGO_HOST', 'localhost')
        mongo_port = mongo_port or int(os.getenv('MONGO_PORT', '27017'))
        db_name = db_name or os.getenv('MONGO_DB', 'gold_metadata')
        
        # Construct the URI
        constructed_uri = f"mongodb://{mongo_host}:{mongo_port}/{db_name}"
        
        print(f"Using constructed MongoDB URI: {constructed_uri}")
        
        # Connect using the imported get_mongo_client function
        client = get_mongo_client(
            mongo_uri=constructed_uri,
            env_file=dotenv_path if os.path.exists(dotenv_path) else None,
            debug=True
        )
    
    print(f"Using database: {db_name}")
    
    # Verify connection
    try:
        # Run a simple command to verify connection
        server_info = client.server_info()
        print(f"Connected to MongoDB server version: {server_info.get('version', 'unknown')}")
        
        # Check if authentication is active
        user_info = client[mongo_auth_source].command('connectionStatus')
        if user_info.get('authInfo', {}).get('authenticatedUsers'):
            authenticated_user = user_info['authInfo']['authenticatedUsers'][0]['user']
            print(f"Authenticated as user: {authenticated_user}")
        else:
            print("Connected without authentication")
    except Exception as e:
        print(f"Warning: {e}")
        print("Continuing with connection attempt...")
    
    db = client[db_name]

    # Define source and target collections
    seq_projects_collection = db[source_collection]
    flattened_seq_projects_collection = db[target_collection]
    flattened_seq_projects_contacts_collection = db[contacts_collection]
    flattened_seq_projects_publications_collection = db[publications_collection]
    flattened_seq_projects_experiments_collection = db[experiments_collection]

    # Clear destination collections before starting
    print("Clearing destination collections...")
    flattened_seq_projects_collection.drop()
    flattened_seq_projects_contacts_collection.drop()
    flattened_seq_projects_publications_collection.drop()
    flattened_seq_projects_experiments_collection.drop()

    # --- Fetch seq_projects documents ---
    print(f"Starting to fetch seq_projects from the {source_collection} collection...")
    total_docs = seq_projects_collection.count_documents({})
    seq_projects = []
    for doc in tqdm(seq_projects_collection.find(), total=total_docs, desc="Fetching seq_projects"):
        # Exclude the MongoDB internal _id field
        seq_projects.append({k: v for k, v in doc.items() if k != '_id'})

    # --- Flatten and clean each seq_project ---
    print("Flattening and cleaning seq_projects...")
    flattened_seq_projects = []
    known_skips = {'contacts', 'genomePublications', 'otherPublications', 'sraExperiments'}
    for doc in tqdm(seq_projects, desc="Processing seq_projects"):
        flat_doc = flatten_document(doc, known_skips=known_skips)
        flattened_seq_projects.append(flat_doc)

    # --- Extract seq_projects contacts ---
    print("Extracting seq_projects contacts...")
    flattened_contacts = []
    for doc in tqdm(seq_projects, desc="Extracting contacts"):
        contacts = extract_gold_contacts_from_doc(doc, "projectGoldId")
        flattened_contacts.extend(contacts)
    print(f"Contacts extraction complete. Total contacts extracted: {len(flattened_contacts)}")

    # --- Extract seq_projects publications ---
    print("Extracting seq_projects publications...")
    flattened_publications = []
    for doc in tqdm(seq_projects, desc="Extracting publications"):
        publications = extract_publications_from_doc(doc, "projectGoldId")
        flattened_publications.extend(publications)
    print(f"Publications extraction complete. Total publications extracted: {len(flattened_publications)}")

    # --- Extract seq_projects experiments ---
    print("Extracting seq_projects SRA experiments...")
    flattened_experiments = []
    for doc in tqdm(seq_projects, desc="Extracting experiments"):
        experiments = extract_experiments_from_doc(doc, "projectGoldId")
        flattened_experiments.extend(experiments)
    print(f"Experiments extraction complete. Total experiments extracted: {len(flattened_experiments)}")

    # --- Insert processed documents into target collections ---
    print("Starting insertion of processed documents...")
    print(f"Inserting {len(flattened_seq_projects)} flattened seq_projects...")
    if flattened_seq_projects:
        flattened_seq_projects_collection.insert_many(flattened_seq_projects)
    print(f"Flattened seq_projects insertion complete into {target_collection} collection.")

    print(f"Inserting {len(flattened_contacts)} flattened contacts...")
    if flattened_contacts:
        flattened_seq_projects_contacts_collection.insert_many(flattened_contacts)
    print(f"Flattened contacts insertion complete into {contacts_collection} collection.")

    print(f"Inserting {len(flattened_publications)} flattened publications...")
    if flattened_publications:
        flattened_seq_projects_publications_collection.insert_many(flattened_publications)
    print(f"Flattened publications insertion complete into {publications_collection} collection.")

    print(f"Inserting {len(flattened_experiments)} flattened experiments...")
    if flattened_experiments:
        flattened_seq_projects_experiments_collection.insert_many(flattened_experiments)
    print(f"Flattened experiments insertion complete into {experiments_collection} collection.")

    print(f"Gold seq_projects flattening completed. Documents inserted into MongoDB collections:")
    print(f"  - {target_collection}")
    print(f"  - {contacts_collection}")
    print(f"  - {publications_collection}")
    print(f"  - {experiments_collection}")


if __name__ == "__main__":
    main()
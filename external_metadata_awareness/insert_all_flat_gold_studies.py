#!/usr/bin/env python
"""
Standalone Script for Flattening Gold Studies

This script performs the following tasks:
  1. Connects to a MongoDB instance (database configurable via CLI).
     - Supports both authenticated and unauthenticated connections
     - Loads connection parameters from .env file if available
     - Allows override of connection parameters via command line arguments
     - Verifies connection and authentication status
  2. Clears the destination collections.
  3. Fetches study documents from the source collection.
  4. Flattens each document (ignoring complex fields like contacts). This produces keys such as:
         studyGoldId, studyName, description, modDate, addDate, etc.
  5. Extracts study contacts.
  6. Inserts the processed studies and contacts into target collections.

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
    Extracts contacts from a study document.
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
@click.option('--source-collection', default='studies', help='Source collection name')
@click.option('--target-collection', default='flattened_studies', help='Target collection for flattened studies')
@click.option('--contacts-collection', default='flattened_studies_contacts', help='Target collection for contacts')
@click.option('--dotenv-path', default='local/.env', help='Path to .env file with MongoDB connection details')
def main(mongo_uri, mongo_host, mongo_port, mongo_username, mongo_password, mongo_auth_source, 
         db_name, source_collection, target_collection, contacts_collection, dotenv_path):
    """Flatten GOLD studies from MongoDB."""
    
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
    studies_collection = db[source_collection]
    flattened_studies_collection = db[target_collection]
    flattened_studies_contacts_collection = db[contacts_collection]

    # Clear destination collections before starting
    print("Clearing destination collections...")
    flattened_studies_collection.drop()
    flattened_studies_contacts_collection.drop()

    # --- Fetch study documents ---
    print(f"Starting to fetch studies from the {source_collection} collection...")
    total_docs = studies_collection.count_documents({})
    studies = []
    for doc in tqdm(studies_collection.find(), total=total_docs, desc="Fetching studies"):
        # Exclude the MongoDB internal _id field
        studies.append({k: v for k, v in doc.items() if k != '_id'})

    # --- Flatten and clean each study ---
    print("Flattening and cleaning studies...")
    flattened_studies = []
    for doc in tqdm(studies, desc="Processing studies"):
        flat_doc = flatten_document(doc, known_skips={'contacts'})
        flattened_studies.append(flat_doc)

    # --- Extract study contacts ---
    print("Extracting study contacts...")
    flattened_contacts = []
    for doc in tqdm(studies, desc="Extracting contacts"):
        contacts = extract_gold_contacts_from_doc(doc, "studyGoldId")
        flattened_contacts.extend(contacts)
    print(f"Contacts extraction complete. Total contacts extracted: {len(flattened_contacts)}")

    # --- Insert processed documents into target collections ---
    print("Starting insertion of processed documents...")
    print(f"Inserting {len(flattened_studies)} flattened studies...")
    if flattened_studies:
        flattened_studies_collection.insert_many(flattened_studies)
    print(f"Flattened studies insertion complete into {target_collection} collection.")

    print(f"Inserting {len(flattened_contacts)} flattened contacts...")
    if flattened_contacts:
        flattened_studies_contacts_collection.insert_many(flattened_contacts)
    print(f"Flattened contacts insertion complete into {contacts_collection} collection.")

    print(f"Gold studies flattening completed. Documents inserted into MongoDB collections:")
    print(f"  - {target_collection}")
    print(f"  - {contacts_collection}")


if __name__ == "__main__":
    main()
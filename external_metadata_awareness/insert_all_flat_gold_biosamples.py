#!/usr/bin/env python
"""
Standalone Script for Flattening and Decorating Gold Biosamples

This script performs the following tasks:
  1. Connects to a MongoDB instance (database configurable via CLI).
     - Supports both authenticated and unauthenticated connections
     - Loads connection parameters from .env file if available
     - Allows override of connection parameters via command line arguments
     - Verifies connection and authentication status
  2. Loads ontology adapters for "envo", "pato", and "uberon" to build a label cache and obsolete terms list.
  3. Clears the destination collections.
  4. Fetches biosample documents from the source collection.
  5. Flattens each document (ignoring complex fields like contacts). This produces keys such as:
         envoBroadScale.id, envoBroadScale.label,
         envoLocalScale.id, envoLocalScale.label,
         envoMedium.id, envoMedium.label, etc.
  6. Removes uninformative root keys (e.g. "envoBroadScale", "envoLocalScale", "envoMedium", "longhurst").
  7. Decorates environmental fields by:
         - Converting the input IDs by replacing "_" with ":" (e.g. "ENVO_01000339" → "ENVO:01000339")
         - Looking up the canonical label from the ontology label cache
         - Flagging obsolete terms
         - Writing out MIxS‑style decorated keys:
               • env_broad_scale_canonical_curie
               • env_broad_scale_canonical_label
               • env_broad_scale_obsolete
               • env_broad_scale_labels_equivalent
         (and similarly for env_local_scale and env_medium)
  8. Extracts biosample contacts.
  9. Inserts the processed biosamples and contacts into target collections.

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
from oaklib import get_adapter
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

# Using the imported get_mongo_client function instead of this local definition


# ------------------------------------------------------------
# Ontology setup functions
# ------------------------------------------------------------

def build_ontology_adapters(ontology_names):
    """Creates ontology adapters for the provided list of ontology names."""
    return {ontology: get_adapter(f"sqlite:obo:{ontology}") for ontology in ontology_names}


def generate_label_cache(entities, adapter):
    """Builds a cache mapping CURIEs to their labels."""
    label_cache = {}
    for curie in entities:
        label = adapter.label(curie)
        if label:
            label_cache[curie] = label
    return label_cache


def load_ontology_labels(ontology_adapters):
    """Aggregates label caches from all provided ontology adapters."""
    aggregated_label_cache = {}
    for ontology, adapter in ontology_adapters.items():
        entities = sorted(list(adapter.entities()))
        label_cache = generate_label_cache(entities, adapter)
        aggregated_label_cache.update(label_cache)
    return aggregated_label_cache


def find_obsolete_terms(ontology_adapters):
    """Aggregates obsolete term CURIEs from all ontology adapters."""
    obsolete_curies = []
    for adapter in ontology_adapters.values():
        obsolete_curies.extend(adapter.obsoletes())
    return obsolete_curies


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


def remove_root_keys(flat_doc, keys_to_remove):
    """
    Removes keys from a flattened document that are not needed,
    such as the parent object keys ("envoBroadScale", "envoLocalScale", etc.)
    """
    for key in keys_to_remove:
        if key in flat_doc:
            del flat_doc[key]
    return flat_doc


# ------------------------------------------------------------
# Decoration function
# ------------------------------------------------------------

def decorate_env_fields(sample, label_cache, obsolete_terms_list):
    """
    Decorates environmental fields using MIxS‑style naming.

    It reads the following flattened input fields:
      - envoBroadScale.id and envoBroadScale.label
      - envoLocalScale.id and envoLocalScale.label
      - envoMedium.id and envoMedium.label

    For each, it:
      • Converts the input id by replacing '_' with ':' to get a canonical CURIE.
      • Looks up the canonical label using the ontology label cache.
      • Flags obsolete status (True if the canonical CURIE is in the obsolete list, else False).
      • Determines whether the original label equals the canonical label.

    The decorated MIxS‑style keys written out are:
      - env_broad_scale_canonical_curie
      - env_broad_scale_canonical_label
      - env_broad_scale_obsolete
      - env_broad_scale_labels_equivalent
      (and similarly for env_local_scale and env_medium)
    """
    # Broad Scale
    broad_id = sample.get("envoBroadScale_id")
    broad_label = sample.get("envoBroadScale_label")
    if broad_id:
        canonical_curie = broad_id.replace('_', ':')
        sample["env_broad_scale_canonical_curie"] = canonical_curie
        # Use the canonical label from the ontology, or fallback to the original label
        sample["env_broad_scale_canonical_label"] = label_cache.get(canonical_curie, broad_label)
        sample["env_broad_scale_obsolete"] = canonical_curie in obsolete_terms_list
        sample["env_broad_scale_labels_equivalent"] = (broad_label == sample["env_broad_scale_canonical_label"])
    else:
        sample["env_broad_scale_canonical_curie"] = None
        sample["env_broad_scale_canonical_label"] = None
        sample["env_broad_scale_obsolete"] = None
        sample["env_broad_scale_labels_equivalent"] = None

    # Local Scale
    local_id = sample.get("envoLocalScale_id")
    local_label = sample.get("envoLocalScale_label")
    if local_id:
        canonical_curie = local_id.replace('_', ':')
        sample["env_local_scale_canonical_curie"] = canonical_curie
        sample["env_local_scale_canonical_label"] = label_cache.get(canonical_curie, local_label)
        sample["env_local_scale_obsolete"] = canonical_curie in obsolete_terms_list
        sample["env_local_scale_labels_equivalent"] = (local_label == sample["env_local_scale_canonical_label"])
    else:
        sample["env_local_scale_canonical_curie"] = None
        sample["env_local_scale_canonical_label"] = None
        sample["env_local_scale_obsolete"] = None
        sample["env_local_scale_labels_equivalent"] = None

    # Medium
    medium_id = sample.get("envoMedium_id")
    medium_label = sample.get("envoMedium_label")
    if medium_id:
        canonical_curie = medium_id.replace('_', ':')
        sample["env_medium_canonical_curie"] = canonical_curie
        sample["env_medium_canonical_label"] = label_cache.get(canonical_curie, medium_label)
        sample["env_medium_obsolete"] = canonical_curie in obsolete_terms_list
        sample["env_medium_labels_equivalent"] = (medium_label == sample["env_medium_canonical_label"])
    else:
        sample["env_medium_canonical_curie"] = None
        sample["env_medium_canonical_label"] = None
        sample["env_medium_obsolete"] = None
        sample["env_medium_labels_equivalent"] = None


def extract_gold_contacts_from_doc(doc, idcol):
    """
    Extracts contacts from a biosample document.
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
@click.option('--source-collection', default='biosamples', help='Source collection name')
@click.option('--target-collection', default='flattened_biosamples', help='Target collection for flattened biosamples')
@click.option('--contacts-collection', default='flattened_biosample_contacts', help='Target collection for contacts')
@click.option('--dotenv-path', default='local/.env', help='Path to .env file with MongoDB connection details')
def main(mongo_uri, mongo_host, mongo_port, mongo_username, mongo_password, mongo_auth_source, 
         db_name, source_collection, target_collection, contacts_collection, dotenv_path):
    """Flatten and decorate GOLD biosamples from MongoDB."""
    
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
    biosamples_collection = db[source_collection]
    flattened_biosamples_collection = db[target_collection]
    flattened_biosample_contacts_collection = db[contacts_collection]

    # Clear destination collections before starting
    print("Clearing destination collections...")
    flattened_biosamples_collection.drop()
    flattened_biosample_contacts_collection.drop()

    # --- Setup ontology adapters and build decoration data ---
    print("Setting up ontology adapters and building label cache...")
    ontology_list = ["envo", "pato", "uberon"]
    ontology_adapters = build_ontology_adapters(ontology_list)
    label_cache = load_ontology_labels(ontology_adapters)
    obsolete_terms_list = find_obsolete_terms(ontology_adapters)

    # --- Fetch biosample documents ---
    print(f"Starting to fetch biosamples from the {source_collection} collection...")
    total_docs = biosamples_collection.count_documents({})
    biosamples = []
    for doc in tqdm(biosamples_collection.find(), total=total_docs, desc="Fetching biosamples"):
        # Exclude the MongoDB internal _id field
        biosamples.append({k: v for k, v in doc.items() if k != '_id'})

    # --- Flatten and clean each biosample ---
    print("Flattening and cleaning biosamples...")
    flattened_biosamples = []
    # Define root keys to remove from the flattened output
    keys_to_remove = {"envoBroadScale", "envoLocalScale", "envoMedium", "longhurst"}
    for doc in tqdm(biosamples, desc="Processing biosamples"):
        flat_doc = flatten_document(doc, known_skips={'contacts'})
        # Remove blank parent keys (e.g. "envoBroadScale")
        flat_doc = remove_root_keys(flat_doc, keys_to_remove)
        # Decorate environmental fields using the flattened keys
        decorate_env_fields(flat_doc, label_cache, obsolete_terms_list)
        flattened_biosamples.append(flat_doc)

    # --- Extract biosample contacts ---
    print("Extracting biosample contacts...")
    flattened_contacts = []
    for doc in tqdm(biosamples, desc="Extracting contacts"):
        contacts = extract_gold_contacts_from_doc(doc, "biosampleGoldId")
        flattened_contacts.extend(contacts)
    print(f"Contacts extraction complete. Total contacts extracted: {len(flattened_contacts)}")

    # --- Insert processed documents into target collections ---
    print("Starting insertion of processed documents...")
    print(f"Inserting {len(flattened_biosamples)} flattened biosamples...")
    if flattened_biosamples:
        flattened_biosamples_collection.insert_many(flattened_biosamples)
    print(f"Flattened biosamples insertion complete into {target_collection} collection.")

    print(f"Inserting {len(flattened_contacts)} flattened contacts...")
    if flattened_contacts:
        flattened_biosample_contacts_collection.insert_many(flattened_contacts)
    print(f"Flattened contacts insertion complete into {contacts_collection} collection.")

    print(f"Gold biosample flattening and decoration completed. Documents inserted into MongoDB collections:")
    print(f"  - {target_collection}")
    print(f"  - {contacts_collection}")


if __name__ == "__main__":
    main()
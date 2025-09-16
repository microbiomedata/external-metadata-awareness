#!/usr/bin/env python
"""
Export Flattened GOLD Collections to CSV

This script exports all flattened_* collections from a GOLD MongoDB database to CSV files.
It automatically discovers collections with the "flattened_" prefix and exports each to a
corresponding CSV file.

The script performs the following tasks:
  1. Connects to a MongoDB instance (database configurable via CLI).
  2. Discovers all collections starting with "flattened_"
  3. Exports each collection to a CSV file in the specified output directory
  4. Handles data type conversion for CSV compatibility

Environment Variables (can be set in .env file):
  - MONGO_HOST: MongoDB server hostname (default: localhost)
  - MONGO_PORT: MongoDB server port (default: 27017)
  - MONGO_USERNAME: Username for MongoDB authentication (optional)
  - MONGO_PASSWORD: Password for MongoDB authentication (optional)
  - MONGO_AUTH_SOURCE: Authentication database (default: admin)
  - MONGO_DB: Target database name (default: gold_metadata)
"""

import os
import csv
import click
import pandas as pd
from pymongo import MongoClient
from tqdm import tqdm
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs
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


def export_collection_to_csv(collection, output_file, batch_size=10000):
    """
    Export a MongoDB collection to CSV file using pandas for efficient processing.
    
    Args:
        collection: MongoDB collection object
        output_file: Path to output CSV file
        batch_size: Number of documents to process in each batch
    """
    total_docs = collection.count_documents({})
    
    if total_docs == 0:
        print(f"Collection {collection.name} is empty, skipping...")
        return
    
    print(f"Exporting {total_docs} documents from {collection.name} to {output_file}")
    
    # Initialize CSV writer
    first_batch = True
    
    # Process documents in batches
    for skip in tqdm(range(0, total_docs, batch_size), desc=f"Exporting {collection.name}"):
        # Fetch batch of documents
        cursor = collection.find({}).skip(skip).limit(batch_size)
        docs = list(cursor)
        
        if not docs:
            break
            
        # Convert to DataFrame
        df = pd.DataFrame(docs)
        
        # Remove MongoDB _id field if present
        if '_id' in df.columns:
            df = df.drop('_id', axis=1)
        
        # Write to CSV
        if first_batch:
            df.to_csv(output_file, index=False, mode='w')
            first_batch = False
        else:
            df.to_csv(output_file, index=False, mode='a', header=False)


@click.command()
@click.option('--mongo-uri', default=None, help='MongoDB URI (overrides individual connection params except username/password from .env)')
@click.option('--mongo-host', default=None, help='MongoDB host (overrides .env)')
@click.option('--mongo-port', default=None, type=int, help='MongoDB port (overrides .env)')
@click.option('--mongo-username', default=None, help='MongoDB username for authentication (overrides .env)')
@click.option('--mongo-password', default=None, help='MongoDB password for authentication (overrides .env)')
@click.option('--mongo-auth-source', default=None, help='MongoDB authentication source (overrides .env)')
@click.option('--db-name', default=None, help='MongoDB database name (overrides .env)')
@click.option('--output-dir', default='local/csv_exports', help='Output directory for CSV files')
@click.option('--collection-prefix', default='flattened_', help='Collection name prefix to filter for export')
@click.option('--batch-size', default=10000, type=int, help='Batch size for processing large collections')
@click.option('--dotenv-path', default='local/.env', help='Path to .env file with MongoDB connection details')
def main(mongo_uri, mongo_host, mongo_port, mongo_username, mongo_password, mongo_auth_source, 
         db_name, output_dir, collection_prefix, batch_size, dotenv_path):
    """Export all flattened GOLD collections from MongoDB to CSV files."""
    
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
        user_info = client[mongo_auth_source or 'admin'].command('connectionStatus')
        if user_info.get('authInfo', {}).get('authenticatedUsers'):
            authenticated_user = user_info['authInfo']['authenticatedUsers'][0]['user']
            print(f"Authenticated as user: {authenticated_user}")
        else:
            print("Connected without authentication")
    except Exception as e:
        print(f"Warning: {e}")
        print("Continuing with connection attempt...")
    
    db = client[db_name]
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    print(f"CSV files will be saved to: {output_dir}")
    
    # Discover collections with the specified prefix
    all_collections = db.list_collection_names()
    target_collections = [name for name in all_collections if name.startswith(collection_prefix)]
    
    if not target_collections:
        print(f"No collections found with prefix '{collection_prefix}' in database '{db_name}'")
        return
    
    print(f"Found {len(target_collections)} collections to export:")
    for collection_name in target_collections:
        print(f"  - {collection_name}")
    
    # Export each collection to CSV
    for collection_name in target_collections:
        collection = db[collection_name]
        output_file = os.path.join(output_dir, f"{collection_name}.csv")
        
        try:
            export_collection_to_csv(collection, output_file, batch_size)
            print(f"✓ Successfully exported {collection_name} to {output_file}")
        except Exception as e:
            print(f"✗ Error exporting {collection_name}: {e}")
    
    print(f"\nCSV export completed. Files saved in: {output_dir}")


if __name__ == "__main__":
    main()
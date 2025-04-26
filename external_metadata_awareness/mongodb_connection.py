import os
import sys
import argparse
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse
from dotenv import load_dotenv
import pymongo


def get_mongo_client(
        mongo_uri: str,
        env_file: Optional[str] = None,
        debug: bool = False,
        dry_run: bool = False
) -> pymongo.MongoClient:
    """
    Establishes a connection to a MongoDB server using a URI and optional credentials from env file.
    
    This simplified version only uses the provided URI and extracts credentials from the env file.
    All connection details (host, port, database name, options) must be included in the URI.

    Args:
        mongo_uri: MongoDB connection URI string (required, must include host/port/database)
        env_file: Path to .env file to load credentials from
        debug: Print debug information about the connection
        dry_run: If True, don't actually connect, just return connection info

    Returns:
        A pymongo.MongoClient instance or connection info dict if dry_run=True
    """
    if not mongo_uri:
        raise ValueError("mongo_uri is required")
    
    if not mongo_uri.startswith("mongodb://"):
        raise ValueError("MongoDB URI must start with 'mongodb://'")
    
    # Check if URI has a database name
    parsed = urlparse(mongo_uri)
    if not parsed.path or parsed.path == "/":
        raise ValueError("MongoDB URI must include a database name (mongodb://host:port/database)")
    
    # Create a copy of the URI that we might modify
    final_uri = mongo_uri
    
    # Load credentials from env file if provided
    if env_file and Path(env_file).exists():
        load_dotenv(env_file, override=True)
        if debug:
            print(f"Loaded .env file from {env_file}")
        
        username = os.getenv("MONGO_USER")
        password = os.getenv("MONGO_PASSWORD")
        
        if username and password:
            # If URI already has credentials, we'll replace them
            if "@" in final_uri:
                protocol, rest = final_uri.split("://", 1)
                _, after_auth = rest.split("@", 1)
                final_uri = f"{protocol}://{username}:{password}@{after_auth}"
            else:
                # No auth part, add it
                protocol, rest = final_uri.split("://", 1)
                final_uri = f"{protocol}://{username}:{password}@{rest}"
                
            if debug:
                username_preview = username
                if len(username_preview) > 4:
                    username_preview = f"{username_preview[:2]}...{username_preview[-2:]}"
                print(f"Loaded credentials from .env file - Username: {username_preview}")
    
    # Create a masked URI for debug output
    masked_uri = final_uri
    if "@" in final_uri:
        protocol, rest = final_uri.split("://", 1)
        _, after_auth = rest.split("@", 1)
        masked_uri = f"{protocol}://[credentials_masked]@{after_auth}"
    
    if debug:
        print(f"Final connection URI: {masked_uri}")
    
    # For dry runs, return connection info instead of a client
    if dry_run:
        return {
            "uri": masked_uri,
            "has_credentials": "@" in final_uri,
        }
    
    # Create the MongoDB client
    client = pymongo.MongoClient(final_uri)
    
    # Verify connection information
    if debug:
        print(f"MongoDB client address: {client.address}")
    
    return client


def main():
    """Command-line interface for testing MongoDB connection parameters."""
    parser = argparse.ArgumentParser(description="Test MongoDB connection using a URI and optional env file")
    parser.add_argument("--uri", required=True, help="MongoDB connection URI (must start with mongodb:// and include database name)")
    parser.add_argument("--env-file", help="Path to .env file for credentials (should contain MONGO_USER and MONGO_PASSWORD)")
    parser.add_argument("--verbose", action="store_true", help="Show verbose output")
    parser.add_argument("--connect", action="store_true", help="Actually connect to the database")
    args = parser.parse_args()
    
    try:
        # Get connection info in dry-run mode
        result = get_mongo_client(
            mongo_uri=args.uri,
            env_file=args.env_file,
            debug=args.verbose,
            dry_run=not args.connect
        )
        
        if not args.connect:
            # Show minimal connection info
            print(f"Final connection URI: {result['uri']}")
            print(f"Using credentials: {result['has_credentials']}")
        else:
            # Actually try to connect
            print("Testing connection...")
            # Get database name from URI
            parsed = urlparse(args.uri)
            db_name = parsed.path.lstrip("/").split("?")[0]
            
            # List collections in the database
            db = result[db_name]
            print(f"Connected to database: {db.name}")
            print(f"Collections: {db.list_collection_names()}")
            print("Connection test successful!")
    
    except ValueError as e:
        print(f"Error: {e}")
        print("\nThe MongoDB URI must use the format: mongodb://host[:port]/database[?options]")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

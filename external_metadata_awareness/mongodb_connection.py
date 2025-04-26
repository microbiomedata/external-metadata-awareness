import os
import sys
import re
import argparse
import json
import subprocess
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
import pymongo
from pymongo import uri_parser


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
    try:
        parsed = uri_parser.parse_uri(mongo_uri)
        if not parsed.get('database'):
            raise ValueError("MongoDB URI must include a database name (mongodb://host:port/database)")
    except pymongo.errors.InvalidURI:
        raise ValueError("Invalid MongoDB URI format")
    
    # Create a copy of the URI that we might modify
    final_uri = mongo_uri
    
    # Load credentials from env file if provided
    if env_file:
        if not Path(env_file).exists():
            raise ValueError(f"Error: .env file not found at {env_file}")
            
        load_dotenv(env_file, override=True)
        if debug:
            print(f"Loaded .env file from {env_file}")
        
        username = os.getenv("MONGO_USER")
        password = os.getenv("MONGO_PASSWORD")
        
        # Only use credentials if both username and password are provided
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
                print(f"Loaded credentials from .env file - Username: {username}")
        else:
            if debug:
                print("No credentials found in .env file, continuing with unauthenticated connection")
    
    # Display the full URI with credentials for debug output
    if debug:
        print(f"Final connection URI: {final_uri}")
    
    # For dry runs, return connection info instead of a client
    if dry_run:
        return {
            "uri": final_uri,
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
    parser.add_argument("--command", help="MongoDB command to execute (must be valid JavaScript/MongoDB shell command)")
    args = parser.parse_args()
    
    try:
        # Get connection info in dry-run mode if not connecting
        if not args.connect and not args.command:
            result = get_mongo_client(
                mongo_uri=args.uri,
                env_file=args.env_file,
                debug=args.verbose,
                dry_run=True
            )
            
            # Show minimal connection info without duplicating the output from get_mongo_client
            if not args.verbose:
                print(f"Final connection URI: {result['uri']}")
            print(f"Using credentials: {result['has_credentials']}")
            
            # Show a sample mongosh command with the full URI including credentials
            print("\nSample mongosh command:")
            print(f'mongosh "{result["uri"]}"')
        else:
            # Actually connect to the database
            client = get_mongo_client(
                mongo_uri=args.uri,
                env_file=args.env_file,
                debug=args.verbose
            )
            
            # Extract database name from URI
            parsed = uri_parser.parse_uri(args.uri)
            db_name = parsed.get('database')
            
            if not db_name:
                raise ValueError("MongoDB URI must include a database name")
                
            db = client[db_name]
            
            if args.command:
                # Execute command
                print(f"Executing command: {args.command}")
                
                # Parse MongoDB shell commands directly
                # Example: db.collection.createIndex({ field: 1 })
                index_match = re.match(r'db\.(\w+)\.createIndex\((.*)\)', args.command)
                
                if index_match:
                    collection_name = index_match.group(1)
                    index_spec_str = index_match.group(2)
                    
                    try:
                        # Try to execute createIndex command directly with PyMongo
                        collection = db[collection_name]
                        
                        # This is a simplified approach - we're executing the Python equivalent
                        # of the MongoDB shell command. For complex index specs, we might need
                        # more sophisticated parsing.
                        
                        # Convert JavaScript/MongoDB shell object notation to Python dict
                        # First, replace JavaScript-style keys without quotes with Python-style keys with quotes
                        index_spec_str = re.sub(r'(\s*)(\w+):', r'\1"\2":', index_spec_str)
                        
                        # Replace 'true' with 'True' and 'false' with 'False' for Python compatibility
                        index_spec_str = index_spec_str.replace('true', 'True').replace('false', 'False')
                        
                        # Check if this is a complex index with options like {unique: true}
                        complex_index_match = re.match(r'(\{[^}]+\})\s*,\s*(\{.+\})', index_spec_str)
                        
                        if complex_index_match:
                            # We have both keys and options
                            keys_str = complex_index_match.group(1)
                            options_str = complex_index_match.group(2)
                            
                            # Parse the keys
                            keys_dict = eval(f"dict({keys_str})")
                            keys = [(k, v) for k, v in keys_dict.items()]
                            
                            # Parse the options
                            options = eval(f"dict({options_str})")
                            
                            # Create the index with options
                            result = collection.create_index(keys, **options)
                        else:
                            # Simple index without options
                            index_spec = eval(f"dict({index_spec_str})")
                            result = collection.create_index([(k, v) for k, v in index_spec.items()])
                        
                        # Log the result
                        print(f"Created index: {result}")
                    except Exception as e:
                        print(f"Error creating index: {e}")
                        raise
                
                # Add other command patterns here as needed
                
                else:
                    # Try using mongosh directly as a fallback for unsupported command patterns
                    try:
                        print("Attempting to execute command with mongosh...")
                        
                        # Get the URI with credentials if any
                        final_uri = args.uri
                        credentials_text = ""
                        if "@" in final_uri:
                            credentials_text = " (with credentials)"
                        
                        # Run the command with mongosh
                        cmd = ["mongosh", final_uri, "--eval", args.command]
                        result = subprocess.run(cmd, capture_output=True, text=True)
                        
                        if result.returncode == 0:
                            print(f"Command executed successfully via mongosh{credentials_text}")
                            if result.stdout.strip():
                                print(result.stdout)
                        else:
                            print(f"Error executing via mongosh: {result.stderr}")
                            raise ValueError(f"mongosh execution failed: {result.stderr}")
                    except Exception as e:
                        print(f"Failed to execute command: {e}")
                        print("Try using mongo-js-executor for complex operations.")
                        raise
            else:
                # Just show connection info and list collections
                print("Testing connection...")
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

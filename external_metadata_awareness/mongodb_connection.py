import logging
import os
import sys
import re
import subprocess
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse, urlunparse

import click
from dotenv import load_dotenv
import pymongo
from pymongo import uri_parser

logger = logging.getLogger(__name__)


def _redact_uri(uri: str) -> str:
    """Redact credentials from a MongoDB URI for safe logging."""
    parsed = urlparse(uri)
    if parsed.password:
        host_part = parsed.hostname + (f":{parsed.port}" if parsed.port else "")
        redacted = parsed._replace(netloc=f"{parsed.username}:****@{host_part}")
        return urlunparse(redacted)
    return uri


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
            logger.debug(f"Loaded .env file from {env_file}")
        
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

            # Ensure authSource is set. Without it, MongoDB tries to authenticate
            # against the URI's database, which usually doesn't hold the user
            # record and fails with "Authentication failed".
            auth_source = os.getenv("MONGO_AUTH_SOURCE", "admin")
            if "authSource=" not in final_uri:
                separator = "&" if "?" in final_uri else "?"
                final_uri = f"{final_uri}{separator}authSource={auth_source}"

            if debug:
                logger.debug("Loaded credentials from .env file")
        else:
            if debug:
                logger.debug("No credentials found in .env file, continuing with unauthenticated connection")
    
    # Avoid logging connection URIs, even redacted ones, to keep credentials
    # and infrastructure details out of logs.
    if debug:
        logger.debug("Final connection URI prepared")
    
    # Re-parse now that credentials have been applied. This runs for both the
    # dry-run and connect paths so they fail the same way; validating only in
    # the dry run left --connect reporting the raw parser message with none of
    # the guidance below.
    try:
        parsed_final = uri_parser.parse_uri(final_uri)
    except pymongo.errors.InvalidURI as exc:
        # Credentials needing percent-encoding produce a URI that only fails
        # once parsed. Raise ValueError like the other URI problems above, so
        # callers get the same handling and format guidance. The parser message
        # is not interpolated: this point is reached after credentials were
        # applied, so it is kept out of the output.
        raise ValueError(
            "Invalid MongoDB URI after applying credentials. Username and "
            "password must be percent-encoded per RFC 3986; see "
            "urllib.parse.quote_plus."
        ) from exc

    # For dry runs, return connection info instead of a client
    if dry_run:
        # Ask the URI parser for a username rather than looking for an "@",
        # which also matches option values such as ?appName=user@example.com
        # and would report credentials that are not there.
        return {
            "uri": final_uri,
            "has_credentials": bool(parsed_final.get("username")),
        }
    
    # Create the MongoDB client
    client = pymongo.MongoClient(final_uri)
    
    # Verify connection information
    if debug:
        logger.debug("MongoDB client initialized")
    
    return client


@click.command()
@click.option("--uri", required=True, help="MongoDB connection URI (must start with mongodb:// and include database name)")
@click.option("--env-file", "env_file", help="Path to .env file for credentials (should contain MONGO_USER and MONGO_PASSWORD)")
@click.option("--verbose", is_flag=True, help="Show verbose output")
@click.option("--connect", is_flag=True, help="Actually connect to the database")
@click.option("--command", help="MongoDB command to execute (must be valid JavaScript/MongoDB shell command)")
def main(uri, env_file, verbose, connect, command):
    """Test MongoDB connection using a URI and optional env file."""
    # Nothing else configures logging, so the debug messages get_mongo_client
    # emits under debug=True were being discarded and --verbose did nothing.
    # Configure it here, at the entry point, rather than at import time.
    # force=True because basicConfig does nothing when handlers already exist,
    # which would leave --verbose silent under a test runner or any importer
    # that configured logging first.
    # Keep the root at WARNING and raise only this module's logger. Putting the
    # root at DEBUG switches on pymongo.command and pymongo.connection debug
    # output, which carries connection details and command payloads, in a
    # function that deliberately never logs the URI even redacted.
    logging.basicConfig(
        level=logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
        force=True,
    )
    logger.setLevel(logging.DEBUG if verbose else logging.WARNING)

    try:
        # Get connection info in dry-run mode if not connecting
        if not connect and not command:
            connection_info = get_mongo_client(
                mongo_uri=uri,
                env_file=env_file,
                debug=verbose,
                dry_run=True
            )

            # Report on stdout, not through logger.debug: this is the result the
            # user asked for, and it has to show up without a --verbose flag.
            # The URI itself is never printed, since it can carry credentials.
            credentials = "yes" if connection_info["has_credentials"] else "no"
            print("Dry run: connection URI prepared, no connection attempted.")
            print(f"Credentials present in URI: {credentials}")
            print("Re-run with --connect to open a connection.")
        else:
            # Actually connect to the database
            client = get_mongo_client(
                mongo_uri=uri,
                env_file=env_file,
                debug=verbose
            )

            # Extract database name from URI
            parsed = uri_parser.parse_uri(uri)
            db_name = parsed.get('database')

            if not db_name:
                raise ValueError("MongoDB URI must include a database name")

            db = client[db_name]

            if command:
                # Execute command
                print(f"Executing command: {command}")

                # Parse MongoDB shell commands directly
                # Example: db.collection.createIndex({ field: 1 })
                index_match = re.match(r'db\.(\w+)\.createIndex\((.*)\)', command)
                
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
                        
                        # Resolve the same URI the PyMongo client used, so that
                        # credentials supplied via --env-file reach mongosh too.
                        # dry_run=True builds the URI without opening a connection.
                        connection_info = get_mongo_client(
                            mongo_uri=uri,
                            env_file=env_file,
                            debug=verbose,
                            dry_run=True
                        )
                        final_uri = connection_info["uri"]
                        credentials_text = ""
                        if connection_info["has_credentials"]:
                            credentials_text = " (with credentials)"

                        # Run the command with mongosh
                        cmd = ["mongosh", final_uri, "--eval", command]
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

import os
import sys
import argparse
from pathlib import Path
from typing import Optional, Dict, Any
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
import pymongo


def parse_mongo_uri(uri: str) -> Dict[str, Any]:
    """
    Parse a MongoDB URI into its component parts using the standard library.

    Args:
        uri: A MongoDB connection URI (mongodb://host:port/db)

    Returns:
        A dictionary containing the parsed components
    """
    result = {
        "host": "localhost",
        "port": 27017,
        "username": None,
        "password": None,
        "db_name": None,
        "options": {}
    }

    # Validate URI format
    if not uri:
        return result

    if not uri.startswith("mongodb://"):
        raise ValueError("MongoDB URI must start with 'mongodb://'")

    # Parse the URI using urllib
    try:
        parsed = urlparse(uri)

        # Get username and password if present
        if parsed.username:
            result["username"] = parsed.username
        if parsed.password:
            result["password"] = parsed.password

        # Get host and port
        if parsed.hostname:
            result["host"] = parsed.hostname
        if parsed.port:
            result["port"] = parsed.port

        # Get database name if present
        if parsed.path and parsed.path != "/":
            # Remove leading slash
            result["db_name"] = parsed.path.lstrip("/")

        # Get query parameters
        if parsed.query:
            query_params = parse_qs(parsed.query)
            # Convert from lists to single values
            for key, value in query_params.items():
                if value and len(value) > 0:
                    result["options"][key] = value[0]
    except Exception as e:
        raise ValueError(f"Error parsing URI: {e}")

    return result


def get_mongo_client(
        mongo_uri: Optional[str] = None,
        env_file: Optional[str] = None,
        debug: bool = False,
        dry_run: bool = False
) -> pymongo.MongoClient:
    """
    Establishes a connection to a MongoDB server based only on provided URI or env file.

    Args:
        mongo_uri: MongoDB connection URI string
        env_file: Path to .env file to load credentials from
        debug: Print debug information about the connection
        dry_run: If True, don't actually connect, just return connection info

    Returns:
        A pymongo.MongoClient instance or connection info dict if dry_run=True
    """
    # Initialize connection parameters with minimal defaults
    conn_params = {
        "host": "localhost",
        "port": 27017,
        "username": None,
        "password": None,
        "db_name": None,
        "options": {}
    }

    # Step 1: Parse the URI if provided
    uri_params = None
    if mongo_uri:
        if debug:
            masked_uri = mongo_uri
            if "@" in mongo_uri:
                # Mask credentials in URI for debug output
                try:
                    protocol, rest = mongo_uri.split("://", 1)
                    user_pass, rest = rest.split("@", 1)
                    masked_uri = f"{protocol}://[credentials_masked]@{rest}"
                except ValueError:
                    # If splitting fails, just show as is (will be caught by parser)
                    pass
            print(f"Parsing URI: {masked_uri}")

        uri_params = parse_mongo_uri(mongo_uri)

        # Update connection parameters from the URI
        conn_params["host"] = uri_params["host"]
        conn_params["port"] = uri_params["port"]
        conn_params["username"] = uri_params["username"]
        conn_params["password"] = uri_params["password"]
        conn_params["db_name"] = uri_params["db_name"]
        conn_params["options"] = uri_params["options"]

    # Step 2: Load credentials from env file only if username/password not in URI
    if (not conn_params["username"] or not conn_params["password"]) and env_file and Path(env_file).exists():
        load_dotenv(env_file, override=True)
        if debug:
            print(f"Loaded .env file from {env_file}")

        # Get credentials from environment
        env_username = os.getenv("MONGO_USERNAME")
        env_password = os.getenv("MONGO_PASSWORD")

        if env_username and env_password:
            conn_params["username"] = env_username
            conn_params["password"] = env_password

            if debug:
                username_preview = env_username
                if len(username_preview) > 4:
                    username_preview = f"{username_preview[:2]}...{username_preview[-2:]}"
                print(f"Loaded credentials from .env file - Username: {username_preview}")

    # Debug output
    if debug:
        print(f"Final connection parameters:")
        print(f"  Host: {conn_params['host']}")
        print(f"  Port: {conn_params['port']}")
        if conn_params['db_name']:
            print(f"  Database: {conn_params['db_name']}")
        print(f"  Using authentication: {bool(conn_params['username'] and conn_params['password'])}")
        if conn_params['options']:
            print(f"  Connection options: {conn_params['options']}")

    # Construct the connection URI exactly as provided or with minimal parameters
    final_uri = None
    if mongo_uri:
        # Use the provided URI as the base
        final_uri = mongo_uri

        # If credentials were loaded from env file and not in the original URI,
        # inject them into the URI
        if not uri_params["username"] and not uri_params["password"] and conn_params["username"] and conn_params[
            "password"]:
            protocol, rest = mongo_uri.split("://", 1)
            if "@" in rest:
                # There's already some auth part that we need to replace
                _, after_auth = rest.split("@", 1)
                final_uri = f"{protocol}://{conn_params['username']}:{conn_params['password']}@{after_auth}"
            else:
                # No auth part, add it
                final_uri = f"{protocol}://{conn_params['username']}:{conn_params['password']}@{rest}"
    else:
        # No URI provided, construct a minimal one
        if conn_params["username"] and conn_params["password"]:
            final_uri = f"mongodb://{conn_params['username']}:{conn_params['password']}@{conn_params['host']}:{conn_params['port']}"
        else:
            final_uri = f"mongodb://{conn_params['host']}:{conn_params['port']}"

        # Add database name if available
        if conn_params["db_name"]:
            final_uri += f"/{conn_params['db_name']}"

        # Add options if any (should only be from URI or default)
        if conn_params["options"]:
            options_str = "&".join(f"{k}={v}" for k, v in conn_params["options"].items())
            final_uri += f"?{options_str}"

    # For debug, show the masked URI
    masked_uri = final_uri
    if conn_params["username"] and conn_params["password"]:
        protocol, rest = final_uri.split("://", 1)
        if "@" in rest:
            user_pass, after_auth = rest.split("@", 1)
            masked_uri = f"{protocol}://[credentials_masked]@{after_auth}"

    if debug:
        print(f"Final connection URI: {masked_uri}")

    # Generate mongosh command
    mongosh_cmd = generate_mongosh_command(conn_params)

    # For dry runs, return connection info instead of a client
    if dry_run:
        return {
            "uri": masked_uri,
            "params": {k: v for k, v in conn_params.items() if k != "password"},
            "has_credentials": bool(conn_params["username"] and conn_params["password"]),
            "mongosh_command": mongosh_cmd
        }

    # Create the MongoDB client with minimal options
    client = pymongo.MongoClient(final_uri)

    # Verify connection information
    if debug:
        print(f"MongoDB client address: {client.address}")

    return client


def generate_mongosh_command(conn_params):
    """Generate a mongosh command line that can be pasted into a shell."""
    cmd_parts = ["mongosh"]

    # Add host and port only
    cmd_parts.append(f"--host {conn_params['host']}")
    cmd_parts.append(f"--port {conn_params['port']}")

    # Add authentication if available
    if conn_params["username"] and conn_params["password"]:
        cmd_parts.append(f"--username {conn_params['username']}")
        cmd_parts.append(f"--password {conn_params['password']}")

    # Add database name if available
    if conn_params["db_name"]:
        cmd_parts.append(conn_params["db_name"])  # Database as positional argument

    # Add any additional options specified in the original URI
    for key, value in conn_params["options"].items():
        if key == "authSource":
            cmd_parts.append(f"--authenticationDatabase {value}")
        elif key == "authMechanism":
            cmd_parts.append(f"--authenticationMechanism {value}")
        # Only add other options if they were explicitly in the original URI
        # We're not adding any defaults here

    # Construct a URI for the mongosh command
    uri_cmd = "mongosh"
    if conn_params["username"] and conn_params["password"]:
        # Build URI with authentication
        uri = f"mongodb://{conn_params['username']}:{conn_params['password']}@{conn_params['host']}:{conn_params['port']}"
    else:
        # Build URI without authentication
        uri = f"mongodb://{conn_params['host']}:{conn_params['port']}"

    # Add database name if available
    if conn_params["db_name"]:
        uri += f"/{conn_params['db_name']}"

    # Add any options that were explicitly specified
    if conn_params["options"]:
        options_str = "&".join(f"{k}={v}" for k, v in conn_params["options"].items())
        uri += f"?{options_str}"

    uri_cmd = f"mongosh \"{uri}\""

    return {
        "command_with_args": " ".join(cmd_parts),
        "command_with_uri": uri_cmd,
        "shell_export_commands": generate_shell_exports(conn_params)
    }


def generate_shell_exports(conn_params):
    """Generate shell export commands for the MongoDB connection parameters."""
    if not (conn_params["username"] and conn_params["password"]):
        return None

    exports = [
        f"export MONGO_USERNAME='{conn_params['username']}'",
        f"export MONGO_PASSWORD='{conn_params['password']}'"
    ]

    return "\n".join(exports)


def main():
    """Command-line interface for testing MongoDB connection parameters."""
    parser = argparse.ArgumentParser(description="Show MongoDB connection details based only on provided inputs")
    parser.add_argument("--uri", help="MongoDB connection URI (must start with mongodb://)")
    parser.add_argument("--env-file", help="Path to .env file for credentials")
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

            print("\nMongoDB Connection Details:")
            print("--------------------------")
            print(f"Host: {result['params']['host']}")
            print(f"Port: {result['params']['port']}")
            if result['params']['db_name']:
                print(f"Database: {result['params']['db_name']}")
            if result['has_credentials']:
                print(f"Has Credentials: Yes")

            # Show any explicitly provided options
            if result['params']['options']:
                print("\nConnection Options:")
                for key, value in result['params']['options'].items():
                    print(f"  {key}: {value}")

            # Show mongosh commands
            print("\nMongoDB Shell Commands:")
            print("--------------------------")
            print(f"With separate arguments:")
            print(f"  {result['mongosh_command']['command_with_args']}")
            print(f"\nWith URI:")
            print(f"  {result['mongosh_command']['command_with_uri']}")

            # If credentials are available, show export commands
            if result['mongosh_command']['shell_export_commands']:
                print("\nShell export commands:")
                print(f"{result['mongosh_command']['shell_export_commands']}")
        else:
            # Actually try to connect
            print("Testing connection...")
            # result is a pymongo.MongoClient in this case
            db_name = None
            if args.uri:
                try:
                    parsed = parse_mongo_uri(args.uri)
                    db_name = parsed.get("db_name")
                except ValueError:
                    pass

            if db_name:
                db = result[db_name]
                print(f"Connected to database: {db.name}")
                print(f"Collections: {db.list_collection_names()}")
            else:
                print("Connected successfully to MongoDB server")
                print("Available databases: ", result.list_database_names())

            print("Connection test successful!")

    except ValueError as e:
        print(f"Error: {e}")
        print("\nThe MongoDB URI must use the format: mongodb://[username:password@]host[:port][/database][?options]")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

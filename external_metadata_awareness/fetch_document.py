#!/usr/bin/env python3
"""Minimal script to fetch one document from a MongoDB collection."""

import json
from urllib.parse import urlparse
import click
from bson import json_util
from external_metadata_awareness.mongodb_connection import get_mongo_client


@click.command()
@click.option("--mongo-uri", required=True, help="MongoDB URI (must start with mongodb:// and include database name)")
@click.option("--env-file", help="Path to .env file for credentials (should contain MONGO_USER and MONGO_PASSWORD)")
@click.option("--collection", required=True, help="Collection name to fetch document from")
@click.option("--verbose", is_flag=True, help="Show verbose connection output")
def fetch_document(mongo_uri, env_file, collection, verbose):
    """Fetch a single document from a MongoDB collection."""
    try:
        # Get MongoDB client
        client = get_mongo_client(
            mongo_uri=mongo_uri,
            env_file=env_file,
            debug=verbose
        )

        # Extract database name from URI
        parsed = urlparse(mongo_uri)
        db_name = parsed.path.lstrip("/").split("?")[0]
        
        if verbose:
            click.echo(f"Using database: {db_name}")

        # Access the database and collection
        db = client[db_name]

        # Get one document from the collection
        doc = db[collection].find_one()

        if doc:
            # Convert ObjectId to string for JSON serialization
            json_doc = json.loads(json_util.dumps(doc))
            click.echo(json.dumps(json_doc, indent=2))
        else:
            click.echo(f"No documents found in collection: {collection}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        exit(1)


if __name__ == "__main__":
    fetch_document()

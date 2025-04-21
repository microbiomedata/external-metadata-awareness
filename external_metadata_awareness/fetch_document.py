#!/usr/bin/env python3
"""Minimal script to fetch one document from a MongoDB collection."""

import json
import click
from bson import json_util
from external_metadata_awareness.mongodb_connection import get_mongo_client


@click.command()
@click.option("--uri", help="MongoDB URI (must start with mongodb://)")
@click.option("--env-file", help="Path to .env file for credentials")
@click.option("--collection", required=True, help="Collection name to fetch document from")
@click.option("--verbose", is_flag=True, help="Show verbose connection output")
def fetch_document(uri, env_file, collection, verbose):
    """Fetch a single document from a MongoDB collection."""
    try:
        # Get MongoDB client
        client = get_mongo_client(
            mongo_uri=uri,
            env_file=env_file,
            debug=verbose
        )

        # Extract database name from URI if provided
        db_name = None
        if uri and '/' in uri:
            parts = uri.split('/')
            if len(parts) > 3:  # mongodb://host:port/dbname
                db_part = parts[3]
                if '?' in db_part:
                    db_name = db_part.split('?')[0]
                else:
                    db_name = db_part

        # Use default if no database in URI
        if not db_name:
            db_name = "test"
            click.echo(f"No database specified in URI, using default: {db_name}")

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

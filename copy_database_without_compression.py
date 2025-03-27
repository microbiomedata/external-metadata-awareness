#!/usr/bin/env python3
import click
from pymongo import MongoClient
from datetime import datetime


# # for example:

# python copy_database_without_compression.py \
# --source-uri 'mongodb://localhost:27017/' \
# --dest-uri 'mongodb://mam-ncbi:carve_uninsured_rocking_293@localhost:27777?directConnection=true&authMechanism=SCRAM-SHA-256&authSource=admin' \
# --source-db-name nmdc \
# --dest-db-name misc_metadata \
# --skip-system \
# --skip-collection workflow_execution_set

# --skip-collection functional_annotation_agg \


def copy_database(source_uri, dest_uri, source_db_name, dest_db_name, skip_collections, skip_system):
    """
    Copies an entire MongoDB database from a source server to a destination server.

    Parameters:
      source_uri (str): MongoDB URI of the source server.
      dest_uri (str): MongoDB URI of the destination server.
      source_db_name (str): Name of the database to copy from.
      dest_db_name (str): Name of the database to copy to.
      skip_collections (list): List of collection names to skip.
      skip_system (bool): Whether to skip system collections (those starting with "system.").
    """
    source_client = MongoClient(source_uri)
    dest_client = MongoClient(dest_uri)

    if not dest_db_name or dest_db_name == "":
        dest_db_name = source_db_name

    source_db = source_client[source_db_name]
    dest_db = dest_client[dest_db_name]

    click.echo(f"Copying from '{source_db_name}' to '{dest_db_name}'")

    collection_names = source_db.list_collection_names()
    collection_names.sort()

    for coll_name in collection_names:
        if skip_system and coll_name.startswith("system."):
            click.echo(f"{datetime.now().isoformat()} - Skipping system collection: {coll_name}")
            continue
        if coll_name in skip_collections:
            click.echo(f"{datetime.now().isoformat()} - Skipping collection (user-specified): {coll_name}")
            continue

        click.echo(f"{datetime.now().isoformat()} - Copying collection: {coll_name}")
        source_coll = source_db[coll_name]
        dest_coll = dest_db[coll_name]

        # Drop destination collection if it exists
        dest_coll.drop()

        documents = list(source_coll.find())
        if documents:
            dest_coll.insert_many(documents)
            click.echo(f"{datetime.now().isoformat()} - Copied {len(documents)} documents.")
        else:
            # dest_coll.insert_many(documents)
            click.echo(f"{datetime.now().isoformat()} - Collection is empty.")


@click.command()
@click.option('--source-uri', required=True,
              help="MongoDB URI for the source server (e.g., 'mongodb://localhost:27017/').")
@click.option('--dest-uri', required=True,
              help="MongoDB URI for the destination server (e.g., 'mongodb://destination_server:27017/').")
@click.option('--source-db-name', required=True, help="Name of the database to copy.")
@click.option('--dest-db-name', required=True, help="Name of the database to copy.")
@click.option('--skip-collection', multiple=True,
              help="Name of a collection to skip (can be specified multiple times).")
@click.option('--skip-system/--no-skip-system', default=True,
              help="Skip system collections (those starting with 'system.'). Defaults to True.")
def main(source_uri, dest_uri, source_db_name, dest_db_name, skip_collection, skip_system):
    """Copy an entire MongoDB database from a source server to a destination server."""
    copy_database(source_uri, dest_uri, source_db_name, dest_db_name, list(skip_collection), skip_system)


if __name__ == '__main__':
    main()

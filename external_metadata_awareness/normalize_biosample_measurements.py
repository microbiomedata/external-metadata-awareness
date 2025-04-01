import datetime
import sys
import time
from copy import deepcopy

import click
from pymongo import MongoClient
from quantulum3 import parser
from tqdm import tqdm


def ensure_index(collection, field_name):
    """Ensure an ascending index exists on the given field."""
    existing_indexes = collection.index_information()
    if field_name not in [list(i["key"])[0][0] for i in existing_indexes.values()]:
        collection.create_index([(field_name, 1)])
        click.echo(f"[{timestamp()}] Created index on '{collection.name}.{field_name}'")
    else:
        click.echo(f"[{timestamp()}] Index already exists on '{collection.name}.{field_name}'")


def clean_dict(d):
    """Recursively remove empty lists/dicts from a dictionary."""
    if isinstance(d, list):
        return [clean_dict(x) for x in d if clean_dict(x) not in ({}, [], None)]
    elif isinstance(d, dict):
        return {k: clean_dict(v) for k, v in d.items() if clean_dict(v) not in ({}, [], None)}
    else:
        return d


def timestamp():
    """Return ISO 8601 formatted timestamp."""
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def format_quantity_value(q):
    """Format the quantity value with uncertainty if present."""
    unit_name = q['unit']['name'] if q['unit']['name'] != "dimensionless" else ""

    if 'uncertainty' in q and q['uncertainty'] is not None:
        lower = q['value'] - q['uncertainty']
        upper = q['value'] + q['uncertainty']
        return f"{lower}-{upper} {unit_name}".strip()
    else:
        return f"{q['value']} {unit_name}".strip()


def aggregate_measurements(client, db_name, input_collection, output_collection, field_name, extra_verbose, overwrite):
    """Aggregate measurements from the specified field."""
    db = client[db_name]

    click.echo(
        f"[{timestamp()}] Step 1: Aggregating unique values for field '{field_name}' from collection '{input_collection}'...")

    # Check if input collection exists
    if input_collection not in db.list_collection_names():
        click.echo(
            f"[{timestamp()}] Error: Input collection '{input_collection}' does not exist in database '{db_name}'",
            err=True)
        sys.exit(1)

    # Create the aggregation pipeline
    pipeline = [
        {"$match": {field_name: {"$exists": True, "$ne": None}}},
        {"$group": {"_id": f"${field_name}", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]

    # Get count of matching documents for progress reporting
    match_count = db[input_collection].count_documents({field_name: {"$exists": True, "$ne": None}})
    click.echo(
        f"[{timestamp()}] Found {match_count} documents with field '{field_name}' in collection '{input_collection}'")

    # Run the aggregation
    click.echo(f"[{timestamp()}] Running aggregation pipeline...")
    start_time = time.time()
    result = list(db[input_collection].aggregate(pipeline))
    end_time = time.time()
    click.echo(f"[{timestamp()}] Aggregation completed in {end_time - start_time:.2f} seconds")
    click.echo(f"[{timestamp()}] Identified {len(result)} unique values for field '{field_name}'")

    # Create output collection if it doesn't exist
    if output_collection not in db.list_collection_names():
        click.echo(f"[{timestamp()}] Creating new collection '{output_collection}'...")
    else:
        # Check for existing documents with the same harmonized name
        existing_count = db[output_collection].count_documents({"harmonized_name": field_name})
        if existing_count > 0:
            if overwrite:
                click.echo(
                    f"[{timestamp()}] Removing {existing_count} existing documents for field '{field_name}' from '{output_collection}'...")
                db[output_collection].delete_many({"harmonized_name": field_name})
            else:
                click.echo(
                    f"[{timestamp()}] Warning: {existing_count} documents for field '{field_name}' already exist in '{output_collection}'")
                click.echo(
                    f"[{timestamp()}] Skipping aggregation for field '{field_name}'. Use --overwrite to replace existing data.")
                return None

    # Insert documents with the harmonized_name field
    click.echo(
        f"[{timestamp()}] Adding {len(result)} documents for field '{field_name}' to collection '{output_collection}'...")
    with tqdm(total=len(result), desc=f"[{timestamp()}] Inserting documents", unit="doc") as pbar:
        for doc in result:
            db[output_collection].insert_one({
                "_id": f"{field_name}:{doc['_id']}",  # Namespace the ID to avoid collisions
                "original_value": doc["_id"],
                "harmonized_name": field_name,
                "count": doc["count"]
            })
            pbar.update(1)

    click.echo(
        f"[{timestamp()}] Successfully added {len(result)} documents for field '{field_name}' to collection '{output_collection}'")
    return field_name


def parse_measurements(client, db_name, collection_name, field_name, extra_verbose):
    """Parse measurements using quantulum3."""
    db = client[db_name]
    col = db[collection_name]

    click.echo(
        f"[{timestamp()}] Step 2: Parsing measurement values for field '{field_name}' in collection '{collection_name}'...")

    # Get total document count for progress reporting
    total_docs = col.count_documents({"harmonized_name": field_name})
    click.echo(f"[{timestamp()}] Found {total_docs} documents to process for field '{field_name}'")

    parsed_count = 0
    skipped_count = 0

    # Iterate over documents with progress bar
    with tqdm(total=total_docs, desc=f"[{timestamp()}] Parsing measurements", unit="doc") as pbar:
        for doc in col.find({"harmonized_name": field_name}):
            raw_val = doc["original_value"]

            try:
                parsed = parser.parse(str(raw_val))  # Ensure it's a string
            except Exception as e:
                if extra_verbose:
                    click.echo(f"[{timestamp()}] Error parsing '{raw_val}': {str(e)}")
                skipped_count += 1
                pbar.update(1)
                continue

            if not parsed:
                if extra_verbose:
                    click.echo(f"[{timestamp()}] No quantity detected in '{raw_val}'")
                skipped_count += 1
                pbar.update(1)
                continue

            # Convert Quantity objects to JSON-serializable dicts
            parsed_dicts = []
            for q in parsed:
                try:
                    # Create a copy of the object's dict
                    q_dict = deepcopy(q.__dict__)

                    # Convert unit object to a simple dictionary
                    if 'unit' in q_dict and hasattr(q_dict['unit'], 'name'):
                        q_dict['unit'] = {
                            'name': q_dict['unit'].name,
                            'entity': q_dict['unit'].entity.name if hasattr(q_dict['unit'].entity, 'name') else str(
                                q_dict['unit'].entity),
                            'uri': str(q_dict['unit'].uri) if hasattr(q_dict['unit'], 'uri') else None
                        }

                    # Convert span tuple to list for better MongoDB compatibility
                    if 'span' in q_dict and isinstance(q_dict['span'], tuple):
                        q_dict['span'] = list(q_dict['span'])

                    # Clean the dictionary
                    cleaned_dict = clean_dict(q_dict)
                    parsed_dicts.append(cleaned_dict)
                except Exception as e:
                    if extra_verbose:
                        click.echo(f"[{timestamp()}] Error processing parsed result for '{raw_val}': {str(e)}")

            # Remove any completely empty results
            parsed_dicts = [pd for pd in parsed_dicts if pd]

            if parsed_dicts:
                reconstructed_values = []
                try:
                    # Generate reconstructed values
                    reconstructed_values = [format_quantity_value(q) for q in parsed_dicts]

                    # Update the document with parsed quantities
                    col.update_one(
                        {"_id": doc["_id"]},
                        {"$set": {
                            "parsed_quantity": parsed_dicts,
                            "reconstructed": reconstructed_values
                        }}
                    )
                    parsed_count += 1

                    if extra_verbose:
                        click.echo(
                            f"[{timestamp()}] Successfully parsed '{raw_val}' → {', '.join(reconstructed_values)}")
                except Exception as e:
                    if extra_verbose:
                        click.echo(f"[{timestamp()}] Error updating document for '{raw_val}': {str(e)}")
                    skipped_count += 1
            else:
                skipped_count += 1
                if extra_verbose:
                    click.echo(f"[{timestamp()}] No valid parsed results for '{raw_val}'")

            pbar.update(1)

    # Summary statistics
    if total_docs > 0:
        click.echo(f"[{timestamp()}] Parsing summary for field '{field_name}':")
        click.echo(f"[{timestamp()}]   - Total documents: {total_docs}")
        click.echo(
            f"[{timestamp()}]   - Successfully parsed: {parsed_count} ({(parsed_count / total_docs) * 100:.2f}%)")
        click.echo(f"[{timestamp()}]   - Skipped/failed: {skipped_count} ({(skipped_count / total_docs) * 100:.2f}%)")
    else:
        click.echo(f"[{timestamp()}] No documents processed for field '{field_name}'")

    return parsed_count


@click.command()
@click.option('--mongodb-uri', default='mongodb://localhost:27017', help='MongoDB connection URI')
@click.option('--db-name', default='ncbi_metadata', help='Database name')
@click.option('--input-collection', default='biosamples_flattened', help='Input collection name')
@click.option('--output-collection', default='biosamples_measurements', help='Output collection name')
@click.option('--field', required=True, multiple=True,
              help='Field name(s) to parse (e.g., samp_size). Can be specified multiple times.')
@click.option('-v', '--verbosity',
              type=click.Choice(['quiet', 'normal', 'verbose']),
              default='normal',
              help='Set output verbosity: quiet (errors only), normal (default), or verbose (detailed)')
@click.option('--overwrite', is_flag=True, help='Overwrite existing data for the specified field(s)')
def main(mongodb_uri, db_name, input_collection, output_collection, field, verbosity, overwrite):
    """Parse and normalize measurement fields from MongoDB collections."""
    try:
        # Set output verbosity
        is_quiet = verbosity == 'quiet'
        is_verbose = verbosity == 'verbose'

        if not is_quiet:
            click.echo(f"[{timestamp()}] " + "=" * 80)
            click.echo(f"[{timestamp()}]  Measurement Parser for MongoDB Collections ")
            click.echo(f"[{timestamp()}] " + "=" * 80)
            click.echo(f"[{timestamp()}] Database: {db_name}")
            click.echo(f"[{timestamp()}] Input collection: {input_collection}")
            click.echo(f"[{timestamp()}] Output collection: {output_collection}")
            click.echo(f"[{timestamp()}] Fields to parse: {', '.join(field)}")
            click.echo(f"[{timestamp()}] MongoDB URI: {mongodb_uri}")
            click.echo(f"[{timestamp()}] Verbosity: {verbosity}")
            click.echo(f"[{timestamp()}] Overwrite existing: {'Yes' if overwrite else 'No'}")
            click.echo(f"[{timestamp()}] " + "-" * 80)

        # Connect to MongoDB
        if not is_quiet:
            click.echo(f"[{timestamp()}] Connecting to MongoDB at {mongodb_uri}...")
        start_time = time.time()
        client = MongoClient(mongodb_uri)

        # Verify connection
        client.admin.command('ping')
        end_time = time.time()
        if not is_quiet:
            click.echo(f"[{timestamp()}] Connected successfully in {end_time - start_time:.2f} seconds")

        # Display available databases and collections
        if is_verbose:
            click.echo(f"[{timestamp()}] Available databases: {', '.join(client.list_database_names())}")
            if db_name in client.list_database_names():
                db = client[db_name]
                click.echo(f"[{timestamp()}] Collections in '{db_name}': {', '.join(db.list_collection_names())}")

        total_start_time = time.time()
        fields_processed = 0
        total_parsed = 0

        # Process each field incrementally
        for current_field in field:

            ensure_index(client[db_name][input_collection], current_field)

            if not is_quiet:
                click.echo(f"[{timestamp()}] " + "-" * 80)
                click.echo(f"[{timestamp()}] Processing field: '{current_field}'")

            # Step 1: Aggregate measurements
            field_start_time = time.time()
            processed_field = aggregate_measurements(client, db_name, input_collection, output_collection,
                                                     current_field, is_verbose, overwrite)

            # If aggregation was skipped (no overwrite), continue to next field
            if processed_field is None:
                if not is_quiet:
                    click.echo(f"[{timestamp()}] Skipping processing for field '{current_field}'")
                continue

            ensure_index(client[db_name][output_collection], "harmonized_name")

            # Step 2: Parse measurements
            parsed_count = parse_measurements(client, db_name, output_collection, current_field, is_verbose)
            field_end_time = time.time()
            field_duration = field_end_time - field_start_time

            if not is_quiet:
                click.echo(f"[{timestamp()}] Field '{current_field}' processed in {field_duration:.2f} seconds")

            fields_processed += 1
            total_parsed += parsed_count

        total_end_time = time.time()
        total_duration = total_end_time - total_start_time

        # Final summary
        if not is_quiet:
            click.echo(f"[{timestamp()}] " + "=" * 80)
            click.echo(f"[{timestamp()}]  Operation Summary ")
            click.echo(f"[{timestamp()}] " + "=" * 80)
            click.echo(f"[{timestamp()}] Fields processed: {fields_processed} of {len(field)}")
            click.echo(f"[{timestamp()}] Total documents parsed: {total_parsed}")
            click.echo(f"[{timestamp()}] Input collection: '{input_collection}'")
            click.echo(f"[{timestamp()}] Output collection: '{output_collection}'")
            click.echo(f"[{timestamp()}] Total processing time: {total_duration:.2f} seconds")
            click.echo(f"[{timestamp()}] " + "=" * 80)
            click.echo(f"[{timestamp()}] Operation completed successfully!")

    except Exception as e:
        click.echo(f"[{timestamp()}] " + "=" * 80)
        click.echo(f"[{timestamp()}]  ERROR ")
        click.echo(f"[{timestamp()}] " + "=" * 80)
        click.echo(f"[{timestamp()}] An error occurred: {str(e)}")
        raise


if __name__ == "__main__":
    main()

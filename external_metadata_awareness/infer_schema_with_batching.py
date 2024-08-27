import json
from typing import Dict, Any, Set
from pymongo import MongoClient, errors
from tqdm import tqdm
import click


def infer_schema_in_batches(collection, total_samples: int, batch_size: int) -> Dict[str, Any]:
    """
    Infer the schema of a MongoDB collection using batched sampling.

    Args:
        collection: The MongoDB collection to analyze.
        total_samples (int): The total number of documents to sample.
        batch_size (int): The size of each batch to process.

    Returns:
        A dictionary representing the inferred schema.
    """
    schema = {}
    sampled_ids: Set[Any] = set()  # Track sampled document IDs
    num_batches = total_samples // batch_size

    for batch_num in tqdm(range(num_batches), desc="Processing Batches"):
        remaining_sample_size = batch_size
        while remaining_sample_size > 0:
            pipeline = [{"$sample": {"size": remaining_sample_size}}]
            cursor = collection.aggregate(pipeline)

            new_docs = 0
            for document in cursor:
                doc_id = document['_id']
                if doc_id not in sampled_ids:
                    sampled_ids.add(doc_id)
                    update_schema(schema, document)
                    new_docs += 1

            remaining_sample_size = batch_size - new_docs  # Update remaining sample size

    # Print the number of unique documents processed
    print(f"Number of unique documents processed: {len(sampled_ids)}")

    return schema


def update_schema(schema: Dict[str, Any], document: Dict[str, Any]) -> None:
    """
    Update the inferred schema with a new document.

    Args:
        schema: The current schema dictionary.
        document: The document to use for updating the schema.
    """
    for key, value in document.items():
        if key not in schema:
            schema[key] = infer_type(value)
        elif isinstance(value, dict):
            if not isinstance(schema[key], dict):
                schema[key] = {}
            update_schema(schema[key], value)
        elif isinstance(value, list):
            if not isinstance(schema[key], list):
                schema[key] = [infer_type(value[0]) if value else "None"]
            elif value:
                schema[key][0] = merge_types(schema[key][0], infer_type(value[0]))
        else:
            schema[key] = merge_types(schema[key], infer_type(value))


def infer_type(value: Any) -> str:
    """
    Infer the type of a MongoDB document field.

    Args:
        value: The value to infer the type of.

    Returns:
        A string representing the type of the value.
    """
    if isinstance(value, dict):
        return {k: infer_type(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [infer_type(value[0]) if value else "None"]
    else:
        return type(value).__name__


def merge_types(type1: Any, type2: Any) -> Any:
    """
    Merge two inferred types into one, favoring more specific types.

    Args:
        type1: The first inferred type.
        type2: The second inferred type.

    Returns:
        The merged type.
    """
    if type1 == type2:
        return type1
    elif isinstance(type1, dict) and isinstance(type2, dict):
        merged = type1.copy()
        for key, value in type2.items():
            if key in merged:
                merged[key] = merge_types(merged[key], value)
            else:
                merged[key] = value
        return merged
    elif isinstance(type1, list) and isinstance(type2, list):
        return [merge_types(type1[0], type2[0])]
    else:
        return "Mixed"


@click.command()
@click.option('--host', default='localhost', help='MongoDB host.')
@click.option('--port', default=27017, help='MongoDB port.')
@click.option('--database', required=True, help='Name of the database.')
@click.option('--collection', required=True, help='Name of the collection.')
@click.option('--total-samples', default=410000, help='Total number of documents to sample.')
@click.option('--batch-size', default=100000, help='Number of documents to sample in each batch.')
@click.option('--output', default='schema.json', help='Output file to save the schema.')
def main(host: str, port: int, database: str, collection: str, total_samples: int, batch_size: int, output: str):
    """
    Command-line tool to infer the schema of a MongoDB collection using batched sampling and save it to a file.

    Args:
        host: The MongoDB host.
        port: The MongoDB port.
        database: The name of the database.
        collection: The name of the collection.
        total_samples: The total number of documents to sample.
        batch_size: The size of each batch to process.
        output: The output file to save the schema.
    """
    try:
        # Connect to MongoDB
        client = MongoClient(host, port)
        db = client[database]
        coll = db[collection]

        # Check if the collection exists and has documents
        if coll.count_documents({}) == 0:
            click.echo(f"Error: The collection '{collection}' in database '{database}' is empty or does not exist.")
            return

        # Infer the schema in batches
        schema = infer_schema_in_batches(coll, total_samples, batch_size)

        # Export schema to a JSON file
        with open(output, "w") as file:
            json.dump(schema, file, indent=4)
        click.echo(f"Schema saved to {output}")

    except errors.ServerSelectionTimeoutError:
        click.echo("Error: Unable to connect to the MongoDB server. Please check your connection settings.")
    except errors.CollectionInvalid:
        click.echo(f"Error: The collection '{collection}' in database '{database}' is invalid or does not exist.")
    except Exception as e:
        click.echo(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()

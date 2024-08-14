import click
from pymongo import MongoClient
from tqdm import tqdm
from typing import Any, Dict, List


@click.command()
@click.option('--mongo-uri', default='mongodb://localhost:27017/', help='MongoDB URI connection string.')
@click.option('--db-name', default='biosamples', help='Database name.')
@click.option('--collection', default='biosamples', help='Collection name.')
@click.option('--sample-size', default=100_000, type=int, help='Number of documents to sample.')  # out of ~ 45 million
def main(mongo_uri: str, db_name: str, collection: str, sample_size: int):
    """
    Connects to a MongoDB collection, samples a set number of documents, and
    analyzes the structure of the sampled documents by enumerating and counting
    all the unique paths within them.

    :param mongo_uri: MongoDB URI connection string.
    :param db_name: Database name.
    :param collection: Collection name.
    :param sample_size: Number of documents to sample.
    """
    client = MongoClient(mongo_uri)
    db = client[db_name]
    coll = db[collection]

    # Sample 'n' documents randomly
    sampled_docs = coll.aggregate([{'$sample': {'size': sample_size}}])

    all_paths = []
    for doc in tqdm(sampled_docs, total=sample_size, desc="Processing documents"):
        doc_paths = find_paths(doc)
        all_paths.extend(doc_paths)

    # Aggregate and count paths
    path_counts = aggregate_paths(all_paths)

    # Sort path_counts alphabetically by path
    path_counts = dict(sorted(path_counts.items(), key=lambda item: item[0]))

    # Output the counted paths
    for path, count in path_counts.items():
        print(f"Path: {path}, Count: {count}")


def find_paths(document: Dict[str, Any], prefix: str = '') -> List[str]:
    """
    Recursively finds all paths in a nested dictionary and returns them.

    :param document: The document (nested dictionary) to find paths in.
    :param prefix: A prefix to prepend to each path (used for recursion).
    :return: A list of string paths.
    """
    paths = []
    if isinstance(document, dict):
        for key, value in document.items():
            sub_paths = find_paths(value, f"{prefix}{key}.")
            paths.extend(sub_paths)
    elif isinstance(document, list):
        for item in document:
            paths.extend(find_paths(item, prefix))
    else:
        return [prefix[:-1]]  # Remove the last dot
    return paths


def aggregate_paths(paths: List[str]) -> Dict[str, int]:
    """
    Aggregates a list of paths into a dictionary with path counts.

    :param paths: List of paths as strings.
    :return: Dictionary with paths as keys and their counts as values.
    """
    path_count = {}
    for path in paths:
        if path in path_count:
            path_count[path] += 1
        else:
            path_count[path] = 1
    return path_count


if __name__ == '__main__':
    main()

from pymongo import MongoClient
from tqdm import tqdm

# User-supplied settings
mongo_connection_string = 'mongodb://localhost:27017/'  # MongoDB connection string
database_name = 'biosamples'  # Database name
collection_name = 'biosamples'  # Collection name
sample_size = 500_000  # Number of documents to sample (out of roughly 43 million)


def find_paths(document, prefix=''):
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


def aggregate_paths(paths):
    path_count = {}
    for path in paths:
        if path in path_count:
            path_count[path] += 1
        else:
            path_count[path] = 1
    return path_count


client = MongoClient(mongo_connection_string)
db = client[database_name]
collection = db[collection_name]

# Sample 'n' documents randomly
sampled_docs = collection.aggregate([{'$sample': {'size': sample_size}}])

all_paths = []
for doc in tqdm(sampled_docs, total=sample_size, desc="Processing documents"):
    doc_paths = find_paths(doc)
    all_paths.extend(doc_paths)

# Aggregate and count paths
path_counts = aggregate_paths(all_paths)

# sort path_counts alphabetically by path
path_counts = dict(sorted(path_counts.items(), key=lambda item: item[0]))

# Output the counted paths
for path, count in path_counts.items():
    print(f"Path: {path}, Count: {count}")

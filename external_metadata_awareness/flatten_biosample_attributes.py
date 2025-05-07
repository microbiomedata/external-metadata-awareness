import click
from urllib.parse import urlparse
from tqdm import tqdm
from time import time
from external_metadata_awareness.mongodb_connection import get_mongo_client


@click.command()
@click.option("--mongo-uri", default="mongodb://localhost:27017/ncbi_metadata", show_default=True,
              help="MongoDB connection URI (must start with mongodb:// and include database name)")
@click.option("--env-file", default=None,
              help="Path to .env file for credentials (should contain MONGO_USER and MONGO_PASSWORD)")
@click.option("--verbose", is_flag=True, help="Show verbose connection output")
@click.option("--source-collection", default="biosamples", show_default=True, help="Source collection name")
@click.option("--target-collection", default="biosamples_attributes", show_default=True, help="Target collection name")
@click.option("--batch-size", default=1000, show_default=True, help="Batch insert size")
@click.option("--first-biosample", type=int, default=None, help="Minimum biosample `id` to process (inclusive)")
@click.option("--last-biosample", type=int, default=None, help="Maximum biosample `id` to process (inclusive)")
def extract_attributes(mongo_uri, env_file, verbose, source_collection, target_collection,
                       batch_size, first_biosample, last_biosample):
    client = get_mongo_client(
        mongo_uri=mongo_uri,
        env_file=env_file,
        debug=verbose
    )

    # Extract database name from URI
    parsed = urlparse(mongo_uri)
    db_name = parsed.path.lstrip("/").split("?")[0]

    if verbose:
        print(f"Using database: {db_name}")

    db = client[db_name]
    source = db[source_collection]
    target = db[target_collection]

    match_filter = {"Attributes.Attribute": {"$exists": True, "$type": "array"}}
    if first_biosample is not None:
        match_filter["id"] = {"$gte": str(first_biosample)}
    if last_biosample is not None:
        match_filter.setdefault("id", {})["$lte"] = str(last_biosample)

    pipeline = [
        {"$match": match_filter},
        {"$unwind": "$Attributes.Attribute"},
        {"$project": {
            "_id": 0,
            "biosample_id": "$id",
            "accession": "$accession",
            "attribute_name": "$Attributes.Attribute.attribute_name",
            "harmonized_name": "$Attributes.Attribute.harmonized_name",
            "display_name": "$Attributes.Attribute.display_name",
            "unit": "$Attributes.Attribute.unit",
            "content": "$Attributes.Attribute.content"
        }}
    ]

    cursor = source.aggregate(pipeline, allowDiskUse=True, batchSize=100)
    batch = []
    total_inserted = 0
    start_time = time()

    for doc in tqdm(cursor, desc="Processing attributes"):
        batch.append(doc)
        if len(batch) >= batch_size:
            target.insert_many(batch)
            total_inserted += len(batch)
            batch.clear()

    if batch:
        target.insert_many(batch)
        total_inserted += len(batch)

    elapsed_min = (time() - start_time) / 60
    click.echo(f"✅ Inserted {total_inserted:,} documents in {elapsed_min:.2f} minutes.")


if __name__ == "__main__":
    extract_attributes()

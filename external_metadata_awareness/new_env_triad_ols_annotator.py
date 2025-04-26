import datetime
import click

import requests
import requests_cache
from pymongo import uri_parser
from tqdm import tqdm

from external_metadata_awareness.mongodb_connection import get_mongo_client

# OLS Search API endpoint and query parameters
OLS_SEARCH_URL = "https://www.ebi.ac.uk/ols/api/search"
QUERYFIELDS = "label,synonym"
# type = class
FIELDLIST = "synonym,label,ontology_name,ontology_prefix,is_defining_ontology,obo_id"

OLS_REQ_EXACT_MATCH = "true"  # Use exact matching
# OLS_REQ_EXACT_MATCH = "false"  # Use exact matching # brings searching to a screeching halt

MIN_LABEL_LEN = 3  # Minimum length for labels to query
ROWS = 1000  # Number of results per page

requests_cache_filename="external-metadata-awareness-requests-cache"

# Enable requests caching (expires after 30 days)
requests_cache.install_cache(requests_cache_filename, expire_after=datetime.timedelta(days=30))


@click.command()
@click.option('--mongo-uri', default='mongodb://localhost:27017/ncbi_metadata', help='MongoDB connection URI (must start with mongodb:// and include database name)')
@click.option('--env-file', default=None, help='Path to .env file for credentials (should contain MONGO_USER and MONGO_PASSWORD)')
@click.option('--collection', default='env_triad_component_labels', help='MongoDB collection name')
@click.option('--min-length', default=3, type=int, help='Minimum label length to process')
@click.option('--max-oak-coverage', default=0.9, type=float, help='Maximum oak coverage to process (documents below this value will be annotated)')
@click.option('--verbose', is_flag=True, help='Show verbose connection output')
def main(mongo_uri, env_file, collection, min_length, max_oak_coverage, verbose):
    # Connect to MongoDB
    client = get_mongo_client(
        mongo_uri=mongo_uri,
        env_file=env_file,
        debug=verbose
    )
    
    # Extract database name from URI
    parsed = uri_parser.parse_uri(mongo_uri)
    db_name = parsed.get('database')
    
    if not db_name:
        raise ValueError("MongoDB URI must include a database name")
        
    db = client[db_name]
    collection = db[collection]

    # Find documents to update (those with combined_oak_coverage < max_oak_coverage)
    query = {
        "label_digits_only": False,
        "label_length": {"$gte": min_length},
        "combined_oak_coverage": {"$lt": max_oak_coverage}
    }

    projection = {"label": 1}
    docs = list(collection.find(query, projection))

    print(f"Found {len(docs)} documents.")

    # Process each document with a progress bar
    for doc in tqdm(docs, desc="Processing documents"):
        label_raw = doc.get("label")
        if not isinstance(label_raw, str):
            continue  # skip if label is missing or not a string

        query_text = label_raw.strip().lower()
        if not query_text or len(query_text) < MIN_LABEL_LEN:
            continue

        start = 0
        ols_hits = []
        while True:
            params = {
                "q": query_text,
                "exact": OLS_REQ_EXACT_MATCH,
                "fieldList": FIELDLIST,
                "queryFields": QUERYFIELDS,
                "rows": ROWS,
                "start": start,
            }

            try:
                response = requests.get(OLS_SEARCH_URL, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                if verbose:
                    print(f"Error: {e}")
                break

            results = data.get("response", {}).get("docs", [])
            if not results:
                break

            for result in results:
                if result.get("is_defining_ontology", True):
                    label_lower = result.get("label", "").lower()
                    exact_match = (label_lower == query_text)
                    synonyms = result.get("synonym", [])
                    exact_synonym_match = any(query_text == synonym.lower() for synonym in synonyms)
                    hit = {
                        "label": result.get("label", ""),
                        "synonyms": synonyms,
                        "exact_label_match": exact_match,
                        "exact_synonym_match": exact_synonym_match,
                        "obo_id": result.get("obo_id", ""),
                        # Store ontology name and prefix in upper case:
                        "ontology_name_uc": result.get("ontology_name", "").upper(),
                        "ontology_prefix_uc": result.get("ontology_prefix", "").upper(),
                    }
                    ols_hits.append(hit)

            num_found = data.get("response", {}).get("numFound", 0)
            start += ROWS
            if start >= num_found:
                break

        # If we found any OLS hits, update the document with the new fields,
        # including an "ols_annotations_count" field.
        if ols_hits:
            collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {
                    "ols_text_annotations": ols_hits,
                    "ols_annotations_count": len(ols_hits)
                }}
            )

    print("OLS lookups completed and documents updated.")


if __name__ == "__main__":
    main()

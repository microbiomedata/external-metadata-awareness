#!/usr/bin/env python3
import requests
from pymongo import MongoClient
from tqdm import tqdm
import requests_cache
import datetime

# --- Configuration ---
MONGO_URL = "mongodb://localhost:27017"
DATABASE_NAME = "ncbi_metadata"
COLLECTION_NAME = "env_triad_component_labels"

# OLS Search API endpoint and query parameters
OLS_SEARCH_URL = "https://www.ebi.ac.uk/ols/api/search"
QUERYFIELDS = "label,synonym"
# type = class
FIELDLIST = "synonym,label,ontology_name,ontology_prefix,is_defining_ontology,obo_id"

OLS_REQ_EXACT_MATCH = "true"  # Use exact matching
# OLS_REQ_EXACT_MATCH = "false"  # Use exact matching # brings searching to a screeching halt

MIN_LABEL_LEN = 3  # Minimum length for labels to query
ROWS = 1000  # Number of results per page

# Enable requests caching (expires after 7 days)
requests_cache.install_cache("requests_cache", expire_after=datetime.timedelta(days=30))


def main():
    # Connect to MongoDB
    client = MongoClient(MONGO_URL)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]

    # Find documents to update (in this example, those with combined_oak_coverage < 0.90)

    min_length = 3
    max_oak_coverage = 0.9

    query = {
        "label_digits_only": False,
        "label_length": {"$gte": min_length},
        "combined_oak_coverage": {"$lt": max_oak_coverage}
    }

    # query = {"combined_oak_coverage": {"$lt": 0.90}}
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

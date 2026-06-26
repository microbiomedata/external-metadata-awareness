import datetime
import logging
import os
import pprint
import urllib.parse
import click
from typing import List, Dict

logger = logging.getLogger(__name__)

import requests
import requests_cache
from dotenv import load_dotenv
from prefixmaps.io.parser import load_converter
from pymongo import uri_parser
from tqdm import tqdm

from external_metadata_awareness.mongodb_connection import get_mongo_client

requests_cache_filename = "external-metadata-awareness-requests-cache"

# Enable requests caching (expires after 30 days)
requests_cache.install_cache(requests_cache_filename, expire_after=datetime.timedelta(days=30))

# Set up the CURIE converter
converter = load_converter(["bioportal", "obo"])

converter.add_prefix("ENV", "http://purl.obolibrary.org/obo/ENVO_", merge=True)
converter.add_prefix("ENV0", "http://purl.obolibrary.org/obo/ENVO_", merge=True)
converter.add_prefix("EVNO", "http://purl.obolibrary.org/obo/ENVO_", merge=True)
converter.add_prefix("SNOMED", "http://purl.bioontology.org/ontology/SNOMEDCT/", merge=True)

# Define ontology mapping configuration
map_to = {
    "DOID",
    "ENVO",
    "FOODON",
    "MONDO",
    "NCBITAXON",
    "PO",
    "UBERON",
}
dont_map_from = {
    "BFO",
    "IAO",
    # TODO: Verify where `OF:*` CURIEs originate in source metadata (likely malformed/truncated prefixes).
    # If they are invalid, keep `OF` in `dont_map_from`; if valid, add explicit normalization/mapping and
    # remove `OF` from this ignore list to allow BioPortal CURIE mapping.
    "OF",
    "RO",
}
ignore = list(map_to | dont_map_from)


def deduplicate_dicts(lst: List[Dict]) -> List[Dict]:
    seen = set()
    result = []
    for d in lst:
        # Convert dict to a tuple of sorted key-value pairs
        items = tuple(sorted(d.items()))
        if items not in seen:
            seen.add(items)
            result.append(d)
    return result


def safe_expand(curie):
    """
    Expand a CURIE string using the configured converter.

    Args:
        curie (str): A CURIE identifier to expand.

    Returns:
        str | None: The expanded URI string if expansion succeeds; otherwise
        None when expansion fails (for example, invalid input or unknown prefix).
    """
    try:
        return converter.expand(curie.upper())
    except Exception:
        return None


def get_bioportal_info(term_uri, prefix, api_key):
    """
    Get term information from BioPortal given a term URI and ontology prefix.
    Returns a dict that includes the mappings_link and the full response data.
    """
    ontology = prefix.upper()
    encoded_uri = urllib.parse.quote(term_uri, safe="")
    url = f"https://data.bioontology.org/ontologies/{ontology}/classes/{encoded_uri}"
    headers = {"Authorization": f"apikey token={api_key}"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        mappings_link = data.get("links", {}).get("mappings")
        return {"mappings_link": mappings_link, "data": data}
    except requests.exceptions.RequestException as e:
        logger.warning(
            "BioPortal request failed for term_uri=%s prefix=%s: %s",
            term_uri,
            prefix,
            e,
        )
        return None
    except ValueError as e:
        logger.warning(
            "BioPortal response JSON decode failed for term_uri=%s prefix=%s: %s",
            term_uri,
            prefix,
            e,
        )
        return None


def get_mapped_term_info(self_link, api_key):
    """
    Given a mapped term's self link, fetch its details from BioPortal.
    Returns the JSON data.
    """
    url = self_link
    headers = {"Authorization": f"apikey token={api_key}"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.warning("Mapped term request failed for self_link: %s", e)
        return {}
    except ValueError as e:
        logger.warning("Mapped term JSON decode failed for self_link: %s", e)
        return {}


def fetch_mappings(mappings_url, api_key, verbose=False):
    """
    Fetch LOOM-type mappings from BioPortal using the mappings_link.
    """
    try:
        if "?" in mappings_url:
            full_url = mappings_url + f"&apikey={api_key}"
        else:
            full_url = mappings_url + f"?apikey={api_key}"
        if verbose:
            logger.debug("Following BioPortal mappings link")
        response = requests.get(full_url, timeout=10)
        response.raise_for_status()
        mappings_obj = response.json()
        loom_count = 0
        accepted_mappings = []
        map_to_upper = {m.upper() for m in map_to}
        for item in mappings_obj:
            if item.get("source") != "LOOM":
                continue
            loom_count += 1
            classes = item.get("classes", [])
            if len(classes) < 2:
                continue
            # Use the second class as the mapped target
            target_cls = classes[1]
            class_links = target_cls.get("links", {})
            ontology_url = class_links.get("ontology", "")
            if not ontology_url:
                continue
            ontology_id = ontology_url.rstrip("/").split("/")[-1].upper()
            mapped_curie = converter.compress(target_cls["@id"])
            if not mapped_curie:
                continue
            mapped_prefix = mapped_curie.split(":")[0]
            if mapped_prefix.upper() in map_to_upper and ontology_id in map_to_upper:
                self_link = class_links.get("self")
                mapped_info = get_mapped_term_info(self_link, api_key) if self_link else {}
                if mapped_info.get("prefLabel"):
                    mapping_obj = {
                        "curie": mapped_curie,
                        "prefix": mapped_prefix,
                        "label_lc": mapped_info.get("prefLabel").lower(),
                        "obsolete": mapped_info.get("obsolete", False)
                    }

                    accepted_mappings.append(mapping_obj)
        accepted_mappings = deduplicate_dicts(accepted_mappings)
        if verbose:
            pprint.pprint(accepted_mappings)
        return accepted_mappings
    except Exception:
        return []


def process_document(doc, collection, api_key, verbose=False):
    """
    Process a document: expand its CURIE, fetch BioPortal info, and update the document with fetched data and mappings.
    Verbose mode emits generic progress messages without logging CURIEs, labels, or URLs.
    """
    curie = doc.get("curie_uc")

    term_uri = safe_expand(curie)
    if term_uri:
        if verbose:
            print(f"Expansion success: {curie} -> {term_uri}")
    else:
        if verbose:
            print(f"Expansion failed for CURIE: {curie}")
        return

    reverse_engineered = converter.compress(term_uri)
    reverse_engineered_prefix = reverse_engineered.split(":")[0]

    bioportal_info = get_bioportal_info(term_uri, reverse_engineered_prefix, api_key)
    if not bioportal_info:
        # print(f"Failed to fetch BioPortal info for CURIE: {curie}")
        return

    data = bioportal_info["data"]
    pref_label = data.get("prefLabel")
    if verbose:
        logger.debug("Fetched BioPortal preferred label")

    update_fields = {
        "label": pref_label,
        "obsolete": data.get("obsolete", False)
    }

    if bioportal_info.get("mappings_link"):
        mappings_url = bioportal_info["mappings_link"]
        accepted_mappings = fetch_mappings(mappings_url, api_key, verbose)
        if accepted_mappings:
            update_fields["mappings"] = accepted_mappings

    collection.update_one({"_id": doc["_id"]}, {"$set": update_fields})


@click.command()
@click.option('--mongo-uri', default='mongodb://localhost:27017/ncbi_metadata', help='MongoDB connection URI (must start with mongodb:// and include database name)')
@click.option('--env-file', default='local/.env', help='Path to .env file for credentials (should contain MONGO_USER, MONGO_PASSWORD, and BIOPORTAL_API_KEY)')
@click.option('--collection', default='env_triad_component_curies_uc', help='MongoDB collection name')
@click.option('--verbose', is_flag=True, help='Show verbose connection and processing output')
def main(mongo_uri, env_file, collection, verbose):
    # Load environment variables from .env file
    load_dotenv(env_file)
    
    # Get BIOPORTAL_API_KEY from environment
    BIOPORTAL_API_KEY = os.environ.get("BIOPORTAL_API_KEY")
    if not BIOPORTAL_API_KEY:
        raise Exception(f"Please set the BIOPORTAL_API_KEY environment variable in {env_file}")
    
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
        
    mongo_collection = client[db_name][collection]

    # Build query for documents to process
    query = {
        "prefix_uc": {
            "$nin": ignore
        },
        "curie_uc": {
            "$ne": None
        }
    }

    # Get all documents matching the query
    docs_cursor = mongo_collection.find(query)
    doc_count = mongo_collection.count_documents(query)

    print(f"Found {doc_count} documents to process")

    # Process each document. Each call may make multiple BioPortal API requests,
    # so wrap the iteration in tqdm for a visible progress bar.
    for doc in tqdm(docs_cursor, total=doc_count, desc="BioPortal mapping", unit="doc"):
        process_document(doc, mongo_collection, BIOPORTAL_API_KEY, verbose)

    print("Processing complete.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python
import os
import urllib.parse
from pymongo import MongoClient
import requests
import requests_cache
from dotenv import load_dotenv

# Load environment variables from local/.env file (make sure BIOPORTAL_API_KEY is defined)
load_dotenv("local/.env")
BIOPORTAL_API_KEY = os.environ.get("BIOPORTAL_API_KEY")
if not BIOPORTAL_API_KEY:
    raise Exception("Please set the BIOPORTAL_API_KEY environment variable in local/.env.")

# Enable requests caching (expires after 7 days)
requests_cache.install_cache("requests_cache", expire_after=6048000)

# Load the converter using prefixmaps (assumes you have the curies and prefixmaps packages installed)
from prefixmaps.io.parser import load_converter

converter = load_converter(["bioportal", "obo"])

# Connect to MongoDB (adjust the URL if necessary)
mongo_url = "mongodb://localhost:27017"
client = MongoClient(mongo_url)
db = client.ncbi_metadata
collection = db.env_triad_component_in_scope_curies_lc


def safe_expand(curie):
    """Expand a CURIE using the converter."""
    try:
        return converter.expand(curie.upper())
    except Exception as e:
        print(f"CURIE: {curie} - Expansion error: {e}")
        return None


def get_bioportal_info(term_uri, prefix):
    """
    Get term information from BioPortal given a term URI and ontology prefix.
    Returns a dict that includes the mappings_link and the full response data.
    """
    ontology = prefix.upper()
    encoded_uri = urllib.parse.quote(term_uri, safe="")
    url = f"https://data.bioontology.org/ontologies/{ontology}/classes/{encoded_uri}?apikey={BIOPORTAL_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        mappings_link = data.get("links", {}).get("mappings")
        return {"mappings_link": mappings_link, "data": data}
    except Exception as e:
        print(f"Error fetching BioPortal info for {term_uri}: {e}")
        return None


def get_mapped_term_info(self_link):
    """
    Given a mapped term's self link, fetch its details from BioPortal.
    Returns the JSON data.
    """
    if "?" in self_link:
        url = self_link + f"&apikey={BIOPORTAL_API_KEY}"
    else:
        url = self_link + f"?apikey={BIOPORTAL_API_KEY}"
    # print(f"Following mapping self link: {url}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching mapped term info from {self_link}: {e}")
        return {}


def fetch_mappings(mappings_url):
    """
    Fetch LOOM-type mappings from BioPortal using the mappings_link.
    Returns a tuple: (accepted_mappings, counts) where counts is a dict containing:
       - total: total mapping items in response,
       - loom: number of mapping items with source 'LOOM',
       - accepted: number of LOOM mappings that passed the overlap check,
       - overlap: True if any accepted mapping's id overlapped with its links.ontology.
    """
    try:
        if "?" in mappings_url:
            full_url = mappings_url + f"&apikey={BIOPORTAL_API_KEY}"
        else:
            full_url = mappings_url + f"?apikey={BIOPORTAL_API_KEY}"
        print(f"Following mappings URL: {full_url}")
        response = requests.get(full_url, timeout=10)
        response.raise_for_status()
        mappings_obj = response.json()
        total_count = len(mappings_obj) if isinstance(mappings_obj, list) else 0
        loom_count = 0
        accepted_mappings = []
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
            ontology_url = class_links.get("ontology", "").lower()
            mapped_curie = converter.compress(target_cls["@id"])
            if not mapped_curie:
                continue
            mapped_prefix = mapped_curie.split(":")[0]
            if mapped_prefix.lower() in ontology_url:
                self_link = class_links.get("self")
                if self_link:
                    # print(f"Following mapping self link: {self_link}")
                    pass
                mapped_info = get_mapped_term_info(self_link) if self_link else {}
                mapping_obj = {
                    "curie": mapped_curie,
                    "prefix": mapped_prefix,
                    "prefLabel": mapped_info.get("prefLabel"),
                    "synonyms": mapped_info.get("synonym", []),
                    "obsolete": mapped_info.get("obsolete", False)
                }
                accepted_mappings.append(mapping_obj)
        accepted_count = len(accepted_mappings)
        overlap_found = accepted_count > 0
        return accepted_mappings, {
            "total": total_count,
            "loom": loom_count,
            "accepted": accepted_count,
            "overlap": overlap_found
        }
    except Exception as e:
        print(f"Error fetching mappings from {mappings_url}: {e}")
        return [], {"total": 0, "loom": 0, "accepted": 0, "overlap": False}


def process_document(doc):
    """
    Process a document: expand its CURIE, fetch BioPortal info, and update the document with fetched data and mappings.
    Logs a summary message with the CURIE, expansion status, the prefLabel from BioPortal, and mapping details.
    """
    curie = doc.get("curie_lc")
    print(f"Processing CURIE: {curie}")

    term_uri = safe_expand(curie)
    if term_uri:
        print(f"Expansion success: {curie} -> {term_uri}")
    else:
        print(f"Expansion failed for CURIE: {curie}")
        return

    bioportal_info = get_bioportal_info(term_uri, doc.get("prefix", ""))
    if not bioportal_info:
        print(f"Failed to fetch BioPortal info for CURIE: {curie}")
        return

    data = bioportal_info["data"]
    pref_label = data.get("prefLabel")
    print(f"BioPortal prefLabel for {curie}: {pref_label}")

    update_fields = {
        "prefLabel": pref_label,
        "synonyms": data.get("synonym", []),
        "obsolete": data.get("obsolete", False)
    }

    mapping_summary = ""
    if bioportal_info.get("mappings_link"):
        mappings_url = bioportal_info["mappings_link"]
        accepted_mappings, counts = fetch_mappings(mappings_url)
        mapping_summary = (
            f"Total mappings in response: {counts['total']}; "
            f"LOOM mappings encountered: {counts['loom']}; "
            f"Accepted LOOM mappings: {counts['accepted']}; "
            f"Overlap found: {'Yes' if counts['overlap'] else 'No'}"
        )
        if accepted_mappings:
            update_fields["mappings"] = accepted_mappings
    else:
        mapping_summary = "No mappings_link available."

    print(f"CURIE: {curie} - {mapping_summary}")
    collection.update_one({"_id": doc["_id"]}, {"$set": update_fields})


def main():
    query = {
        "prefix": {"$nin": ["ENVO"]},
        # "count": {"$gte": 1},
        # "$or": [{"label": {"$exists": False}}, {"label": {"$in": [None, ""]}}]
    }
    docs_cursor = collection.find(query)
    for doc in docs_cursor:
        process_document(doc)


if __name__ == "__main__":
    main()

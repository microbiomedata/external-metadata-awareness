import os
import urllib.parse
from pymongo import MongoClient
import requests
import requests_cache
from dotenv import load_dotenv
from prefixmaps.io.parser import load_converter
import pprint
from typing import List, Dict

# Load environment variables from local/.env file (make sure BIOPORTAL_API_KEY is defined)
load_dotenv("local/.env")
BIOPORTAL_API_KEY = os.environ.get("BIOPORTAL_API_KEY")
if not BIOPORTAL_API_KEY:
    raise Exception("Please set the BIOPORTAL_API_KEY environment variable in local/.env.")

# Enable requests caching (expires after 7 days)
requests_cache.install_cache("requests_cache", expire_after=6048000)

converter = load_converter(["bioportal", "obo"])

converter.add_prefix("ENV", "http://purl.obolibrary.org/obo/ENVO_", merge=True)
converter.add_prefix("ENV0", "http://purl.obolibrary.org/obo/ENVO_", merge=True)
converter.add_prefix("EVNO", "http://purl.obolibrary.org/obo/ENVO_", merge=True)
converter.add_prefix("SNOMED", "http://purl.bioontology.org/ontology/SNOMEDCT/", merge=True)

# Connect to MongoDB
mongo_url = "mongodb://localhost:27017"
client = MongoClient(mongo_url)
db = client.ncbi_metadata
collection = db.env_triad_component_curies_uc

map_to = {"ENVO", "FOODON", "MONDO", "NCBITAXON", "PO", "UBERON", }
dont_map_from = {
    "BFO",
    "IAO",
    "RO",
    "OF",  # todo garbage CURIes? double check where they come from
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
    """Expand a CURIE using the converter."""
    try:
        return converter.expand(curie.upper())
    except Exception as e:
        # print(f"CURIE: {curie} - Expansion error: {e}")
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
        # print(f"Error fetching BioPortal info for {url}: {e}")
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
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        # print(f"Error fetching mapped term info from {self_link}: {e}")
        return {}


def fetch_mappings(mappings_url):
    """
    Fetch LOOM-type mappings from BioPortal using the mappings_link.
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
            if mapped_prefix.upper() in map_to and ontology_url.upper() in ontology_url.upper():
                self_link = class_links.get("self")
                mapped_info = get_mapped_term_info(self_link) if self_link else {}
                if mapped_info.get("prefLabel"):
                    mapping_obj = {
                        "curie": mapped_curie,
                        "prefix": mapped_prefix,
                        "label_lc": mapped_info.get("prefLabel").lower(),
                        "obsolete": mapped_info.get("obsolete", False)
                    }

                    accepted_mappings.append(mapping_obj)
        accepted_mappings = deduplicate_dicts(accepted_mappings)
        pprint.pprint(accepted_mappings)
        return accepted_mappings
    except Exception as e:
        # print(f"Error fetching mappings from {mappings_url}: {e}")
        return []


def process_document(doc):
    """
    Process a document: expand its CURIE, fetch BioPortal info, and update the document with fetched data and mappings.
    Logs a summary message with the CURIE, expansion status, the prefLabel from BioPortal, and mapping details.
    """
    curie = doc.get("curie_uc")

    term_uri = safe_expand(curie)
    if term_uri:
        print(f"Expansion success: {curie} -> {term_uri}")
    else:
        print(f"Expansion failed for CURIE: {curie}")
        return

    reverse_engineered = converter.compress(term_uri)
    reverse_engineered_prefix = reverse_engineered.split(":")[0]

    bioportal_info = get_bioportal_info(term_uri, reverse_engineered_prefix)
    if not bioportal_info:
        # print(f"Failed to fetch BioPortal info for CURIE: {curie}")
        return

    data = bioportal_info["data"]
    pref_label = data.get("prefLabel")
    print(f"BioPortal prefLabel for {curie}: {pref_label}")

    update_fields = {
        "label": pref_label,
        "obsolete": data.get("obsolete", False)
    }

    if bioportal_info.get("mappings_link"):
        mappings_url = bioportal_info["mappings_link"]
        accepted_mappings = fetch_mappings(mappings_url)
        if accepted_mappings:
            update_fields["mappings"] = accepted_mappings

    collection.update_one({"_id": doc["_id"]}, {"$set": update_fields})


def main():
    query = {
        "prefix_uc": {
            "$nin": ignore
        },
        "curie_uc": {
            "$ne": None
        }
    }

    docs_cursor = collection.find(query)

    for doc in docs_cursor:
        process_document(doc)


if __name__ == "__main__":
    main()

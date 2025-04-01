#!/usr/bin/env python3
"""
Generalized script to update env_triad_component_in_scope_curies_lc documents:
For each document whose "prefix" field (case-insensitive) is one of ENVO, UBERON, or PO, this script:
  - Normalizes the stored CURIE (in the "curie_uc" field) so that the prefix is upper-case.
  - Uses the corresponding OAK adapter (configured via a semantic SQL database) to retrieve the term’s label
    and check if the term is obsolete.
  - Updates the document by adding the "label" and "obsolete" fields.

Before running, ensure that:
  • Your MongoDB connection details (database name, collection, etc.) are correct.
  • The OAK adapter strings match your semantic SQL configurations.
"""

from pymongo import MongoClient
from oaklib import get_adapter
from tqdm import tqdm


def attempt_oak_labelling(curie, adapter):
    """
    Attempts to get the label for a given CURIE using the provided OAK adapter.
    Also checks if the term is obsolete.

    Returns a dict with the CURIE, label, and obsolete status if found;
    otherwise returns None.
    """
    label = adapter.label(curie)
    if label:
        try:
            obsolete = adapter.is_obsolete(curie)
        except Exception:
            obsolete = False
        return {"curie": curie, "label": label, "obsolete": obsolete}
    return None


def process_documents(collection, query, adapter, ontology_name):
    """
    Processes documents matching the given query.
    For each document:
      - Normalizes the CURIE.
      - Uses the provided adapter to fetch the label and obsolete status.
      - Updates the document with these fields.
    """
    total = collection.count_documents(query)
    print(f"Found {total} documents with prefix '{ontology_name.lower()}'.")
    cursor = collection.find(query)

    for doc in tqdm(cursor, total=total, desc=f"Processing {ontology_name} documents"):
        curie_uc = doc.get("curie_uc")
        if not curie_uc:
            continue

        # Normalize the CURIE: if it starts with the lower-case prefix, convert it to upper-case.
        prefix, sep, local_id = curie_uc.partition(":")
        if sep and prefix.lower() == ontology_name.lower():
            canonical_curie = f"{ontology_name.upper()}:{local_id}"
        else:
            canonical_curie = curie_uc

        # Retrieve label and obsolete status using the OAK adapter.
        result = attempt_oak_labelling(canonical_curie, adapter)
        if result:
            update_fields = {"label": result["label"], "obsolete": result["obsolete"]}
        else:
            update_fields = {"label": None, "obsolete": None}

        collection.update_one({"_id": doc["_id"]}, {"$set": update_fields})


def main():
    # MongoDB connection configuration.
    mongo_url = "mongodb://localhost:27017"
    client = MongoClient(mongo_url)
    db = client.ncbi_metadata
    collection = db.env_triad_component_curies_uc

    # Define the ontologies and their corresponding OAK adapter strings.
    ontologies = {
        "agro": "sqlite:obo:agro",
        "bco": "sqlite:obo:bco",
        "bto": "sqlite:obo:bto",
        "chebi": "sqlite:obo:chebi",
        "doid": "sqlite:obo:doid",
        "ecto": "sqlite:obo:ecto",
        "efo": "sqlite:obo:efo",
        "envo": "sqlite:obo:envo",
        "eupath": "sqlite:obo:eupath",
        "fma": "sqlite:obo:fma",
        "foodon": "sqlite:obo:foodon",
        "go": "sqlite:obo:go",
        "ma": "sqlite:obo:ma",
        "mco": "sqlite:obo:mco",
        "mondo": "sqlite:obo:mondo",
        "mp": "sqlite:obo:mp",
        "ncbitaxon": "sqlite:obo:ncbitaxon",
        "ncit": "sqlite:obo:ncit",
        "obi": "sqlite:obo:obi",
        "ohmi": "sqlite:obo:ohmi",
        "omit": "sqlite:obo:omit",
        "pato": "sqlite:obo:pato",
        "pco": "sqlite:obo:pco",
        "po": "sqlite:obo:po",
        "uberon": "sqlite:obo:uberon",
        "vto": "sqlite:obo:vto",
        "xao": "sqlite:obo:xao",
        "zfa": "sqlite:obo:zfa",
    }

    for ontology, adapter_string in ontologies.items():
        adapter = get_adapter(adapter_string)
        query = {"prefix_uc": {"$regex": f"^{ontology}$", "$options": "i"}}
        process_documents(collection, query, adapter, ontology)

    print("Processing complete.")


if __name__ == '__main__':
    main()

import datetime
import os
import re
import string

import click
import requests
import requests_cache
import yaml
from oaklib import get_adapter
from tqdm import tqdm

from external_metadata_awareness.mongodb_connection import get_mongo_client

# todo doesnt' address ENV or ENV0 prefixes, but they are rare
# seeing OF and TO prefixes that are defined in Bioportal. I'm suspicious.

requests_cache_filename = "external-metadata-awareness-requests-cache"

# Precompiled regex patterns (assumed global in your file; repeated here for clarity).
from external_metadata_awareness.env_triad_parsing import (
    bracketed_pattern,
    extract_components,
    improved_curie_pattern,
    is_digits_only,
    make_plain_component,
    normalize_label,
    trailing_curie_pattern,
)

obo_registry_yaml_url = "https://raw.githubusercontent.com/OBOFoundry/OBOFoundry.github.io/refs/heads/master/registry/ontologies.yml"


@click.command()
@click.option('--mongo-uri', required=True, help='MongoDB connection URI (must start with mongodb:// and include database name)')
@click.option('--env-file', default=None, help='Path to .env file for credentials (should contain MONGO_USER and MONGO_PASSWORD)')
@click.option('--collection', required=True, help='MongoDB collection name')
@click.option('--field', default='env_triad_value', help='Field to parse')
@click.option('--min-length', default=0, type=int, help='Minimum value of the length field to include a document')
@click.option('--verbose', is_flag=True, help='Show verbose connection output')
def main(mongo_uri, env_file, collection, field, min_length, verbose):
    # Use the unified MongoDB connection utility
    client = get_mongo_client(
        mongo_uri=mongo_uri,
        env_file=env_file,
        debug=verbose
    )
    
    # Extract database name from URI using pymongo's uri_parser
    from pymongo import uri_parser
    parsed = uri_parser.parse_uri(mongo_uri)
    db_name = parsed.get('database')
    
    if not db_name:
        raise ValueError("MongoDB URI must include a database name")
        
    coll = client[db_name][collection]

    envo_adapter_string = "sqlite:obo:envo"
    envo_adapter = get_adapter(envo_adapter_string)
    all_envo_curies_and_iris = set(envo_adapter.entities())

    obo_reg_resp = requests.get(obo_registry_yaml_url)
    obo_reg_resp.raise_for_status()  # Raises an error for bad status codes

    obo_reg = yaml.safe_load(obo_reg_resp.text)['ontologies']

    obo_ontology_indicators_lc = set()
    for i in obo_reg:
        if 'id' in i and len(i['id'].strip()) > 0:
            obo_ontology_indicators_lc.add(i['id'].strip().lower())
        if 'preferredPrefix' in i and len(i['preferredPrefix'].strip()) > 0:
            obo_ontology_indicators_lc.add(i['preferredPrefix'].strip().lower())

    # Create a cache that lasts for 30 days
    requests_cache.install_cache(requests_cache_filename, expire_after=datetime.timedelta(days=30))

    BIOPORTAL_API_KEY = os.getenv("BIOPORTAL_API_KEY")

    bioportal_ontologies_url = f"https://data.bioontology.org/ontologies?apikey={BIOPORTAL_API_KEY}"

    bioportal_ontologies_resp = requests.get(bioportal_ontologies_url)

    bioportal_ontologies = bioportal_ontologies_resp.json()

    bioportal_ontology_indicators_lc = set()

    for i in bioportal_ontologies:
        if 'acronym' in i and len(i['acronym'].strip()) > 0:
            bioportal_ontology_indicators_lc.add(i['acronym'].strip().lower())

    known_prefixes = {x.upper() for x in (obo_ontology_indicators_lc or [])} | {x.upper() for x in (
            bioportal_ontology_indicators_lc or [])}

    known_prefixes.discard("OF")
    known_prefixes.discard("GUT")
    known_prefixes.discard("RHIZOSPHERE")

    docs = list(coll.find({
        "$and": [
            {field: {"$exists": True}},
            {
                "$or": [
                    {"digits_only": {"$exists": False}},
                    {"digits_only": False}
                ]
            },
            {
                "$or": [
                    {"equation_like": {"$exists": False}},
                    {"equation_like": False}
                ]
            },
            {
                "$or": [
                    {"insdc_missing_match": {"$exists": False}},
                    {"insdc_missing_match": False}
                ]
            },
            {
                "$or": [
                    {"other_missing_indicator": {"$exists": False}},
                    {"insdc_missing_match": False}
                ]
            },
            {"length": {"$gte": min_length}}
        ]
    }))

    for doc in tqdm(docs, desc="Parsing and updating"):
        value = doc.get(field)
        parsed = extract_components(value, known_envo_curies=all_envo_curies_and_iris,
                                    obo_ontology_indicators_lc=obo_ontology_indicators_lc,
                                    bioportal_ontology_indicators_lc=bioportal_ontology_indicators_lc,
                                    known_prefixes=known_prefixes)

        for comp in parsed:
            if comp.get("prefix_uc") and comp.get("local"):
                comp["curie_uc"] = f"{comp['prefix_uc']}:{comp['local'].upper()}"
            else:
                comp["curie_uc"] = None
            if comp["label"]:
                comp["label_length"] = len(comp["label"])
            else:
                comp["label_length"] = 0

        coll.update_one(
            {"_id": doc["_id"]},
            {"$set": {
                "components": parsed,
                "components_count": len(parsed)
            }}
        )

    print(f"Updated {len(docs)} documents in '{collection}' collection.")


if __name__ == '__main__':
    main()

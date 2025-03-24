import os
import re
import urllib.parse
import click
from pymongo import MongoClient
from dotenv import load_dotenv
from tqdm import tqdm
import string
from oaklib import get_adapter
import yaml
import requests
import requests_cache

strict_curie_pattern = re.compile(
    r"""
    (?P<raw>
        (?P<label>[^\[\(\]:_]*)?                   # optional label before the CURIE
        [\[\(]?\s*                                 # optional opening bracket
        (?P<prefix>[A-Z][A-Z0-9]+)                 # prefix (uppercase)
        [:\-_\s\uFF1A]+                                     # colon, underscore, or space(s)
        (?P<local>[A-Za-z0-9]{2,})                 # local ID
        \s*[\]\)]?                                 # optional closing bracket
    )
    """,
    re.VERBOSE
)

obo_registry_yaml_url = "https://raw.githubusercontent.com/OBOFoundry/OBOFoundry.github.io/refs/heads/master/registry/ontologies.yml"


def is_digits_only(label):
    return label.isdigit()


def normalize_label(label):
    # Convert to lowercase
    label = label.lower()
    # Replace punctuation and underscore with space
    label = re.sub(rf"[{re.escape(string.punctuation)}]", " ", label)
    # Normalize whitespace
    label = re.sub(r"\s+", " ", label).strip()
    return label


def extract_components(text, known_envo_curies=None, obo_ontology_indicators_lc=None,
                       bioportal_ontology_indicators_lc=None):
    if not isinstance(text, str):
        return []

    components = []
    annotations = text.split('|')

    for ann in annotations:
        matches = list(strict_curie_pattern.finditer(ann))
        if matches:
            for m in matches:
                prefix = m.group('prefix').upper().strip()
                local = m.group('local').strip()
                full_curie = f"{prefix}:{local}"
                label = m.group('label')

                if prefix.upper() == "ENVO" and known_envo_curies and full_curie.upper() not in known_envo_curies:
                    ann_split = ann.split(':', 1)
                    if len(ann_split) == 2:
                        label = normalize_label(ann_split[1])
                    else:
                        label = None
                    components.append({
                        'raw': ann,
                        'label': label,
                        'prefix': prefix,
                        'local': None,
                        'digits_only': is_digits_only(local) if local else False,
                        'lingering_envo': "ENVO" in label.upper() if label else False,
                        'uses_obo_prefix': prefix.lower() in obo_ontology_indicators_lc if obo_ontology_indicators_lc else False,
                        'uses_bioportal_prefix': prefix.lower() in bioportal_ontology_indicators_lc if bioportal_ontology_indicators_lc else False,
                    })
                else:
                    # Valid CURIE
                    label = normalize_label(label) if label else None
                    components.append({
                        'raw': ann,
                        'label': label,
                        'prefix': prefix,
                        'local': local,
                        'digits_only': is_digits_only(local) if local else False,
                        'lingering_envo': "ENVO" in label.upper() if label else False,
                        'uses_obo_prefix': prefix.lower() in obo_ontology_indicators_lc if obo_ontology_indicators_lc else False,
                        'uses_bioportal_prefix': prefix.lower() in bioportal_ontology_indicators_lc if bioportal_ontology_indicators_lc else False,
                    })
        else:
            components.append({
                'raw': ann,
                'label': None,
                'prefix': None,
                'local': None,
                'digits_only': is_digits_only(ann) if ann else False,
                'lingering_envo': "ENVO" in ann.upper() if ann else False,
                'uses_obo_prefix': False,
                'uses_bioportal_prefix': False,
            })

    return components


@click.command()
@click.option('--host', default='mongo-ncbi-loadbalancer.mam.production.svc.spin.nersc.org', help='MongoDB host')
@click.option('--port', default=27017, type=int, help='MongoDB port')
@click.option('--db', required=True, help='MongoDB database name')
@click.option('--collection', required=True, help='MongoDB collection name')
@click.option('--field', default='env_triad_value', help='Field to parse')
@click.option('--env-file', default='../.env', help='Path to .env file')
@click.option('--min-length', default=0, type=int, help='Minimum value of the length field to include a document')
def main(host, port, db, collection, field, env_file, min_length):
    load_dotenv(env_file)

    username = urllib.parse.quote_plus(os.getenv("MONGO_NCBI_LOADBALANCER_WRITING_USERNAME"))
    password = urllib.parse.quote_plus(os.getenv("MONGO_NCBI_LOADBALANCER_WRITING_PW"))

    auth_source = "admin"
    auth_mechanism = "SCRAM-SHA-256"
    extra_params = "directConnection=true"

    mongo_uri = (
        f"mongodb://{username}:{password}@{host}:{port}/"
        f"?authSource={auth_source}&authMechanism={auth_mechanism}&{extra_params}"
    )

    client = MongoClient(mongo_uri)
    coll = client[db][collection]

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

    # Create a cache that lasts for 1 hour (3600 seconds)
    requests_cache.install_cache('new_env_triad_values_splitter_cache', expire_after=3600)  # 1 hour

    BIOPORTAL_API_KEY = os.getenv("BIOPORTAL_API_KEY")

    bioportal_ontologies_url = f"https://data.bioontology.org/ontologies?apikey={BIOPORTAL_API_KEY}"

    bioportal_ontologies_resp = requests.get(bioportal_ontologies_url)

    bioportal_ontologies = bioportal_ontologies_resp.json()

    bioportal_ontology_indicators_lc = set()

    for i in bioportal_ontologies:
        if 'acronym' in i and len(i['acronym'].strip()) > 0:
            bioportal_ontology_indicators_lc.add(i['acronym'].strip().lower())

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
            {"length": {"$gte": min_length}}
        ]
    }))

    for doc in tqdm(docs, desc="Parsing and updating"):
        value = doc.get(field)
        parsed = extract_components(value, known_envo_curies=all_envo_curies_and_iris,
                                    obo_ontology_indicators_lc=obo_ontology_indicators_lc,
                                    bioportal_ontology_indicators_lc=bioportal_ontology_indicators_lc)

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

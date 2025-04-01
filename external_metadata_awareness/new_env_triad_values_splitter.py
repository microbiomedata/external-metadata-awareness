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

# todo doesnt' address ENV or ENV0 prefixes, but they are rare
# seeing OF and TO prefixes that are defined in Bioportal. I'm suspicios.

# Precompiled regex patterns (assumed global in your file; repeated here for clarity).
improved_curie_pattern = re.compile(
    r"""
    ^                                   # start of string
    (?:(?P<label_before>.*?)(?:(?<=[a-z])(?=[A-Z])|\s+|(?=[\[\(\{])))?  # optional label before
    (?:[\[\(\{])?                       # optional opening bracket
    (?P<prefix>[A-Za-z][A-Za-z0-9]+)      # prefix
    [:\-_ \uFF1A]+                      # one or more separators
    (?P<local>[A-Za-z0-9]{2,})           # local identifier
    (?:\s*[\]\)\}])?                    # optional closing bracket
    (?:(?:\s*[:\-_ \uFF1A]\s*)(?P<label_after>.+))?  # optional label after
    $                                   # end of string
    """, re.VERBOSE
)

bracketed_pattern = re.compile(
    r"""
    (?P<label>.*?)\s*            # capture any text before the bracket as the label
    [\[\(\{]                    # opening bracket
    (?P<prefix>[A-Za-z][A-Za-z0-9]+)   # prefix
    [:\-_ \uFF1A]+             # separator(s)
    (?P<local>[A-Za-z0-9]{2,})   # local identifier
    \s*[\]\)\}]                # closing bracket
    """, re.VERBOSE
)

trailing_curie_pattern = re.compile(
    r"""
    ^(?P<label>.*?)\s+                   # any text at start as the label (non-greedy)
    (?P<prefix>[A-Za-z][A-Za-z0-9]+)       # prefix
    [:\-_ \uFF1A]+                       # separator(s)
    (?P<local>[A-Za-z0-9]{2,})\s*$         # local identifier until end-of-string
    """, re.VERBOSE
)

obo_registry_yaml_url = "https://raw.githubusercontent.com/OBOFoundry/OBOFoundry.github.io/refs/heads/master/registry/ontologies.yml"


def make_plain_component(ann):
    norm = normalize_label(ann)
    return {
        'label': norm,
        'label_digits_only': is_digits_only(norm),
        'lingering_envo': ("envo" in norm),
        'local': None,
        'local_digits_only': False,
        'prefix_uc': None,
        'raw': ann,
        'uses_bioportal_prefix': False,
        'uses_obo_prefix': False,
    }


def is_digits_only(label):
    if label:
        return label.isdigit()
    else:
        return False


def normalize_label(label):
    # Convert to lowercase
    label = label.lower()
    # Replace punctuation and underscore with space
    label = re.sub(rf"[{re.escape(string.punctuation)}]", " ", label)
    # Normalize whitespace
    label = re.sub(r"\s+", " ", label).strip()
    return label


def extract_components(text,
                       known_envo_curies=None,
                       obo_ontology_indicators_lc=None,
                       bioportal_ontology_indicators_lc=None,
                       known_prefixes=None):
    if not isinstance(text, str):
        return []

    components = []

    # Pre-clean the text.
    text = text.strip().strip('“”"\'')
    text = re.sub(r'\b(ENVO:){2,}', 'ENVO:', text, flags=re.IGNORECASE)

    # If text contains a bracketed CURIE, use that branch.
    if re.search(r'[\[\(\{].+[\]\)\}]', text):
        found = False
        for m in bracketed_pattern.finditer(text):
            found = True
            raw = m.group(0)
            label = m.group('label').strip() if m.group('label') else None
            if label:
                label = normalize_label(label)
            components.append({
                'label': label,
                'label_digits_only': is_digits_only(label) if label else False,
                'lingering_envo': (("ENVO" in label.upper()) if label else False),
                'local': m.group('local'),
                'local_digits_only': is_digits_only(m.group('local')),
                'prefix_uc': m.group('prefix').upper() if m.group('prefix') else None,
                'raw': raw,
                'uses_bioportal_prefix': (bioportal_ontology_indicators_lc and
                                          m.group('prefix').upper() in {x.upper() for x in
                                                                        bioportal_ontology_indicators_lc}),
                'uses_obo_prefix': (obo_ontology_indicators_lc and
                                    m.group('prefix').upper() in {x.upper() for x in obo_ontology_indicators_lc}),
            })
        if found:
            return components
        return [make_plain_component(text)]

    # Otherwise, split text on delimiters (pipe, semicolon, comma).
    annotations = re.split(r'\|+|;+|,+', text)
    for ann in annotations:
        ann = ann.strip()
        if not ann:
            continue

        # If no obvious separator is found, treat as plain text.
        if not any(sep in ann for sep in [":", "-", "_", "\uFF1A"]):
            components.append(make_plain_component(ann))
            continue

        ann = ann.strip('“”"\'')
        ann = re.sub(r'\b(ENVO:){2,}', 'ENVO:', ann, flags=re.IGNORECASE)

        # If the annotation ends with a CURIE-like pattern, force use of the trailing matcher.
        if re.search(r'\s+[A-Za-z][A-Za-z0-9]+[:\-_ \uFF1A][A-Za-z0-9]{2,}\s*$', ann):
            m = trailing_curie_pattern.match(ann)
        else:
            m = improved_curie_pattern.match(ann)

        if m:
            candidate_prefix = m.group('prefix').upper()
            # Validate the prefix using the passed-in known_prefixes.
            if candidate_prefix not in known_prefixes:
                components.append(make_plain_component(ann))
                continue

            prefix = candidate_prefix
            local = m.group('local')
            label = None
            if "label_after" in m.groupdict() and m.group('label_after'):
                label = m.group('label_after')
            elif "label_before" in m.groupdict() and m.group('label_before'):
                label = m.group('label_before')
            elif "label" in m.groupdict():
                label = m.group('label')
            if label:
                label = normalize_label(label)
            components.append({
                'label': label,
                'label_digits_only': is_digits_only(label) if label else False,
                'lingering_envo': False,
                'local': local,
                'local_digits_only': is_digits_only(local),
                'prefix_uc': prefix,
                'raw': ann,
                'uses_bioportal_prefix': (bioportal_ontology_indicators_lc and
                                          prefix in {x.upper() for x in bioportal_ontology_indicators_lc}),
                'uses_obo_prefix': (obo_ontology_indicators_lc and
                                    prefix in {x.upper() for x in obo_ontology_indicators_lc}),
            })
        else:
            components.append(make_plain_component(ann))

    if not components and text.strip():
        components.append(make_plain_component(text))
    return components


@click.command()
@click.option('--host', default='mongo-ncbi-loadbalancer.mam.production.svc.spin.nersc.org', help='MongoDB host')
@click.option('--port', default=27017, type=int, help='MongoDB port')
@click.option('--db', required=True, help='MongoDB database name')
@click.option('--collection', required=True, help='MongoDB collection name')
@click.option('--field', default='env_triad_value', help='Field to parse')
@click.option('--authenticate/--no-authenticate', default=True)
@click.option('--env-file', default='../.env', help='Path to .env file')
@click.option('--min-length', default=0, type=int, help='Minimum value of the length field to include a document')
def main(host, port, db, collection, field, env_file, min_length, authenticate):
    if authenticate:
        load_dotenv(env_file)

        # todo too much hard coding/assumptions
        username = urllib.parse.quote_plus(os.getenv("MONGO_NCBI_LOADBALANCER_WRITING_USERNAME"))
        password = urllib.parse.quote_plus(os.getenv("MONGO_NCBI_LOADBALANCER_WRITING_PW"))
        auth_source = "admin"
        auth_mechanism = "SCRAM-SHA-256"
        extra_params = "directConnection=true"

        mongo_uri = (
            f"mongodb://{username}:{password}@{host}:{port}/?authSource={auth_source}&authMechanism={auth_mechanism}&{extra_params}"
        )
    else:
        mongo_uri = (
            f"mongodb://{host}:{port}/"
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

    # Create a cache that lasts for 30 days
    import datetime
    requests_cache.install_cache('new_env_triad_values_splitter_cache', expire_after=datetime.timedelta(days=30))

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

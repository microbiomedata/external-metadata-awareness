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

improved_curie_pattern = re.compile(
    r"""
    ^                                   # start of string
    (?:(?P<label_before>.*?)(?:(?<=[a-z])(?=[A-Z])|\s+|(?=[\[\(\{])))?  # optional label before; stop if whitespace or an opening bracket/parenthesis/curly bracket is seen
    (?:[\[\(\{])?                       # optional opening bracket (square, round, or curly)
    (?P<prefix>[A-Za-z][A-Za-z0-9]+)      # prefix (allowing mixed case)
    [:\-_ \uFF1A]+                      # one or more separators (colon, dash, underscore, space, or fullwidth colon)
    (?P<local>[A-Za-z0-9]{2,})           # local identifier (at least 2 alphanumerics)
    (?:\s*[\]\)\}])?                    # optional closing bracket (allowing any of ], ), or })
    (?:(?:\s*[:\-_ \uFF1A]\s*)(?P<label_after>.+))?  # optional label after if preceded by a separator
    $                                   # end of string
    """,
    re.VERBOSE
)

# Updated pattern for the multi-bracket branch.
bracketed_pattern = re.compile(
    r"""
    (?P<label>.*?)\s*            # capture any text before the bracket as the label (non-greedy)
    [\[\(\{]                    # opening bracket: square, round, or curly
    (?P<prefix>[A-Za-z][A-Za-z0-9]+)   # prefix (mixed case allowed)
    [:\-_ \uFF1A]+             # one or more separators
    (?P<local>[A-Za-z0-9]{2,})   # local identifier
    \s*[\]\)\}]                # optional whitespace then a closing bracket (any of ], ), or })
    """,
    re.VERBOSE
)

obo_registry_yaml_url = "https://raw.githubusercontent.com/OBOFoundry/OBOFoundry.github.io/refs/heads/master/registry/ontologies.yml"


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


def extract_components(text, known_envo_curies=None, obo_ontology_indicators_lc=None,
                       bioportal_ontology_indicators_lc=None):
    if not isinstance(text, str):
        return []

    components = []

    # Pre-clean the text:
    text = text.strip()
    # Remove leading/trailing quotation marks (including fancy quotes)
    text = text.strip('“”"\'')
    # Collapse repeated ENVO prefixes (e.g. "ENVO:ENVO:" becomes "ENVO:")
    text = re.sub(r'\b(ENVO:){2,}', 'ENVO:', text, flags=re.IGNORECASE)

    # If the text appears to contain multiple bracketed CURIEs, use the dedicated branch.
    if re.search(r'[\[\(\{]', text) and len(re.findall(r'[\[\(\{]', text)) > 1:
        found_any = False
        for m in bracketed_pattern.finditer(text):
            found_any = True
            raw = m.group(0)
            label = m.group('label').strip() if m.group('label') else None
            if label:
                label = normalize_label(label)
            components.append({
                # lingering_envo now only flags if extra "envo" is present in the label (if any)
                'label': label,
                'label_digits_only': is_digits_only(label) if label else False,
                'lingering_envo': (("ENVO" in label.upper()) if label else False),
                'local': m.group('local'),
                'local_digits_only': is_digits_only(m.group('local')) if m.group('local') else False,
                'prefix_uc': m.group('prefix').upper() if m.group('prefix') else None,
                'raw': raw,
                'uses_bioportal_prefix': bioportal_ontology_indicators_lc and m.group('prefix').upper() in {x.upper()
                                                                                                            for x in
                                                                                                            bioportal_ontology_indicators_lc},
                'uses_obo_prefix': obo_ontology_indicators_lc and m.group('prefix').upper() in {x.upper() for x in
                                                                                                obo_ontology_indicators_lc},

            })
        if found_any:
            return components
        # Fallback if no match was found:
        components.append({
            'label': normalize_label(text),
            'label_digits_only': is_digits_only(normalize_label(text)),
            'lingering_envo': "ENVO" in text.upper(),
            'local': None,
            'local_digits_only': False,
            'prefix_uc': None,
            'raw': text,
            'uses_bioportal_prefix': False,
            'uses_obo_prefix': False,
        })
        return components

    # Otherwise, split the text on pipe, semicolon, or comma.
    annotations = re.split(r'\|+|;+|,+', text)
    for ann in annotations:
        ann = ann.strip()
        if not ann:
            continue
        # Add the check: if no separator is found, treat as plain text
        if not any(sep in ann for sep in [":", "-", "_", "\uFF1A"]):
            components.append({
                'label': normalize_label(ann),
                'label_digits_only': is_digits_only(normalize_label(ann)),
                'lingering_envo': "ENVO" in ann.upper(),
                'local': None,
                'local_digits_only': False,
                'prefix_uc': None,
                'raw': ann,
                'uses_bioportal_prefix': False,
                'uses_obo_prefix': False,
            })
            continue
        # Continue with existing pre-cleaning and regex matching
        ann = ann.strip('“”"\'')
        ann = re.sub(r'\b(ENVO:){2,}', 'ENVO:', ann, flags=re.IGNORECASE)
        m = improved_curie_pattern.match(ann)
        if m:
            candidate_prefix = m.group('prefix').upper()
            known_prefixes = set(x.upper() for x in (obo_ontology_indicators_lc or [])) | set(
                x.upper() for x in (bioportal_ontology_indicators_lc or []))
            if candidate_prefix not in known_prefixes:
                # Candidate prefix isn’t recognized; treat as plain text.
                components.append({
                    'label': normalize_label(ann),
                    'label_digits_only': is_digits_only(normalize_label(ann)),
                    'lingering_envo': "ENVO" in ann.upper(),
                    'local': None,
                    'local_digits_only': False,
                    'prefix_uc': None,
                    'raw': ann,
                    'uses_bioportal_prefix': False,
                    'uses_obo_prefix': False,
                })
                continue
            # Otherwise, proceed with the usual CURIE parsing…
            prefix = candidate_prefix
            local = m.group('local')
            label_after = m.group('label_after')
            label_before = m.group('label_before')
            label = label_after if label_after is not None else label_before
            if label:
                label = normalize_label(label)
            components.append({
                'label': label,
                'label_digits_only': is_digits_only(label),
                'lingering_envo': (("ENVO" in (label.upper() if label else "")) if label else False),
                'local': local,
                'local_digits_only': is_digits_only(local) if local else False,
                'prefix_uc': prefix.upper(),
                'raw': ann,
                'uses_bioportal_prefix': bioportal_ontology_indicators_lc and prefix in {x.upper() for x in
                                                                                         bioportal_ontology_indicators_lc},
                'uses_obo_prefix': obo_ontology_indicators_lc and prefix in {x.upper() for x in
                                                                             obo_ontology_indicators_lc},

            })
        else:
            components.append({
                'label': normalize_label(ann),
                'label_digits_only': is_digits_only(normalize_label(ann)) if ann else False,
                'lingering_envo': "ENVO" in ann.upper(),
                'local': None,
                'local_digits_only': False,
                'prefix_uc': None,
                'raw': ann,
                'uses_bioportal_prefix': False,
                'uses_obo_prefix': False,
            })
    if not components and text.strip():
        components.append({
            'label': normalize_label(text),
            'label_digits_only': is_digits_only(normalize_label(text)) if text else False,
            'lingering_envo': "ENVO" in text.upper(),
            'local': None,
            'local_digits_only': False,
            'prefix_uc': None,
            'raw': text,
            'uses_bioportal_prefix': False,
            'uses_obo_prefix': False,
        })
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
                                    bioportal_ontology_indicators_lc=bioportal_ontology_indicators_lc)

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

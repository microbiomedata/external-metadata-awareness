#!/usr/bin/env python3
import re
import csv
from tqdm import tqdm
from pymongo import MongoClient
from linkml_runtime import SchemaView
from oaklib import get_adapter


# ------------------------------------------------------------------
# Ontology and Schema Helper Functions
# ------------------------------------------------------------------

def build_ontology_adapters(ontology_names):
    """
    Creates ontology adapters for the given ontology names.
    :param ontology_names: List of ontology names (e.g., ["envo", "pato", "uberon"])
    :return: Dictionary mapping ontology names to ontology adapters
    """
    adapters = {}
    for ontology in tqdm(ontology_names, desc="Building ontology adapters"):
        adapters[ontology] = get_adapter(f"sqlite:obo:{ontology}")
    return adapters


def generate_label_cache(entities, adapter, ontology_name):
    """
    Generates a label cache mapping CURIEs to their labels.
    :param entities: List of ontology entities (CURIEs)
    :param adapter: Ontology adapter to fetch labels
    :param ontology_name: Name of the ontology (for tqdm label)
    :return: Dictionary mapping CURIEs to labels
    """
    temp_label_cache = {}
    for curie in tqdm(entities, desc=f"Generating label cache for {ontology_name}"):
        label = adapter.label(curie)  # Fetch label for CURIE
        if label:  # Only store if a valid label exists
            temp_label_cache[curie] = label
    return temp_label_cache


def load_ontology_labels(ont_adapters):
    """
    Loads ontology entity labels from multiple ontologies and aggregates their label caches.
    :param ont_adapters: Dictionary mapping ontology names to ontology adapters
    :return: Aggregated label cache dictionary
    """
    aggregated_label_cache = {}
    for ontology, adapter in tqdm(ont_adapters.items(), desc="Loading ontology labels"):
        entities = sorted(list(adapter.entities()))  # Fetch and sort entities
        tmp_cache = generate_label_cache(entities, adapter, ontology)
        aggregated_label_cache.update(tmp_cache)  # Merge into a single cache
    return aggregated_label_cache


def parse_label_curie(text):
    """
    Parses a string with an optional leading underscore, followed by a label and a CURIE inside square brackets.
    Example input: "________mediterranean savanna biome [ENVO:01000229]"
    :param text: The input string to parse
    :return: A dictionary {'label': <label>, 'curie': <curie>} if successful, else None
    """
    pattern = r"^_*(?P<label>[^\[\]]+)\s*\[(?P<curie>[^\[\]]+)\]$"
    match = re.match(pattern, text.strip())
    if match:
        return {
            "label": match.group("label").strip(),
            "curie": match.group("curie").strip()
        }
    return None


def parse_env_context_field(text):
    """
    Parses an environmental context field to extract label and CURIE (id) components.
    Expected formats include:
      "alpine tundra biome [ENVO:01001505]"
      "alpine tundra biome (ENVO_01001505)"
      "ENVO:01001505"
      "alpine tundra biome"
    The CURIE may use a colon or an underscore, and may be wrapped in square brackets or parentheses.
    Any leading underscores in the label are removed.

    :param text: The environmental context string.
    :return: A dict with keys "label" and "curie". If a part is missing, its value is None.
    """
    if not text or not text.strip():
        return {"label": None, "curie": None}
    text = text.strip()
    # First, try to match a pattern with brackets or parentheses.
    pattern = r"^(?P<label>.*?)\s*[\[\(](?P<curie>[A-Z0-9]+[:_][A-Z0-9]+)[\]\)]$"
    match = re.match(pattern, text, re.IGNORECASE)
    if match:
        label = match.group("label").strip() or None
        # Remove any leading underscores from the label
        if label:
            label = label.lstrip('_')
        curie = match.group("curie").strip() or None
        return {"label": label, "curie": curie}
    # Next, search anywhere in the string for a CURIE pattern.
    pattern2 = r"(?P<curie>[A-Z0-9]+[:_][A-Z0-9]+)"
    match2 = re.search(pattern2, text, re.IGNORECASE)
    if match2:
        curie = match2.group("curie").strip()
        # Remove the found CURIE from the text to use the remainder as a label candidate.
        label_candidate = text.replace(match2.group("curie"), "").strip(" -[]()")
        label_candidate = label_candidate.lstrip('_') if label_candidate else None
        return {"label": label_candidate, "curie": curie}
    # Fallback: treat the entire text as a label if no CURIE pattern is found.
    return {"label": text.lstrip('_'), "curie": None}


def find_obsolete_terms(ont_adapters):
    """
    Identifies obsolete terms from multiple ontologies using their adapters.
    :param ont_adapters: Dictionary mapping ontology names to ontology adapters
    :return: List of CURIEs for obsolete terms
    """
    tmp_obsolete_curies = []
    for ontology, adapter in tqdm(ont_adapters.items(), desc="Finding obsolete terms"):
        tmp_obsolete_curies.extend(adapter.obsoletes())  # Use ontology access kit function
    return tmp_obsolete_curies


def flatten_sample(sample):
    """
    Collapse any list values in the sample dictionary to a pipe-delimited string.
    Also, merge keys with bracket notation (e.g. "analysis_type[0]", "analysis_type[1]") into a single key.
    """
    flattened = {}
    for key, value in sample.items():
        # Check for keys with bracket notation, e.g. "analysis_type[0]"
        m = re.match(r"^(.*)\[\d+\]$", key)
        if m:
            base_key = m.group(1)
            flattened.setdefault(base_key, []).append(value)
        else:
            # If key already exists (from merged bracket keys), merge the values
            if key in flattened:
                if isinstance(flattened[key], list):
                    flattened[key].append(value)
                else:
                    flattened[key] = [flattened[key], value]
            else:
                flattened[key] = value

    # Convert any list values into a pipe-delimited string
    for key, value in flattened.items():
        if isinstance(value, list):
            flattened[key] = "|".join(str(item) for item in value)
    return flattened


# ------------------------------------------------------------------
# Ontology and Schema Setup
# ------------------------------------------------------------------

# Load NMDC schema using LinkML SchemaView
nmdc_schema_url = (
    "https://raw.githubusercontent.com/microbiomedata/nmdc-schema/"
    "refs/heads/main/nmdc_schema/nmdc_materialized_patterns.yaml"
)
nmdc_schema_view = SchemaView(nmdc_schema_url)
nmdc_schema_usage_index = nmdc_schema_view.usage_index()  # This is a defaultdict

# Extract usage for ControlledTermValue and ControlledIdentifiedTermValue
ctv_usage = nmdc_schema_usage_index['ControlledTermValue']
citv_usage = nmdc_schema_usage_index['ControlledIdentifiedTermValue']

# Build a set of slots that use ControlledTermValue
ctv_using_slots = set()
for usage in ctv_usage:
    ctv_using_slots.add(usage.slot)
print(f"Found {len(ctv_using_slots)} slots using ControlledTermValue.")

# Define keys to check for labels in non-environmental fields
to_label_check = [
    'env_broad_scale.id', 'env_local_scale.id', 'env_medium.id',
    'env_broad_scale.term.id', 'env_local_scale.term.id', 'env_medium.term.id',
    'envoBroadScale.id', 'envoLocalScale.id', 'envoLocalScale.id',
]

ever_seen = set()  # Set to store all values found in to_label_check slots

# Build ontology adapters and load label caches
ontology_list = ["envo", "pato", "uberon"]
ontology_adapters = build_ontology_adapters(ontology_list)
label_cache = load_ontology_labels(ontology_adapters)
obsolete_terms_list = find_obsolete_terms(ontology_adapters)


# ------------------------------------------------------------------
# MongoDB Processing and TSV Insertion
# ------------------------------------------------------------------

def process_submissions():
    # Connect to your local MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    submissions_db = client['misc_metadata']
    submissions_collection = submissions_db['nmdc_submissions']

    submission_biosamples = []
    skip_templates = [
        'emsl_data',
        'host_associated_data',
        'jgi_mg_data',
        'jgi_mg_lr_data',
        'jgi_mt_data',
    ]

    total_docs = submissions_collection.count_documents({})
    # Iterate through each document in the submissions collection
    for doc in tqdm(submissions_collection.find(), total=total_docs, desc="Processing submissions"):
        if 'metadata_submission' in doc and 'sampleData' in doc['metadata_submission']:
            sample_data = doc['metadata_submission']['sampleData']
            # Iterate over each category in sampleData
            for key, sample_list in tqdm(sample_data.items(), total=len(sample_data),
                                         desc=f"Processing sample data for submission {doc.get('id')}"):
                if key in skip_templates:
                    continue
                if isinstance(sample_list, list):
                    for sample in tqdm(sample_list, desc=f"Samples in category '{key}'", leave=False):
                        # Process each key-value pair in the sample
                        for k, v in list(sample.items()):
                            if k in ctv_using_slots:
                                parsed_label_curie = parse_label_curie(v)
                                if parsed_label_curie:
                                    sample[f"{k}_id"] = parsed_label_curie['curie']
                                    sample[f"{k}_claimed_label"] = parsed_label_curie['label']

                        if isinstance(sample, dict):
                            # Create a copy of the sample and add extra fields
                            sample_with_id = sample.copy()
                            sample_with_id['sampleData'] = key  # Category of sampleData
                            sample_with_id['submission_id'] = doc.get('id')
                            sample_with_id['created'] = doc.get('created')
                            sample_with_id['date_last_modified'] = doc.get('date_last_modified')
                            sample_with_id['status'] = doc.get('status')
                            # Flatten the sample to collapse list values and merge bracket-indexed keys
                            flattened_sample = flatten_sample(sample_with_id)
                            submission_biosamples.append(flattened_sample)

    # Post-process each sample for additional label checks (non-environmental fields)
    for sample in tqdm(submission_biosamples, desc="Post-processing biosamples"):
        for key in to_label_check:
            if key in sample:
                ever_seen.add(sample[key])
                if sample[key] in label_cache:  # Check if the value is a CURIE in the cache
                    sample[f"{key}_canonical_label"] = label_cache[sample[key]]
                sample[f"{key}_obsolete"] = (sample[key] in obsolete_terms_list)

    # Process environmental context fields specially
    environmental_fields = ["env_broad_scale", "env_local_scale", "env_medium"]
    for sample in tqdm(submission_biosamples, desc="Processing environmental context fields"):
        for field in environmental_fields:
            if field in sample and sample[field]:
                parsed = parse_env_context_field(sample[field])
                sample[f"{field}_parsed_label"] = parsed["label"]
                sample[f"{field}_parsed_curie"] = parsed["curie"]
                if parsed["curie"] and parsed["curie"] in label_cache:
                    sample[f"{field}_canonical_label"] = label_cache[parsed["curie"]]
                sample[f"{field}_obsolete"] = (parsed["curie"] in obsolete_terms_list)
                # New column to check if parsed label matches canonical label
                sample[f"{field}_match"] = (parsed["label"] == sample.get(f"{field}_canonical_label"))

    # Write the processed samples to a TSV file with sorted columns
    if submission_biosamples:
        # Determine the union of all keys for the TSV header and sort them
        all_keys = set()
        for sample in submission_biosamples:
            all_keys.update(sample.keys())
        all_keys = sorted(all_keys)

        tsv_filename = 'flattened_submission_biosamples.tsv'
        with open(tsv_filename, 'w', newline='', encoding='utf-8') as tsvfile:
            writer = csv.DictWriter(tsvfile, fieldnames=all_keys, delimiter='\t')
            writer.writeheader()
            writer.writerows(submission_biosamples)
        print(f"TSV file '{tsv_filename}' written successfully.")

    # Insert the processed samples into the flattened_submission_biosamples collection
    flattened_collection = submissions_db['flattened_submission_biosamples']
    if submission_biosamples:
        insert_result = flattened_collection.insert_many(submission_biosamples)
        print(
            f"Inserted {len(insert_result.inserted_ids)} documents into 'flattened_submission_biosamples' collection.")


def main():
    process_submissions()


if __name__ == '__main__':
    main()

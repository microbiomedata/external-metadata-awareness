#!/usr/bin/env python3
import re
import csv
import json
import click
import requests
from datetime import datetime
from dotenv import dotenv_values
from tqdm import tqdm
from pymongo import MongoClient
from linkml_runtime import SchemaView
from oaklib import get_adapter


# =============================================================================
# FETCH NMDC SUBMISSIONS FROM THE API
# =============================================================================
def fetch_nmdc_submissions(mongo_url, env_path):
    """
    Fetch NMDC submissions from the API and insert them into the MongoDB
    collection 'nmdc_submissions' in the 'misc_metadata' database.
    """
    # Load environment variables from .env file
    env_vars = dotenv_values(env_path)
    refresh_token = env_vars.get('NMDC_DATA_SUBMISSION_REFRESH_TOKEN')
    if not refresh_token:
        click.echo("NMDC_DATA_SUBMISSION_REFRESH_TOKEN not found in env.")
        return False

    # Refresh token to get an access token
    url_auth = 'https://data.microbiomedata.org/auth/refresh'
    payload = {"refresh_token": refresh_token}
    auth_headers = {'Content-Type': 'application/json'}
    response = requests.post(url_auth, data=json.dumps(payload), headers=auth_headers)
    if response.status_code == 200:
        access_token = response.json().get('access_token')
        click.echo(f"Access Token: {access_token}")
    else:
        click.echo(f"Failed to get access token: {response.status_code}")
        click.echo(response.text)
        return False

    # Set up API call for metadata submissions
    url_submissions = 'https://data.microbiomedata.org/api/metadata_submission'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'column_sort': 'created',
        'sort_order': 'desc',
        'offset': 0,
        'limit': 25
    }

    # Connect to MongoDB
    client = MongoClient(mongo_url)
    # Use provided database or default to 'misc_metadata'
    db_name = client.get_database().name or 'misc_metadata'
    db = client[db_name]
    collection = db['nmdc_submissions']

    # Paginate through API results
    while True:
        click.echo(f"Request sent at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        response = requests.get(url_submissions, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            if not results:
                break

            # Insert fetched submissions into MongoDB
            collection.insert_many(results)

            # Check if we've fetched all records based on the reported total count
            total_count = data.get('count')
            if total_count and collection.count_documents({}) >= total_count:
                break

            # Move to the next page
            params['offset'] += params['limit']
        else:
            click.echo(f"Failed to fetch submissions: {response.status_code}")
            click.echo(response.text)
            break

    return True


# =============================================================================
# ONTOLOGY AND SCHEMA HELPER FUNCTIONS
# =============================================================================
def build_ontology_adapters(ontology_names):
    """
    Creates ontology adapters for the given ontology names.
    """
    adapters = {}
    for ontology in tqdm(ontology_names, desc="Building ontology adapters"):
        adapters[ontology] = get_adapter(f"sqlite:obo:{ontology}")
    return adapters


def generate_label_cache(entities, adapter, ontology_name):
    """
    Generates a label cache mapping CURIEs to their labels.
    """
    temp_label_cache = {}
    for curie in tqdm(entities, desc=f"Generating label cache for {ontology_name}"):
        label = adapter.label(curie)
        if label:
            temp_label_cache[curie] = label
    return temp_label_cache


def load_ontology_labels(ont_adapters):
    """
    Aggregates label caches from multiple ontology adapters.
    """
    aggregated_label_cache = {}
    for ontology, adapter in tqdm(ont_adapters.items(), desc="Loading ontology labels"):
        entities = sorted(list(adapter.entities()))
        tmp_cache = generate_label_cache(entities, adapter, ontology)
        aggregated_label_cache.update(tmp_cache)
    return aggregated_label_cache


def parse_label_curie(text):
    """
    Parses a string with an optional leading underscore, followed by a label and a CURIE inside square brackets.
    Example: "________mediterranean savanna biome [ENVO:01000229]"
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
    Parses an environmental context field to extract label and CURIE components.
    Handles formats like:
      "alpine tundra biome [ENVO:01001505]"
      "alpine tundra biome (ENVO_01001505)"
      "ENVO:01001505"
      "alpine tundra biome"
    Removes any leading underscores from the label.
    """
    if not text or not text.strip():
        return {"label": None, "curie": None}
    text = text.strip()
    pattern = r"^(?P<label>.*?)\s*[\[\(](?P<curie>[A-Z0-9]+[:_][A-Z0-9]+)[\]\)]$"
    match = re.match(pattern, text, re.IGNORECASE)
    if match:
        label = match.group("label").strip() or None
        if label:
            label = label.lstrip('_')
        curie = match.group("curie").strip() or None
        return {"label": label, "curie": curie}
    pattern2 = r"(?P<curie>[A-Z0-9]+[:_][A-Z0-9]+)"
    match2 = re.search(pattern2, text, re.IGNORECASE)
    if match2:
        curie = match2.group("curie").strip()
        label_candidate = text.replace(match2.group("curie"), "").strip(" -[]()")
        label_candidate = label_candidate.lstrip('_') if label_candidate else None
        return {"label": label_candidate, "curie": curie}
    return {"label": text.lstrip('_'), "curie": None}


def find_obsolete_terms(ont_adapters):
    """
    Identifies obsolete terms from the given ontology adapters.
    """
    tmp_obsolete_curies = []
    for ontology, adapter in tqdm(ont_adapters.items(), desc="Finding obsolete terms"):
        tmp_obsolete_curies.extend(adapter.obsoletes())
    return tmp_obsolete_curies


def flatten_sample(sample):
    """
    Collapses list values in the sample dictionary to a pipe-delimited string.
    Merges keys with bracket notation (e.g. "analysis_type[0]") into a single key.
    """
    flattened = {}
    for key, value in sample.items():
        m = re.match(r"^(.*)\[\d+\]$", key)
        if m:
            base_key = m.group(1)
            flattened.setdefault(base_key, []).append(value)
        else:
            if key in flattened:
                if isinstance(flattened[key], list):
                    flattened[key].append(value)
                else:
                    flattened[key] = [flattened[key], value]
            else:
                flattened[key] = value
    for key, value in flattened.items():
        if isinstance(value, list):
            flattened[key] = "|".join(str(item) for item in value)
    return flattened


# =============================================================================
# MONGODB PROCESSING & TSV EXPORT
# =============================================================================
def process_submissions(mongo_url, output_file):
    """
    Processes the NMDC submissions stored in MongoDB, performs flattening,
    environmental context parsing and label checks, then exports to TSV and
    inserts the flattened documents into a target collection.
    """
    # Load schema and setup ontology variables
    nmdc_schema_url = (
        "https://raw.githubusercontent.com/microbiomedata/nmdc-schema/refs/heads/main/nmdc_schema/nmdc_materialized_patterns.yaml"
    )
    nmdc_schema_view = SchemaView(nmdc_schema_url)
    nmdc_schema_usage_index = nmdc_schema_view.usage_index()

    # Build set of slots that use ControlledTermValue
    ctv_usage = nmdc_schema_usage_index['ControlledTermValue']
    ctv_using_slots = {usage.slot for usage in ctv_usage}
    click.echo(f"Found {len(ctv_using_slots)} slots using ControlledTermValue.")

    # Define non-environmental label-check keys
    to_label_check = [
        'env_broad_scale.id', 'env_local_scale.id', 'env_medium.id',
        'env_broad_scale.term.id', 'env_local_scale.term.id', 'env_medium.term.id',
        'envoBroadScale.id', 'envoLocalScale.id', 'envoLocalScale.id',
    ]
    ever_seen = set()

    # Build ontology adapters and load labels/obsolete terms
    ontology_list = ["envo", "pato", "uberon"]
    ontology_adapters = build_ontology_adapters(ontology_list)
    label_cache = load_ontology_labels(ontology_adapters)
    obsolete_terms_list = find_obsolete_terms(ontology_adapters)

    # Connect to MongoDB
    client = MongoClient(mongo_url)
    # Use provided database or default to 'misc_metadata'
    db_name = client.get_database().name or 'misc_metadata'
    submissions_db = client[db_name]
    submissions_collection = submissions_db['nmdc_submissions']

    submission_biosamples = []
    skip_templates = [
        'emsl_data', 'host_associated_data', 'jgi_mg_data', 'jgi_mg_lr_data', 'jgi_mt_data'
    ]

    total_docs = submissions_collection.count_documents({})
    for doc in tqdm(submissions_collection.find(), total=total_docs, desc="Processing submissions"):
        if 'metadata_submission' in doc and 'sampleData' in doc['metadata_submission']:
            sample_data = doc['metadata_submission']['sampleData']
            for key, sample_list in tqdm(sample_data.items(), total=len(sample_data),
                                         desc=f"Submission {doc.get('id')} sampleData processing"):
                if key in skip_templates:
                    continue
                if isinstance(sample_list, list):
                    for sample in tqdm(sample_list, desc=f"Processing samples in '{key}'", leave=False):
                        for k, v in list(sample.items()):
                            if k in ctv_using_slots:
                                parsed = parse_label_curie(v)
                                if parsed:
                                    sample[f"{k}_id"] = parsed['curie']
                                    sample[f"{k}_claimed_label"] = parsed['label']
                        if isinstance(sample, dict):
                            sample_with_id = sample.copy()
                            sample_with_id['sampleData'] = key
                            sample_with_id['submission_id'] = doc.get('id')
                            sample_with_id['created'] = doc.get('created')
                            sample_with_id['date_last_modified'] = doc.get('date_last_modified')
                            sample_with_id['status'] = doc.get('status')
                            flattened_sample = flatten_sample(sample_with_id)
                            submission_biosamples.append(flattened_sample)

    # Additional label checks for non-environmental fields
    for sample in tqdm(submission_biosamples, desc="Post-processing biosamples"):
        for key in to_label_check:
            if key in sample:
                ever_seen.add(sample[key])
                if sample[key] in label_cache:
                    sample[f"{key}_canonical_label"] = label_cache[sample[key]]
                sample[f"{key}_obsolete"] = (sample[key] in obsolete_terms_list)

    # Process environmental context fields
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
                # Check if parsed label matches canonical label
                sample[f"{field}_match"] = (parsed["label"] == sample.get(f"{field}_canonical_label"))

    # Write flattened samples to a TSV file with sorted columns
    if submission_biosamples:
        all_keys = set()
        for sample in submission_biosamples:
            all_keys.update(sample.keys())
        all_keys = sorted(all_keys)
        with open(output_file, 'w', newline='', encoding='utf-8') as tsvfile:
            writer = csv.DictWriter(tsvfile, fieldnames=all_keys, delimiter='\t')
            writer.writeheader()
            writer.writerows(submission_biosamples)
        click.echo(f"TSV file '{output_file}' written successfully.")

    # Insert flattened samples into the target collection
    flattened_collection = submissions_db['flattened_submission_biosamples']
    if submission_biosamples:
        flattened_collection.delete_many({})  # Clear existing data
        insert_result = flattened_collection.insert_many(submission_biosamples)
        click.echo(
            f"Inserted {len(insert_result.inserted_ids)} documents into 'flattened_submission_biosamples' collection.")

    return True


# =============================================================================
# BIOSAMPLE ROWS TRANSFORMATION (AS IN THE NOTEBOOK)
# =============================================================================
def create_biosample_rows(mongo_url):
    """
    Transforms each submission's sampleData into individual biosample rows.
    Each row document includes the submission_id, the key (template name),
    and a list of field/value pairs from the row.
    Inserts the resulting documents into the collection 'submission_biosample_rows'.
    """
    client = MongoClient(mongo_url)
    # Use provided database or default to 'misc_metadata'
    db_name = client.get_database().name or 'misc_metadata'
    db = client[db_name]
    submissions_collection = db['nmdc_submissions']
    biosample_rows = []
    total_docs = submissions_collection.count_documents({})

    for record in tqdm(submissions_collection.find(), total=total_docs, desc="Creating biosample rows"):
        submission_id = record.get('id', 'N/A')
        sample_data = record.get('metadata_submission', {}).get('sampleData', {})
        for key, rows in sample_data.items():
            if isinstance(rows, list):
                for row in rows:
                    transformed_doc = {
                        "submission_id": submission_id,
                        "key": key,
                        "row_data": [{"field": field, "value": value} for field, value in row.items()]
                    }
                    biosample_rows.append(transformed_doc)

    biosample_rows_collection = db["submission_biosample_rows"]
    biosample_rows_collection.delete_many({})  # Clear existing data
    if biosample_rows:
        result = biosample_rows_collection.insert_many(biosample_rows)
        click.echo(f"Inserted {len(result.inserted_ids)} documents into 'submission_biosample_rows' collection.")

    return True


# =============================================================================
# AGGREGATION PIPELINE EXECUTION
# =============================================================================
def run_aggregation_pipeline(mongo_url):
    """
    Executes an aggregation pipeline on the 'submission_biosample_rows' collection.
    The pipeline unwinds the 'row_data' array, groups by each field in the row_data,
    projects the field and count, and writes the result to 'submission_biosample_slot_counts'.
    """
    client = MongoClient(mongo_url)
    # Use provided database or default to 'misc_metadata'
    db_name = client.get_database().name or 'misc_metadata'
    db = client[db_name]
    pipeline = [
        {"$unwind": "$row_data"},
        {"$group": {
            "_id": "$row_data.field",
            "count": {"$sum": 1}
        }},
        {"$project": {
            "_id": 0,
            "field": "$_id",
            "count": 1
        }},
        {"$out": "submission_biosample_slot_counts"}
    ]
    # Execute the aggregation pipeline.
    list(db.submission_biosample_rows.aggregate(pipeline))
    click.echo("Aggregation pipeline executed; output written to collection 'submission_biosample_slot_counts'.")

    return True


# =============================================================================
# CLI COMMANDS
# =============================================================================
@click.group()
def cli():
    """NMDC Data Submission Processing Tool.

    This tool fetches, processes, and analyzes NMDC data submissions.
    MongoDB is used for storage and processing.

    The MongoDB URL should be in the format:
    mongodb://[username:password@]host[:port]/database

    If no database is specified in the URL, 'misc_metadata' will be used as default.
    """
    pass


@cli.command('fetch')
@click.option('--mongo-url', required=True, help='MongoDB connection URL')
@click.option('--env-path', default="../../local/.env", help='Path to .env file containing auth tokens')
def fetch_cmd(mongo_url, env_path):
    """Fetch NMDC submissions from the API and store in MongoDB."""
    click.echo(f"Fetching NMDC submissions using {env_path} for auth tokens...")
    success = fetch_nmdc_submissions(mongo_url, env_path)
    if success:
        click.echo("Submissions fetched successfully.")
    else:
        click.echo("Failed to fetch submissions.")


@cli.command('process')
@click.option('--mongo-url', required=True, help='MongoDB connection URL')
@click.option('--output-file', default='flattened_submission_biosamples.tsv', help='Output TSV file path')
def process_cmd(mongo_url, output_file):
    """Process submissions to create flattened biosamples and export to TSV."""
    click.echo("Processing submissions...")
    success = process_submissions(mongo_url, output_file)
    if success:
        click.echo(f"Processed submissions successfully. Output written to {output_file}")
    else:
        click.echo("Failed to process submissions.")


@cli.command('create-rows')
@click.option('--mongo-url', required=True, help='MongoDB connection URL')
def create_rows_cmd(mongo_url):
    """Transform submissions into individual biosample rows."""
    click.echo("Creating biosample rows...")
    success = create_biosample_rows(mongo_url)
    if success:
        click.echo("Biosample rows created successfully.")
    else:
        click.echo("Failed to create biosample rows.")


@cli.command('aggregate')
@click.option('--mongo-url', required=True, help='MongoDB connection URL')
def aggregate_cmd(mongo_url):
    """Run aggregation pipeline on biosample rows."""
    click.echo("Running aggregation pipeline...")
    success = run_aggregation_pipeline(mongo_url)
    if success:
        click.echo("Aggregation pipeline executed successfully.")
    else:
        click.echo("Failed to execute aggregation pipeline.")


@cli.command('run-all')
@click.option('--mongo-url', required=True, help='MongoDB connection URL')
@click.option('--env-path', default="../../local/.env", help='Path to .env file containing auth tokens')
@click.option('--output-file', default='flattened_submission_biosamples.tsv', help='Output TSV file path')
def run_all_cmd(mongo_url, env_path, output_file):
    """Run the complete extraction and processing pipeline."""
    click.echo("Running the complete pipeline...")

    click.echo("\n1. Fetching submissions...")
    if not fetch_nmdc_submissions(mongo_url, env_path):
        click.echo("Failed to fetch submissions. Aborting pipeline.")
        return

    click.echo("\n2. Processing submissions...")
    if not process_submissions(mongo_url, output_file):
        click.echo("Failed to process submissions. Aborting pipeline.")
        return

    click.echo("\n3. Creating biosample rows...")
    if not create_biosample_rows(mongo_url):
        click.echo("Failed to create biosample rows. Aborting pipeline.")
        return

    click.echo("\n4. Running aggregation pipeline...")
    if not run_aggregation_pipeline(mongo_url):
        click.echo("Failed to run aggregation pipeline. Aborting pipeline.")
        return

    click.echo("\nComplete pipeline executed successfully!")


if __name__ == '__main__':
    cli()

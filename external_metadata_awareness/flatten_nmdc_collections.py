"""
Script to flatten NMDC collections into more easily queryable MongoDB collections.

This script creates the following collections from NMDC data:
  - flattened_biosample
  - flattened_biosample_chem_administration
  - flattened_biosample_field_counts
  - flattened_study
  - flattened_study_associated_dois
  - flattened_study_has_credit_associations

The flattening process:
1. Fetches data from NMDC API or local MongoDB
2. Flattens nested structures into dot-notation fields
3. Converts arrays to pipe-separated strings
4. Decorates environmental context fields with ontology information
5. Creates specialized collections for convenient querying

Usage:
  poetry run python external_metadata_awareness/flatten_nmdc_collections.py 
    [--mongo-host MONGO_HOST] [--mongo-port MONGO_PORT] [--mongo-db MONGO_DB]
"""

import json
import logging
import pathlib
import re
import sys
from typing import Dict, List, Set, Any, Optional

import click
import dotenv
from linkml_runtime import SchemaView
from oaklib import get_adapter
from pymongo import MongoClient
from tqdm import tqdm

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
NMDC_RUNTIME_API_BASE_URL = "https://api.microbiomedata.org/nmdcschema/"
NMDC_SCHEMA_URL = "https://raw.githubusercontent.com/microbiomedata/nmdc-schema/refs/heads/main/nmdc_schema/nmdc_materialized_patterns.yaml"


def fetch_all_documents_from_mongodb(client: MongoClient, db_name: str, collection_name: str) -> List[Dict]:
    """
    Fetch all documents from a specified MongoDB collection.

    Args:
        client: MongoDB client
        db_name: MongoDB database name
        collection_name: MongoDB collection name

    Returns:
        List of documents from the collection
    """
    # Ensure db_name and collection_name are strings
    db_name_str = str(db_name)
    collection_name_str = str(collection_name)
    
    db = client[db_name_str]
    collection = db[collection_name_str]
    
    count = collection.count_documents({})
    logger.info(f"Found {count} documents in {collection_name}")
    
    documents = []
    for doc in tqdm(collection.find({}), total=count, desc=f"Fetching {collection_name}"):
        # Remove MongoDB _id field
        if '_id' in doc:
            del doc['_id']
        documents.append(doc)
    
    return documents


def build_ontology_adapters(ontology_names: List[str]) -> Dict:
    """
    Creates ontology adapters for the given ontology names.

    Args:
        ontology_names: List of ontology names (e.g., ["envo", "pato", "uberon"])

    Returns:
        Dictionary mapping ontology names to ontology adapters
    """
    adapters = {}
    for ontology in tqdm(ontology_names, desc="Building ontology adapters"):
        adapters[ontology] = get_adapter(f"sqlite:obo:{ontology}")
    return adapters


def load_ontology_labels(ontology_adapters: Dict) -> Dict[str, str]:
    """
    Loads ontology entity labels from multiple ontologies and aggregates their label caches.

    Args:
        ontology_adapters: Dictionary mapping ontology names to ontology adapters

    Returns:
        Aggregated label cache dictionary
    """
    aggregated_label_cache = {}

    for ontology, adapter in tqdm(ontology_adapters.items(), desc="Loading ontology labels"):
        entities = sorted(list(adapter.entities()))  # Fetch and sort entities
        
        for curie in tqdm(entities, desc=f"Caching {ontology} labels", leave=False):
            label = adapter.label(curie)  # Fetch label for CURIE
            if label:  # Only store if a valid label exists
                aggregated_label_cache[curie] = label

    return aggregated_label_cache


def find_obsolete_terms(ontology_adapters: Dict) -> List[str]:
    """
    Identifies obsolete terms from multiple ontologies using their adapters.

    Args:
        ontology_adapters: Dictionary mapping ontology names to ontology adapters

    Returns:
        List of CURIEs for obsolete terms
    """
    obsolete_curies = []
    for ontology, adapter in tqdm(ontology_adapters.items(), desc="Finding obsolete terms"):
        obsolete_curies.extend(adapter.obsoletes())  # Use ontology access kit function
    return obsolete_curies


def parse_label_curie(text: str) -> Optional[Dict[str, str]]:
    """
    Parses a string with an optional leading underscore, followed by a label and a CURIE inside square brackets.

    Example input: "________mediterranean savanna biome [ENVO:01000229]"

    Args:
        text: The input string to parse
    
    Returns:
        A dictionary {'label': <label>, 'curie': <curie>} if successful, else None
    """
    if not text or not isinstance(text, str):
        return None
        
    pattern = r"^_*(?P<label>[^\[\]]+)\s*\[(?P<curie>[^\[\]]+)\]$"
    match = re.match(pattern, text.strip())

    if match:
        return {
            "label": match.group("label").strip(),
            "curie": match.group("curie").strip()
        }

    return None


def stringify(obj: Any) -> str:
    """
    Converts a list or dictionary into a string representation.
    - Uses JSON format with compact or pretty formatting based on the depth.
    - Sorts keys in dictionaries for consistency.

    Args:
        obj: Any object (list, dict, or other Python object)
    
    Returns:
        String representation
    """
    if isinstance(obj, (dict, list)):
        return json.dumps(obj, sort_keys=True, ensure_ascii=False)  # Compact format
    return str(obj)  # Fallback for other types


def stringify_singleton_dict_list(dict_list: List[Dict]) -> str:
    """
    Processes a list of dictionaries:
    - Removes the 'type' key from each dictionary.
    - Tracks the largest dictionary by key count (excluding 'type').
    - If the largest dictionary has only 1 key, extracts values, sorts them, and returns a pipe-concatenated string.
    - Otherwise, returns an empty string.

    Args:
        dict_list: List of dictionaries to process
    
    Returns:
        Pipe-concatenated sorted values if all dicts have at most one key (excluding 'type'), else an empty string.
    """
    if not isinstance(dict_list, list) or not all(isinstance(d, dict) for d in dict_list):
        return ""

    largest_key_count = 0
    processed_values = []

    for d in dict_list:
        cleaned_dict = {k: v for k, v in d.items() if k != "type"}  # Remove 'type'
        largest_key_count = max(largest_key_count, len(cleaned_dict))
        if len(cleaned_dict) == 1:  # If it only has one key, extract its value
            processed_values.append(next(iter(cleaned_dict.values())))

    # If the largest dictionary has only one key, return sorted pipe-concatenated string
    if largest_key_count == 1:
        return "|".join(map(str, sorted(processed_values)))  # Sort values before joining

    return ""  # Return empty string if dicts contain more than one unique key


def flatten(documents: List[Dict], ctv_slots: Optional[Set[str]] = None, known_skips: Optional[Set[str]] = None) -> List[Dict]:
    """
    Extracts scalar fields from documents, concatenating lists of scalars with a pipe ('|') separator.
    If a field contains a dictionary with only scalar values, it is flattened using 'outer_key_inner_key' notation
    (with underscore separator instead of period to avoid MongoDB field name issues).
    Lists of scalars within dictionaries are also pipe-concatenated.
    Skips 'type' fields.

    Special handling for ControlledIdentifiedTerm range slots like 'env_broad_scale', 'env_local_scale', and 'env_medium' etc.:
      - Extracts 'has_raw_value', 'term.id', and 'term.name' if available.

    Args:
        documents: List of documents (e.g., studies, biosamples)
        ctv_slots: Set of slots whose range is a ControlledTermValue or descendant
        known_skips: Set of slots that can't be stringified nicely
    
    Returns:
        List of dictionaries containing only scalar fields, with lists of scalars pipe-concatenated
    """
    if ctv_slots is None:
        ctv_slots = set()

    if known_skips is None:
        known_skips = set()

    scalar_docs = []
    problem_slots = set()

    for doc in tqdm(documents, desc="Flattening documents"):
        scalar_doc = {}
        stringified_singletons = ""  # Ensure fresh value per row

        for key, value in doc.items():
            if key == "type":
                continue  # Skip 'type' fields

            if key in known_skips:
                continue

            if isinstance(value, (str, int, float, bool, type(None))):
                scalar_doc[key] = value  # Keep scalars as-is

            elif isinstance(value, list) and all(
                    isinstance(item, (str, int, float, bool, type(None))) for item in value):
                scalar_doc[key] = "|".join(map(str, value))  # Join list elements with '|'

            elif isinstance(value, dict):
                if key in ctv_slots:
                    # Extract values from env_* fields
                    if "has_raw_value" in value:
                        scalar_doc[f"{key}_has_raw_value"] = value["has_raw_value"]

                    if "term" in value and isinstance(value["term"], dict):
                        if "id" in value["term"]:
                            scalar_doc[f"{key}_term_id"] = value["term"]["id"]
                        if "name" in value["term"]:
                            scalar_doc[f"{key}_term_name"] = value["term"]["name"]

                elif all(isinstance(v, (str, int, float, bool, type(None))) or
                         (isinstance(v, list) and all(
                             isinstance(item, (str, int, float, bool, type(None))) for item in v))
                         for v in value.values()):
                    # Flatten scalar-only dicts and pipe-join any scalar lists
                    for sub_key, sub_value in value.items():
                        if sub_key == "type":
                            continue  # Skip 'type' fields inside dicts
                        # Use underscores for all nested keys, replacing any periods
                        formatted_sub_key = sub_key.replace('.', '_')
                        if isinstance(sub_value, list):
                            scalar_doc[f"{key}_{formatted_sub_key}"] = "|".join(map(str, sub_value))
                        else:
                            scalar_doc[f"{key}_{formatted_sub_key}"] = sub_value

                else:
                    problem_slots.add(key)
                    stringified_singletons = stringify_singleton_dict_list(value)
                    if stringified_singletons != "":
                        scalar_doc[f"{key}"] = stringified_singletons
                    else:
                        if key not in known_skips:
                            scalar_doc[f"{key}"] = stringify(value)
            else:
                problem_slots.add(key)
                stringified_singletons = stringify_singleton_dict_list(value)
                if stringified_singletons != "":
                    scalar_doc[f"{key}"] = stringified_singletons
                else:
                    if key not in known_skips:
                        scalar_doc[f"{key}"] = stringify(value)

        scalar_docs.append(scalar_doc)

    stringifieds = sorted(problem_slots - known_skips)  # Ensure it's sorted before printing
    logger.info(f"Complex fields that were stringified: {stringifieds}")

    return scalar_docs


def extract_associated_dois(studies: List[Dict]) -> List[Dict]:
    """
    Extracts associated_dois from a list of studies, adding the study's ID to each DOI entry.

    Args:
        studies: List of study documents
    
    Returns:
        List of dictionaries, each representing a DOI with the study ID added
    """
    doi_entries = []

    for study in tqdm(studies, desc="Extracting associated DOIs"):
        study_id = study.get("id")  # Get study ID
        associated_dois = study.get("associated_dois", [])

        for doi in associated_dois:
            if isinstance(doi, dict):  # Ensure it's a dictionary
                doi_entry = doi.copy()  # Make a copy to avoid modifying original data
                doi_entry["study_id"] = study_id  # Add study ID
                doi_entry.pop("type", None)  # Remove 'type' field if it exists
                doi_entries.append(doi_entry)

    return doi_entries


def extract_credit_associations(studies: List[Dict]) -> List[Dict]:
    """
    Extracts credit associations from a list of studies, flattening PersonValue fields 
    and pipe-concatenating applied roles.

    Args:
        studies: List of study documents
    
    Returns:
        List of dictionaries, each representing a CreditAssociation with the study ID added
    """
    credit_entries = []

    for study in tqdm(studies, desc="Extracting credit associations"):
        study_id = study.get("id")  # Get study ID
        credit_associations = study.get("has_credit_associations", [])

        for credit in credit_associations:
            if isinstance(credit, dict):  # Ensure it's a dictionary
                credit_entry = {"study_id": study_id}  # Start with the study ID

                # Flatten applied_roles (if multivalued)
                applied_roles = credit.get("applied_roles", [])
                if isinstance(applied_roles, list):
                    applied_roles.sort()
                    credit_entry["applied_roles"] = "|".join(map(str, applied_roles))

                # Flatten applies_to_person (PersonValue structure)
                person = credit.get("applies_to_person", {})
                if isinstance(person, dict):
                    for key in ["name", "orcid", "profile_image_url", "has_raw_value"]:
                        if key in person:
                            credit_entry[f"person.{key}"] = person[key]

                    # Pipe-concatenate websites if it's a list
                    if isinstance(person.get("websites"), list):
                        credit_entry["person.websites"] = "|".join(person["websites"])

                credit_entries.append(credit_entry)

    return credit_entries


def extract_chem_administration(biosamples: List[Dict]) -> List[Dict]:
    """
    Extracts chem_administration field from biosample documents,
    creating a separate table with biosample ID, chemical name, chemical ID,
    raw value, and timestamp.

    Args:
        biosamples: List of biosample documents
    
    Returns:
        List of dictionaries, each representing a chemical administration entry
    """
    chem_entries = []
    pattern = re.compile(r"^(.*?) \[([^\]]+)\];([\d\-T:]+)$")  # Regex for label, CURIE, timestamp

    for sample in tqdm(biosamples, desc="Extracting chemical administration data"):
        biosample_id = sample.get("id")  # Get biosample ID
        chem_administration = sample.get("chem_administration", [])

        for chem in chem_administration:
            if isinstance(chem, dict):
                entry = {"biosample_id": biosample_id}

                # Extract has_raw_value and parse it
                raw_value = chem.get("has_raw_value", "")
                entry["has_raw_value"] = raw_value

                match = pattern.match(raw_value)
                if match:
                    entry["extracted_label"] = match.group(1)
                    entry["extracted_curie"] = match.group(2)
                    entry["extracted_timestamp"] = match.group(3)
                else:
                    entry["extracted_label"] = ""
                    entry["extracted_curie"] = ""
                    entry["extracted_timestamp"] = ""

                # Extract term details if present
                term = chem.get("term", {})
                if isinstance(term, dict):
                    entry["term_id"] = term.get("id", "")
                    entry["term_name"] = term.get("name", "")

                chem_entries.append(entry)

    return chem_entries


def calculate_field_counts(documents: List[Dict]) -> List[Dict]:
    """
    Calculates the count of each field across all documents.

    Args:
        documents: List of documents (dictionaries)

    Returns:
        List of dictionaries with field names and counts
    """
    field_counts = {}
    
    for doc in tqdm(documents, desc="Calculating field counts"):
        for field, value in doc.items():
            if value is not None:  # Only count non-null values
                field_counts[field] = field_counts.get(field, 0) + 1
    
    return [{"field": field, "count": count} for field, count in field_counts.items()]


def decorate_env_fields(documents: List[Dict], label_cache: Dict[str, str], obsolete_terms_list: List[str], 
                        to_label_check: List[str]) -> List[Dict]:
    """
    Decorates environmental fields in documents with canonical labels and obsolescence status.
    Also checks if the provided labels match the canonical labels.

    Args:
        documents: List of documents to process
        label_cache: Dictionary mapping CURIEs to labels
        obsolete_terms_list: List of obsolete term CURIEs
        to_label_check: List of field names to check for CURIEs

    Returns:
        The original documents with added decoration fields
    """
    # Map term ID field names to their corresponding label field names
    # Only using underscore format to be consistent with MongoDB field names
    term_id_to_label_map = {
        # Flattened format with underscores instead of dots
        'env_broad_scale_term_id': 'env_broad_scale_term_name',
        'env_local_scale_term_id': 'env_local_scale_term_name',
        'env_medium_term_id': 'env_medium_term_name',
        'env_broad_scale_id': 'env_broad_scale_label',
        'env_local_scale_id': 'env_local_scale_label',
        'env_medium_id': 'env_medium_label',
        'envoBroadScale_id': 'envoBroadScale_label',
        'envoLocalScale_id': 'envoLocalScale_label',
        'envoMedium_id': 'envoMedium_label',
    }
    
    for doc in tqdm(documents, desc="Decorating environmental fields"):
        for key in to_label_check:
            if key in doc and doc[key]:
                # Get CURIE and clean it up if needed
                curie = doc[key]
                
                # Normalize CURIE format (ensure it has a colon separator)
                if "_" in curie and ":" not in curie:
                    # Convert ENVO_01000253 to ENVO:01000253
                    curie_parts = curie.split("_", 1)
                    if len(curie_parts) == 2:
                        normalized_curie = f"{curie_parts[0]}:{curie_parts[1]}"
                    else:
                        normalized_curie = curie
                else:
                    normalized_curie = curie
                
                # Convert key to use underscores instead of periods for output fields
                output_key_base = key.replace('.', '_')
                
                # Store the normalized CURIE for reference
                doc[f"{output_key_base}_normalized_curie"] = normalized_curie
                
                # Step 1: Look up the canonical label
                canonical_label = label_cache.get(normalized_curie)
                if canonical_label:
                    doc[f"{output_key_base}_canonical_label"] = canonical_label
                else:
                    doc[f"{output_key_base}_canonical_label"] = None
                
                # Step 2: Check if the term is obsolete
                doc[f"{output_key_base}_obsolete"] = normalized_curie in obsolete_terms_list
                
                # Step 3: Compare the provided label with the canonical one
                label_field = term_id_to_label_map.get(key)
                if label_field and label_field in doc and doc[label_field] and canonical_label:
                    # Ensure label field also uses underscores for comparison
                    label_field_value = doc[label_field]
                    doc[f"{output_key_base}_label_match"] = (label_field_value.strip() == canonical_label.strip())
                else:
                    doc[f"{output_key_base}_label_match"] = None
    
    return documents


@click.command()
@click.option('--mongo-uri', default='mongodb://localhost:27017/nmdc', 
              help='MongoDB connection URI. Can include database name (e.g., mongodb://localhost:27017/nmdc).')
@click.option('--mongo-db', default=None, type=str,
              help='Optional: MongoDB database name. Only needed if not specified in the URI.')
@click.option('--auth', is_flag=True, 
              help='Use authenticated connection from .env file')
@click.option('--env-file', default='local/.env', 
              help='Path to .env file for authenticated connections. Used only with --auth flag.')
def main(mongo_uri: str, mongo_db: Optional[str] = None, auth: bool = False, env_file: str = 'local/.env'):
    """
    Flattens NMDC collections and creates specialized views.
    
    This script:
    1. Fetches data from local MongoDB 
    2. Processes and flattens the data
    3. Stores results in MongoDB collections
    
    Authentication:
      - Without --auth: Uses the connection string as provided
      - With --auth: Loads MongoDB credentials from the specified .env file
                    Expected variables: MONGO_USERNAME, MONGO_PASSWORD, MONGO_HOST, MONGO_PORT, MONGO_DB
    """
    # Set up MongoDB connection
    if auth:
        # Check if env file exists
        env_path = pathlib.Path(env_file)
        if not env_path.exists():
            logger.error(f"Environment file not found: {env_file}")
            sys.exit(1)
            
        # Load environment variables from .env file
        env_vars = dotenv.dotenv_values(env_file)
        
        # Check for required variables
        required_vars = ['MONGO_USERNAME', 'MONGO_PASSWORD']
        missing_vars = [var for var in required_vars if var not in env_vars or not env_vars[var]]
        if missing_vars:
            logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            sys.exit(1)
            
        # Build authenticated connection string
        mongo_host = env_vars.get('MONGO_HOST', 'localhost')
        mongo_port = env_vars.get('MONGO_PORT', '27017')
        db_from_env = env_vars.get('MONGO_DB')
        username = env_vars['MONGO_USERNAME']
        password = env_vars['MONGO_PASSWORD']
        
        # Use MONGO_DB from environment if specified
        if db_from_env:
            mongo_db = db_from_env
            
        auth_source = env_vars.get('MONGO_AUTH_SOURCE', 'admin')
        
        # Construct authenticated URI
        mongo_uri = f"mongodb://{username}:{password}@{mongo_host}:{mongo_port}/?authSource={auth_source}"
        logger.info(f"Using authenticated connection to {mongo_host}:{mongo_port}")
    else:
        logger.info(f"Using connection string: {mongo_uri}")
    
    # Connect to MongoDB
    client = MongoClient(mongo_uri)
    
    # If mongo_db parameter is provided, use it
    # Otherwise, try to extract it from the URI or default to 'nmdc'
    if mongo_db is not None:
        db_name = str(mongo_db)  # Ensure it's a string
    else:
        # Extract database name from URI if present
        from urllib.parse import urlparse
        parsed_uri = urlparse(mongo_uri)
        path = parsed_uri.path
        if path and path.startswith('/'):
            db_name = str(path[1:])  # Remove leading slash and ensure string
        else:
            db_name = 'nmdc'  # Default database name if not specified
    
    # Final safety check to ensure db_name is a string
    if not isinstance(db_name, str):
        db_name = 'nmdc'  # Fallback to default
            
    logger.info(f"Using database: {db_name}")
    db = client[db_name]
    
    # Set up ontology tools
    logger.info("Setting up ontology tools...")
    ontology_list = ["envo", "pato", "uberon"]
    ontology_adapters = build_ontology_adapters(ontology_list)
    label_cache = load_ontology_labels(ontology_adapters)
    obsolete_terms_list = find_obsolete_terms(ontology_adapters)
    
    # Load NMDC schema
    logger.info("Loading NMDC schema...")
    nmdc_schema_view = SchemaView(NMDC_SCHEMA_URL)
    nmdc_schema_usage_index = nmdc_schema_view.usage_index()
    
    # Extract usage for ControlledTermValue and ControlledIdentifiedTermValue
    ctv_usage = nmdc_schema_usage_index['ControlledTermValue']
    citv_usage = nmdc_schema_usage_index['ControlledIdentifiedTermValue']
    
    # Build a set of slots that use ControlledTermValue
    ctv_using_slots = set()
    for usage in ctv_usage:
        ctv_using_slots.add(usage.slot)
    for usage in citv_usage:
        ctv_using_slots.add(usage.slot)
    logger.info(f"Found {len(ctv_using_slots)} slots using ControlledTermValue.")
    
    # Define keys to check for labels - only using underscore format
    to_label_check = [
        # Flattened format with underscores instead of dots
        'env_broad_scale_id', 'env_local_scale_id', 'env_medium_id',
        'env_broad_scale_term_id', 'env_local_scale_term_id', 'env_medium_term_id',
        'envoBroadScale_id', 'envoLocalScale_id', 'envoMedium_id',
    ]
    
    # Get list of available collections
    collections = db.list_collection_names()
    logger.info(f"Available collections in database: {collections}")
    
    # Map of expected collection names to possible alternatives
    collection_map = {
        "study_set": ["study_set", "studies", "study"],
        "biosample_set": ["biosample_set", "biosamples", "biosample"]
    }
    
    # Find the correct collection names
    def find_collection_name(expected, alternatives):
        if expected in collections:
            return expected
        for alt in alternatives:
            if alt in collections:
                logger.info(f"Using alternative collection name: {alt} instead of {expected}")
                return alt
        logger.warning(f"Could not find collection {expected} or alternatives: {alternatives}")
        return expected  # Return the original even if not found
    
    # Find study collection
    study_collection = find_collection_name("study_set", collection_map["study_set"])
    
    # Process studies
    logger.info(f"Processing studies from collection: {study_collection}...")
    studies = fetch_all_documents_from_mongodb(client, db_name, study_collection)
    
    # Create flattened studies
    scalar_studies = flatten(
        studies,
        ctv_slots=ctv_using_slots,
        known_skips={'associated_dois', 'has_credit_associations'}
    )
    
    # Decorate environmental fields
    scalar_studies = decorate_env_fields(scalar_studies, label_cache, obsolete_terms_list, to_label_check)
    
    # Create flattened DOIs
    doi_list = extract_associated_dois(studies)
    
    # Create flattened credit associations
    credit_list = extract_credit_associations(studies)
    
    # Find biosample collection
    biosample_collection = find_collection_name("biosample_set", collection_map["biosample_set"])
    
    # Process biosamples
    logger.info(f"Processing biosamples from collection: {biosample_collection}...")
    biosamples = fetch_all_documents_from_mongodb(client, db_name, biosample_collection)
    
    # Create flattened biosamples
    scalar_biosamples = flatten(biosamples, ctv_slots=ctv_using_slots, known_skips={"chem_administration"})
    
    # Decorate environmental fields
    scalar_biosamples = decorate_env_fields(scalar_biosamples, label_cache, obsolete_terms_list, to_label_check)
    
    # Create flattened chemical administration
    chem_admin_data = extract_chem_administration(biosamples)
    
    # Calculate field counts for biosamples
    biosample_field_counts = calculate_field_counts(scalar_biosamples)
    
    # Insert into MongoDB
    logger.info("Inserting data into MongoDB...")
    
    # Clear existing collections
    db.flattened_biosample.drop()
    db.flattened_biosample_chem_administration.drop()
    db.flattened_biosample_field_counts.drop()
    db.flattened_study.drop()
    db.flattened_study_associated_dois.drop()
    db.flattened_study_has_credit_associations.drop()
    
    # Insert new data
    if scalar_studies:
        db.flattened_study.insert_many(scalar_studies)
        logger.info(f"Inserted {len(scalar_studies)} documents into flattened_study")
    
    if doi_list:
        db.flattened_study_associated_dois.insert_many(doi_list)
        logger.info(f"Inserted {len(doi_list)} documents into flattened_study_associated_dois")
    
    if credit_list:
        db.flattened_study_has_credit_associations.insert_many(credit_list)
        logger.info(f"Inserted {len(credit_list)} documents into flattened_study_has_credit_associations")
    
    if scalar_biosamples:
        db.flattened_biosample.insert_many(scalar_biosamples)
        logger.info(f"Inserted {len(scalar_biosamples)} documents into flattened_biosample")
    
    if chem_admin_data:
        db.flattened_biosample_chem_administration.insert_many(chem_admin_data)
        logger.info(f"Inserted {len(chem_admin_data)} documents into flattened_biosample_chem_administration")
    
    if biosample_field_counts:
        db.flattened_biosample_field_counts.insert_many(biosample_field_counts)
        logger.info(f"Inserted {len(biosample_field_counts)} documents into flattened_biosample_field_counts")
    
    logger.info("Done! Successfully created all flattened NMDC collections.")


if __name__ == "__main__":
    main()
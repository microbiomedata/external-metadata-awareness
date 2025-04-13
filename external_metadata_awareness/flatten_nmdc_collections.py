"""
Script to flatten NMDC collections into more easily queryable MongoDB collections.

This script creates the following collections from NMDC data:
  - flattened_biosample: Flattened biosample records with environmental terms enhanced with ontology information
  - flattened_biosample_chem_administration: Extracted chemical administration records
  - flattened_biosample_field_counts: Field usage statistics across all biosamples
  - flattened_study: Flattened study records with environmental terms enhanced with ontology information
  - flattened_study_associated_dois: Extracted DOI information from studies
  - flattened_study_has_credit_associations: Extracted credit association information from studies

The flattening process:
1. Fetches data from local MongoDB
2. Flattens nested structures with all field names using underscores
3. Converts arrays to pipe-separated strings
4. Enhances environmental context fields (env_broad_scale, env_local_scale, env_medium) with:
   - Normalized CURIEs
   - Canonical labels from ontologies
   - Obsolescence status
   - Label verification

Usage:
  poetry run python flatten_nmdc_collections.py 
    [--mongo-uri MONGO_URI] [--mongo-db MONGO_DB] [--auth] [--env-file ENV_FILE]
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
NMDC_SCHEMA_URL = "https://raw.githubusercontent.com/microbiomedata/nmdc-schema/refs/heads/main/nmdc_schema/nmdc_materialized_patterns.yaml"


def fetch_documents_from_mongodb(client: MongoClient, db_name: str, collection_name: str) -> List[Dict]:
    """
    Fetch all documents from a specified MongoDB collection.

    Args:
        client: MongoDB client
        db_name: MongoDB database name
        collection_name: MongoDB collection name

    Returns:
        List of documents from the collection with MongoDB _id field removed
    """
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


def build_ontology_tools(ontology_names: List[str]) -> tuple:
    """
    Creates ontology tools for the given ontology names:
    1. Builds adapters for each ontology
    2. Loads labels from all ontologies
    3. Identifies obsolete terms

    Args:
        ontology_names: List of ontology names (e.g., ["envo", "pato", "uberon"])

    Returns:
        Tuple containing (label_cache, obsolete_terms)
    """
    # Build ontology adapters
    adapters = {}
    for ontology in tqdm(ontology_names, desc="Building ontology adapters"):
        adapters[ontology] = get_adapter(f"sqlite:obo:{ontology}")

    # Load labels from all ontologies
    label_cache = {}
    for ontology, adapter in tqdm(adapters.items(), desc="Loading ontology labels"):
        entities = sorted(list(adapter.entities()))
        for curie in tqdm(entities, desc=f"Caching {ontology} labels", leave=False):
            label = adapter.label(curie)
            if label:
                label_cache[curie] = label

    # Identify obsolete terms
    obsolete_terms = []
    for _, adapter in tqdm(adapters.items(), desc="Finding obsolete terms"):
        obsolete_terms.extend(adapter.obsoletes())

    return label_cache, obsolete_terms


def normalize_curie(curie: str) -> str:
    """
    Normalizes a CURIE by ensuring it uses a colon separator.
    Example: ENVO_01000253 -> ENVO:01000253

    Args:
        curie: The CURIE to normalize

    Returns:
        Normalized CURIE with colon separator
    """
    if not curie or not isinstance(curie, str):
        return curie

    if "_" in curie and ":" not in curie:
        parts = curie.split("_", 1)
        if len(parts) == 2:
            return f"{parts[0]}:{parts[1]}"
    return curie


def stringify_value(value: Any) -> str:
    """
    Converts any value to a string representation.
    For lists and dictionaries, uses JSON format.

    Args:
        value: Any Python object

    Returns:
        String representation
    """
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True, ensure_ascii=False)
    return str(value)


def stringify_singleton_dict_list(dict_list: List[Dict]) -> str:
    """
    Converts a list of dictionaries to a pipe-separated string of values
    if each dictionary contains only a single field (excluding 'type').

    Args:
        dict_list: List of dictionaries to process

    Returns:
        Pipe-separated string of values or empty string
    """
    if not isinstance(dict_list, list) or not all(isinstance(d, dict) for d in dict_list):
        return ""

    max_keys = 0
    values = []

    for d in dict_list:
        # Remove 'type' field
        filtered_dict = {k: v for k, v in d.items() if k != "type"}
        max_keys = max(max_keys, len(filtered_dict))

        # Extract value if only one key exists
        if len(filtered_dict) == 1:
            values.append(next(iter(filtered_dict.values())))

    # Return pipe-separated string if all dictionaries had only one key
    if max_keys == 1:
        return "|".join(map(str, sorted(values)))
    return ""


def flatten_documents(documents: List[Dict], controlled_term_slots: Optional[Set[str]] = None,
                      skip_fields: Optional[Set[str]] = None) -> List[Dict]:
    """
    Flattens nested document structures for easier querying:
    1. Converts nested dictionaries to fields with underscore notation
    2. Joins arrays with pipe separators
    3. Special handling for controlled term fields (env_broad_scale, etc.)
    4. Orders fields alphabetically in the resulting documents

    Args:
        documents: List of documents to flatten
        controlled_term_slots: Fields with ControlledTermValue range
        skip_fields: Fields to skip during flattening

    Returns:
        List of flattened documents with fields in alphabetical order
    """
    if controlled_term_slots is None:
        controlled_term_slots = set()

    if skip_fields is None:
        skip_fields = set()

    flattened_docs = []
    complex_fields = set()

    for doc in tqdm(documents, desc="Flattening documents"):
        temp_doc = {}  # Use a temporary dictionary to collect fields

        for key, value in doc.items():
            # Skip type fields and specified skip fields
            if key == "type" or key in skip_fields:
                continue

            # Handle simple scalar values directly
            if isinstance(value, (str, int, float, bool, type(None))):
                temp_doc[key] = value

            # Handle lists of scalars - join with pipe separator
            elif isinstance(value, list) and all(
                    isinstance(item, (str, int, float, bool, type(None))) for item in value):
                temp_doc[key] = "|".join(map(str, value))

            # Handle controlled term fields
            elif isinstance(value, dict) and key in controlled_term_slots:
                # Extract raw value
                if "has_raw_value" in value:
                    temp_doc[f"{key}_has_raw_value"] = value["has_raw_value"]

                # Extract term ID and name
                if "term" in value and isinstance(value["term"], dict):
                    term = value["term"]
                    if "id" in term:
                        temp_doc[f"{key}_term_id"] = term["id"]
                    if "name" in term:
                        temp_doc[f"{key}_term_name"] = term["name"]

            # Handle other dictionary types (QuantityValue, TextValue, etc.)
            elif isinstance(value, dict):
                # First extract all scalar fields from the dictionary
                for sub_key, sub_value in value.items():
                    if sub_key == "type":
                        continue  # Skip type fields

                    # Handle scalar sub-values
                    if isinstance(sub_value, (str, int, float, bool, type(None))):
                        temp_doc[f"{key}_{sub_key}"] = sub_value

                    # Handle lists of scalars in sub-values
                    elif isinstance(sub_value, list) and all(
                            isinstance(item, (str, int, float, bool, type(None))) for item in sub_value):
                        temp_doc[f"{key}_{sub_key}"] = "|".join(map(str, sub_value))

                    # Handle nested term dictionary (important for environmental fields)
                    elif isinstance(sub_value, dict) and sub_key == "term":
                        for term_key, term_value in sub_value.items():
                            if term_key != "type" and isinstance(term_value, (str, int, float, bool, type(None))):
                                temp_doc[f"{key}_term_{term_key}"] = term_value

            # Try to handle lists of dictionaries
            elif isinstance(value, list):
                if all(isinstance(item, (str, int, float, bool, type(None))) for item in value):
                    # Simple list of scalars
                    temp_doc[key] = "|".join(map(str, value))
                elif all(isinstance(d, dict) for d in value):
                    # List of dictionaries - try single values
                    single_values = stringify_singleton_dict_list(value)
                    if single_values:
                        temp_doc[key] = single_values
                    else:
                        complex_fields.add(key)
                        temp_doc[key] = stringify_value(value)
                else:
                    complex_fields.add(key)
                    temp_doc[key] = stringify_value(value)
            else:
                complex_fields.add(key)
                if key not in skip_fields:
                    temp_doc[key] = stringify_value(value)

        # Create a new alphabetically ordered document
        ordered_doc = {}
        for key in sorted(temp_doc.keys()):
            ordered_doc[key] = temp_doc[key]

        flattened_docs.append(ordered_doc)

    # Log fields that were stringified
    if complex_fields - skip_fields:
        logger.info(f"Complex fields that were stringified: {sorted(complex_fields - skip_fields)}")

    return flattened_docs


def enhance_env_fields(documents: List[Dict], label_cache: Dict[str, str],
                       obsolete_terms: List[str], env_id_fields: List[str]) -> List[Dict]:
    """
    Enhances environmental fields with ontology information:
    1. Normalizes CURIEs to standard format
    2. Adds canonical labels from ontology
    3. Marks obsolete terms
    4. Verifies if provided labels match canonical labels
    5. Creates new documents with fields in strict alphabetical order

    Args:
        documents: List of documents to enhance
        label_cache: Dictionary mapping CURIEs to canonical labels
        obsolete_terms: List of obsolete term CURIEs
        env_id_fields: Environmental field ID names to process

    Returns:
        Documents enhanced with ontology information, with fields in strict alphabetical order
    """
    enhanced_documents = []

    for doc in tqdm(documents, desc="Enhancing environmental terms"):
        # First collect all the original fields plus the new fields
        all_fields = {}

        # Copy all existing fields
        for key, value in doc.items():
            all_fields[key] = value

        # Add new environmental fields
        for id_field in env_id_fields:
            if id_field not in doc or not doc[id_field]:
                continue

            # Extract CURIE and normalize it
            curie = doc[id_field]
            normalized_curie = normalize_curie(curie)

            # Extract the base field name without the id suffix
            if "term_id" in id_field:
                base_field = id_field.replace("_term_id", "")
            elif "_id" in id_field:
                base_field = id_field.replace("_id", "")
            else:
                base_field = id_field

            # Derive corresponding label field name
            if "term_id" in id_field:
                label_field = id_field.replace("term_id", "term_name")
            else:
                label_field = id_field.replace("_id", "_label")

            # Add new fields
            all_fields[f"{base_field}_normalized_curie"] = normalized_curie

            canonical_label = label_cache.get(normalized_curie)
            all_fields[f"{base_field}_canonical_label"] = canonical_label

            all_fields[f"{base_field}_is_obsolete"] = normalized_curie in obsolete_terms

            # Add label match field
            if canonical_label and label_field in doc and doc[label_field]:
                all_fields[f"{base_field}_label_match"] = (doc[label_field].strip() == canonical_label.strip())
            else:
                all_fields[f"{base_field}_label_match"] = None

        # Create a new document with fields in alphabetical order
        ordered_doc = {}
        for key in sorted(all_fields.keys()):
            ordered_doc[key] = all_fields[key]

        enhanced_documents.append(ordered_doc)

    return enhanced_documents


def extract_associated_dois(studies: List[Dict]) -> List[Dict]:
    """
    Extracts DOI information from studies into a separate collection.
    Creates documents with fields in alphabetical order.

    Args:
        studies: List of study documents

    Returns:
        List of DOI entries with study ID added, fields in alphabetical order
    """
    doi_entries = []

    for study in tqdm(studies, desc="Extracting DOIs"):
        study_id = study.get("id")
        associated_dois = study.get("associated_dois", [])

        for doi in associated_dois:
            if isinstance(doi, dict):
                # Create a temporary dictionary with all fields
                temp_entry = {"study_id": study_id}
                for k, v in doi.items():
                    if k != "type":  # Skip type field
                        temp_entry[k] = v

                # Create a new document with alphabetically ordered fields
                ordered_entry = {}
                for key in sorted(temp_entry.keys()):
                    ordered_entry[key] = temp_entry[key]

                doi_entries.append(ordered_entry)

    return doi_entries


def extract_credit_associations(studies: List[Dict]) -> List[Dict]:
    """
    Extracts credit association information from studies:
    - Flattens person fields
    - Concatenates multiple roles with pipe separator
    - Creates documents with fields in alphabetical order

    Args:
        studies: List of study documents

    Returns:
        List of credit association entries with fields in alphabetical order
    """
    credit_entries = []

    for study in tqdm(studies, desc="Extracting credit associations"):
        study_id = study.get("id")
        credit_associations = study.get("has_credit_associations", [])

        for credit in credit_associations:
            if isinstance(credit, dict):
                # Collect all fields in a temporary dictionary
                temp_entry = {"study_id": study_id}

                # Join multiple roles with pipe separator
                applied_roles = credit.get("applied_roles", [])
                if isinstance(applied_roles, list):
                    applied_roles.sort()
                    temp_entry["applied_roles"] = "|".join(map(str, applied_roles))

                # Extract person fields
                person = credit.get("applies_to_person", {})
                if isinstance(person, dict):
                    # Extract basic person fields
                    for key in ["name", "orcid", "profile_image_url", "has_raw_value"]:
                        if key in person:
                            # Use underscores instead of periods
                            temp_entry[f"person_{key}"] = person[key]

                    # Join multiple websites with pipe separator
                    if isinstance(person.get("websites"), list):
                        temp_entry["person_websites"] = "|".join(person["websites"])

                # Create a new document with alphabetically ordered fields
                ordered_entry = {}
                for key in sorted(temp_entry.keys()):
                    ordered_entry[key] = temp_entry[key]

                credit_entries.append(ordered_entry)

    return credit_entries


def extract_chem_administration(biosamples: List[Dict]) -> List[Dict]:
    """
    Extracts chemical administration information from biosamples:
    - Parses raw values to extract chemical name, ID, and timestamp
    - Links to biosample ID
    - Creates documents with fields in alphabetical order

    Args:
        biosamples: List of biosample documents

    Returns:
        List of chemical administration entries with fields in alphabetical order
    """
    chem_entries = []
    # Pattern for "label [CURIE];timestamp"
    pattern = re.compile(r"^(.*?) \[([^\]]+)\];([\d\-T:]+)$")

    for sample in tqdm(biosamples, desc="Extracting chemical administration data"):
        biosample_id = sample.get("id")
        chem_administration = sample.get("chem_administration", [])

        for chem in chem_administration:
            if isinstance(chem, dict):
                # Collect all fields in a temporary dictionary
                temp_entry = {"biosample_id": biosample_id}

                # Extract raw value
                raw_value = chem.get("has_raw_value", "")
                temp_entry["has_raw_value"] = raw_value

                # Parse raw value to extract components
                match = pattern.match(raw_value)
                if match:
                    temp_entry["chemical_label"] = match.group(1)
                    temp_entry["chemical_id"] = match.group(2)
                    temp_entry["timestamp"] = match.group(3)
                else:
                    temp_entry["chemical_label"] = ""
                    temp_entry["chemical_id"] = ""
                    temp_entry["timestamp"] = ""

                # Extract term details
                term = chem.get("term", {})
                if isinstance(term, dict):
                    temp_entry["term_id"] = term.get("id", "")
                    temp_entry["term_name"] = term.get("name", "")

                # Create a new document with alphabetically ordered fields
                ordered_entry = {}
                for key in sorted(temp_entry.keys()):
                    ordered_entry[key] = temp_entry[key]

                chem_entries.append(ordered_entry)

    return chem_entries


def calculate_field_counts(documents: List[Dict]) -> List[Dict]:
    """
    Calculates the frequency of each field across all documents.
    Creates count documents with fields in alphabetical order.

    Args:
        documents: List of documents

    Returns:
        List of field count entries with fields in alphabetical order
    """
    field_counts = {}

    for doc in tqdm(documents, desc="Calculating field counts"):
        for field, value in doc.items():
            if value is not None:  # Count non-null values
                field_counts[field] = field_counts.get(field, 0) + 1

    # Convert to list of dictionaries with alphabetically ordered fields
    count_entries = []
    for field, count in field_counts.items():
        count_entries.append({"field": field, "count": count})

    return count_entries


@click.command()
@click.option('--mongo-uri', default='mongodb://localhost:27017/nmdc',
              help='MongoDB connection URI. Can include database name.')
@click.option('--mongo-db', default=None, type=str,
              help='Optional: MongoDB database name. Only needed if not in URI.')
@click.option('--auth', is_flag=True,
              help='Use authenticated connection from .env file')
@click.option('--env-file', default='local/.env',
              help='Path to .env file for authenticated connections.')
def main(mongo_uri: str, mongo_db: Optional[str] = None, auth: bool = False, env_file: str = 'local/.env'):
    """
    Flattens NMDC collections and creates enhanced views for easier querying.

    Connects to MongoDB, processes biosample and study data, and creates flattened collections
    with special focus on environmental context fields (env_broad_scale, env_local_scale, env_medium).

    Authentication options:
      - Without --auth: Uses connection string as provided
      - With --auth: Loads credentials from .env file (MONGO_USERNAME, MONGO_PASSWORD, etc.)
    """
    # Set up MongoDB connection
    if auth:
        # Check if env file exists
        env_path = pathlib.Path(env_file)
        if not env_path.exists():
            logger.error(f"Environment file not found: {env_file}")
            sys.exit(1)

        # Load environment variables
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

    # Determine database name
    if mongo_db is not None:
        db_name = str(mongo_db)
    else:
        # Extract database name from URI if present
        from urllib.parse import urlparse
        parsed_uri = urlparse(mongo_uri)
        path = parsed_uri.path
        if path and path.startswith('/'):
            db_name = str(path[1:])
        else:
            db_name = 'nmdc'  # Default database name

    logger.info(f"Using database: {db_name}")
    db = client[db_name]

    # Set up ontology tools
    logger.info("Setting up ontology tools...")
    ontology_list = ["envo", "pato", "uberon"]
    label_cache, obsolete_terms = build_ontology_tools(ontology_list)
    logger.info(f"Loaded {len(label_cache)} ontology labels and {len(obsolete_terms)} obsolete terms")

    # Load NMDC schema
    logger.info("Loading NMDC schema...")
    schema_view = SchemaView(NMDC_SCHEMA_URL)
    schema_usage_index = schema_view.usage_index()

    # Identify slots using ControlledTermValue
    controlled_term_slots = set()
    for usage_type in ['ControlledTermValue', 'ControlledIdentifiedTermValue']:
        if usage_type in schema_usage_index:
            for usage in schema_usage_index[usage_type]:
                controlled_term_slots.add(usage.slot)

    logger.info(f"Found {len(controlled_term_slots)} slots using ControlledTermValue")

    # Define environmental ID fields to enhance
    env_id_fields = [
        'env_broad_scale_term_id', 'env_local_scale_term_id', 'env_medium_term_id',
        'env_broad_scale_id', 'env_local_scale_id', 'env_medium_id',
        'envoBroadScale_id', 'envoLocalScale_id', 'envoMedium_id',
    ]

    # Find collection names
    collections = db.list_collection_names()
    logger.info(f"Available collections: {collections}")

    collection_alternatives = {
        "study_set": ["study_set", "studies", "study"],
        "biosample_set": ["biosample_set", "biosamples", "biosample"]
    }

    def find_collection(preferred, alternatives):
        """Find the best matching collection name"""
        if preferred in collections:
            return preferred
        for alt in alternatives:
            if alt in collections:
                logger.info(f"Using alternative collection: {alt} instead of {preferred}")
                return alt
        logger.warning(f"Could not find collection {preferred} or alternatives")
        return preferred

    # Process studies
    study_collection = find_collection("study_set", collection_alternatives["study_set"])
    logger.info(f"Processing studies from {study_collection}...")
    studies = fetch_documents_from_mongodb(client, db_name, study_collection)

    # Create flattened studies
    flattened_studies = flatten_documents(
        studies,
        controlled_term_slots=controlled_term_slots,
        skip_fields={'associated_dois', 'has_credit_associations'}
    )

    # Enhance environmental fields in studies
    flattened_studies = enhance_env_fields(
        flattened_studies,
        label_cache,
        obsolete_terms,
        env_id_fields
    )

    # Extract specialized collections from studies
    doi_entries = extract_associated_dois(studies)
    credit_entries = extract_credit_associations(studies)

    # Process biosamples
    biosample_collection = find_collection("biosample_set", collection_alternatives["biosample_set"])
    logger.info(f"Processing biosamples from {biosample_collection}...")
    biosamples = fetch_documents_from_mongodb(client, db_name, biosample_collection)

    # Create flattened biosamples
    flattened_biosamples = flatten_documents(
        biosamples,
        controlled_term_slots=controlled_term_slots,
        skip_fields={"chem_administration"}
    )

    # Enhance environmental fields in biosamples
    flattened_biosamples = enhance_env_fields(
        flattened_biosamples,
        label_cache,
        obsolete_terms,
        env_id_fields
    )

    # Extract chemical administration data
    chem_admin_entries = extract_chem_administration(biosamples)

    # Calculate field frequency statistics
    biosample_field_counts = calculate_field_counts(flattened_biosamples)

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
    if flattened_studies:
        db.flattened_study.insert_many(flattened_studies)
        logger.info(f"Inserted {len(flattened_studies)} documents into flattened_study")

    if doi_entries:
        db.flattened_study_associated_dois.insert_many(doi_entries)
        logger.info(f"Inserted {len(doi_entries)} documents into flattened_study_associated_dois")

    if credit_entries:
        db.flattened_study_has_credit_associations.insert_many(credit_entries)
        logger.info(f"Inserted {len(credit_entries)} documents into flattened_study_has_credit_associations")

    if flattened_biosamples:
        db.flattened_biosample.insert_many(flattened_biosamples)
        logger.info(f"Inserted {len(flattened_biosamples)} documents into flattened_biosample")

    if chem_admin_entries:
        db.flattened_biosample_chem_administration.insert_many(chem_admin_entries)
        logger.info(f"Inserted {len(chem_admin_entries)} documents into flattened_biosample_chem_administration")

    if biosample_field_counts:
        db.flattened_biosample_field_counts.insert_many(biosample_field_counts)
        logger.info(f"Inserted {len(biosample_field_counts)} documents into flattened_biosample_field_counts")

    logger.info("Done! Successfully created all flattened NMDC collections.")


if __name__ == "__main__":
    main()

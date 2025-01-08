import json
import pprint
from collections import defaultdict

import duckdb
import requests
import yaml
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

import pandas as pd
from typing import List, Dict, Any

from oaklib import get_adapter
from oaklib.implementations import AggregatorImplementation

import click

import re

# this does not define prefixes
# ie the id ncbitaxon is present but NCBITaxon in that casing is not present
obo_ontologies_yaml_url = "https://raw.githubusercontent.com/OBOFoundry/OBOFoundry.github.io/refs/heads/master/registry/ontologies.yml"

obo_ontologies_json_url = "https://raw.githubusercontent.com/OBOFoundry/OBOFoundry.github.io/master/registry/ontologies.jsonld"

# ner_ontologies = [
#     'bto',
#     'envo',
#     'ncbitaxon',
#     'po',
#     'uberon',
# ]

ner_ontologies = [
    'envo',
    'po',
]


def get_obo_preferred_prefixes(url: str) -> Dict[str, Dict[str, str]]:
    """Retrieves ontology data from a JSON-LD file and extracts specific keys.

    Returns:
      A dictionary where keys are ontology IDs and values are dictionaries
      containing the preferredPrefix and title for each ontology.
    """

    response = requests.get(url)
    data = json.loads(response.text)

    ontologies = {}
    for ontology in data['ontologies']:
        ontology_id = ontology['id']
        preferred_prefix = ontology.get('preferredPrefix')
        title = ontology.get('title')

        if not preferred_prefix:
            print(f"Warning: Ontology {ontology_id} is missing preferredPrefix.")

        if not title:
            print(f"Warning: Ontology {ontology_id} is missing title.")

        ontologies[ontology_id] = {
            'preferredPrefix': preferred_prefix,
            'title': title
        }

    return ontologies


def get_preferred_prefix(prefix_lc: str, lookup_dict: dict) -> str:
    """
    This function retrieves the preferred prefix from the provided lookup_dict.
    If not found, it defaults to the uppercase version of the input prefix.
    """
    preferred_prefix = lookup_dict.get(prefix_lc.lower(), {}).get('preferredPrefix')
    return preferred_prefix if preferred_prefix else prefix_lc.upper()


def get_obo_ids(url: str) -> Dict[str, List[str]]:
    prefixes = defaultdict(list)
    response = requests.get(url)
    data = yaml.safe_load(response.text)
    data = data["ontologies"]
    for ontology in data:
        prefixes[ontology["id"]].append(ontology["title"])
    return prefixes


def get_duckdb_engine(db_path: str) -> Engine:
    """
    Creates and returns an SQLAlchemy Engine for the DuckDB database.

    Args:
        db_path (str): Path to the DuckDB file.

    Returns:
        sqlalchemy.engine.Engine: A connection engine for the DuckDB database.
    """
    try:
        engine = create_engine(f"duckdb:///{db_path}")
        return engine
    except Exception as e:
        raise RuntimeError(f"Failed to create SQLAlchemy engine: {e}")


def list_tables(engine: Engine, message: str = "Tables in the current schema:") -> None:
    """
    Prints a list of all tables in the current schema.

    Args:
        engine (sqlalchemy.engine.Engine): SQLAlchemy engine for the database.
        message (str): Optional message to print before listing the tables. Defaults to "Tables in the current schema:".
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SHOW TABLES"))
            print(message)  # Print the provided message
            for row in result:
                print(f" - {row[0]}")
    except Exception as e:
        raise RuntimeError(f"Error listing tables: {e}")


def extract_curies_from_text(
        text: str,
        row_id: int = None,  # Generic parameter for row context
        prefix_min_len: int = 2,
        prefix_max_len: int = 10,
        local_id_min_len: int = 2,
        local_id_max_len: int = 10,
        prefix_chars_allowed: str = r"[a-zA-Z]",
        local_id_chars_allowed: str = r"[0-9]",
        delimiter_chars_allowed: str = r"[_:]",
) -> List[dict]:
    """
    Extract ontology class CURIEs from text and return them as dictionaries.

    Args:
        text (str): The input text.
        row_id (int, optional): A generic ID or reference for the row context.
        prefix_min_len (int): Minimum length of the prefix part of the CURIE.
        prefix_max_len (int): Maximum length of the prefix part of the CURIE.
        local_id_min_len (int): Minimum length of the local ID part of the CURIE.
        local_id_max_len (int): Maximum length of the local ID part of the CURIE.
        prefix_chars_allowed (str): Allowed characters for the prefix.
        local_id_chars_allowed (str): Allowed characters for the local ID.
        delimiter_chars_allowed (str): Allowed delimiters between prefix and local ID.

    Returns:
        List[dict]: A list of dictionaries containing CURIE parts and row context.
    """

    pattern = rf"""
        \b                                      # Word boundary
        (?P<prefix>{prefix_chars_allowed}{{{prefix_min_len},{prefix_max_len}}})  # Prefix
        (?P<delimiter>{delimiter_chars_allowed})                               # Delimiter
        (?P<local_id>{local_id_chars_allowed}{{{local_id_min_len},{local_id_max_len}}})  # Local ID
        \b                                      # Word boundary
    """
    matches = re.finditer(pattern, text, re.VERBOSE)
    return [
        {
            "row_id": row_id,  # General ID reference
            "curie_prefix": match.group("prefix"),
            "curie_delimiter": match.group("delimiter"),
            "curie_local_id": match.group("local_id"),
        }
        for match in matches
    ]


def class_detection_by_label(
        text: str,
        ontology_adapters: Dict[str, Any],
        row_id: int = None,
        min_annotated_length: int = 3
) -> List[Dict[str, Any]]:
    """
    Detect ontology class labels in a string using multiple ontology adapters and collect the annotations.
    Only annotations with a match string length >= min_annotated_length are included.
    Additionally, a flag 'is_longest_match' is added to indicate the longest match for the string.

    Args:
        text (str): The input string to be analyzed.
        ontology_adapters (dict): Dictionary of ontology adapters.
        row_id (int, optional): A generic ID or reference for the row context.
        min_annotated_length (int): Minimum length for the annotated match string to be included.

    Returns:
        List[dict]: A list of dictionaries with the annotations, each representing a new row.
    """
    annotations_for_this_string = []

    # Annotate the string using each ontology adapter
    for _, adapter in ontology_adapters.items():
        annotations = adapter.annotate_text(text)

        if annotations:  # If there are annotations
            for annotation in annotations:
                subject_string = annotation.match_string

                # Only include annotations where subject_string length is >= min_annotated_length
                if len(subject_string) >= min_annotated_length:
                    # Build the annotation dictionary
                    annotations_dict = {
                        "id": row_id,
                        "subject_string": subject_string,
                        "subject_start": annotation.subject_start,
                        "subject_end": annotation.subject_end,
                        "predicate_id": annotation.predicate_id,
                        "curie": annotation.object_id,
                        "object_string": annotation.object_label,
                    }
                    annotations_for_this_string.append(annotations_dict)

    # Determine the longest match and subsumed annotations for this string
    if annotations_for_this_string:
        longest_annotation = max(annotations_for_this_string, key=lambda x: len(x['subject_string']))

        # Mark each annotation as the longest or not, and if it's subsumed
        for annotation in annotations_for_this_string:
            annotation['is_longest_match'] = annotation['subject_string'] == longest_annotation['subject_string']
            annotation['subsumed'] = False  # Initialize subsumed flag

            for other_annotation in annotations_for_this_string:
                if annotation != other_annotation and \
                        annotation['subject_start'] >= other_annotation['subject_start'] and \
                        annotation['subject_end'] <= other_annotation['subject_end']:
                    annotation['subsumed'] = True
                    break

        covered_chars = set()
        for annotation in annotations_for_this_string:
            for i in range(annotation['subject_start'], annotation['subject_end']):
                covered_chars.add(i)
        coverage_sum = len(covered_chars) / len(text) if text else 0  # Avoid division by zero

        # Add coverage to each annotation
        for annotation in annotations_for_this_string:
            annotation['coverage_sum'] = coverage_sum

    return annotations_for_this_string


def create_ontology_adapters(ontology_short_names: list) -> dict:
    """
    Create a dictionary of OAK adapters for each ontology short name.

    Args:
        ontology_short_names (list): A list of ontology short names (e.g., ['envo', 'po']).

    Returns:
        dict: A dictionary where keys are ontology short names and values are the OAK adapters.
    """
    adapters = {}
    for short_name in ontology_short_names:
        adapter_string = f"sqlite:obo:{short_name}"  # Create the adapter string
        try:
            adapters[short_name] = get_adapter(adapter_string)  # Get the adapter and add to dictionary
        except Exception as e:
            print(f"Warning: Failed to create adapter for {short_name}. Error: {e}")
    return adapters


@click.command()
@click.option('--biosamples-duckdb-file', type=click.Path(exists=True), required=True,
              help="Path Biosamples DUckDB file.")
def main(biosamples_duckdb_file: str):
    """
    """

    obo_ids_to_preferred_prefixes = get_obo_preferred_prefixes(obo_ontologies_json_url)

    biosamples_duckdb_engine = get_duckdb_engine(biosamples_duckdb_file)
    list_tables(biosamples_duckdb_engine)

    with biosamples_duckdb_engine.connect() as connection:
        transaction = connection.begin()
        connection.execute(text("DROP TABLE IF EXISTS main.normalized_contexts;"))
        connection.execute(text("drop table if exists main.normalized_context_strings;"))
        connection.execute(text("DROP TABLE IF EXISTS normalized_contexts;"))
        connection.execute(text("drop table if exists normalized_context_strings;"))
        connection.execute(text("""
        drop table if exists main.contexts_to_normalized_strings;
        """))
        connection.execute(text("""
        drop table if exists contexts_to_normalized_strings;
        """))
        transaction.commit()

    list_tables(biosamples_duckdb_engine)

    with biosamples_duckdb_engine.connect() as connection:
        transaction = connection.begin()

        connection.execute(text("""
        CREATE TEMPORARY TABLE normalized_contexts AS
        SELECT
            id,
            harmonized_name,
            content,
            regexp_replace(trim(lower(content)), '\\s+', ' ', 'g') AS normalized
        FROM
            main.attribute
        WHERE
            harmonized_name IN ('env_broad_scale', 'env_local_scale', 'env_medium');
        """))

        connection.execute(text("""
        CREATE TABLE main.normalized_context_strings (
        normalized_context_string_id INTEGER PRIMARY KEY,
        normalized_context_string TEXT UNIQUE
        );
        """))

        connection.execute(text("""
        INSERT INTO main.normalized_context_strings (normalized_context_string_id, normalized_context_string)
        SELECT
            ROW_NUMBER() OVER () AS string_id,
            normalized
        FROM (
            SELECT DISTINCT normalized
            FROM main.normalized_contexts
        ) sub;
        """))

        connection.execute(text("""
        CREATE TABLE main.contexts_to_normalized_strings (
        id INTEGER ,
        harmonized_name TEXT ,
        normalized_context_string_id INTEGER
        );
        """))

        connection.execute(text("""
        INSERT INTO main.contexts_to_normalized_strings (id, harmonized_name, normalized_context_string_id)
        SELECT
            nc.id,
            nc.harmonized_name,
            ncs.normalized_context_string_id
        FROM
            main.normalized_contexts nc
        JOIN main.normalized_context_strings ncs
        ON
            nc.normalized = ncs.normalized_context_string;
        """))

        connection.execute(text("""
        drop table if exists main.normalized_contexts;
        """))
        connection.execute(text("""
        drop table if exists normalized_contexts;
        """))

        transaction.commit()

    list_tables(biosamples_duckdb_engine)

    normalized_context_strings = pd.read_sql("select * from main.normalized_context_strings", biosamples_duckdb_engine)

    # Ensure the column has string values and handle non-string entries
    normalized_context_strings['normalized_context_string'] = normalized_context_strings[
        'normalized_context_string'].fillna("").astype(str)

    # Apply the CURIE extraction function to each row
    curies_list = normalized_context_strings.apply(
        lambda row: extract_curies_from_text(
            row["normalized_context_string"],
            row.get("normalized_context_string_id", None)  # Pass row ID if available
        ), axis=1
    ).explode().dropna()

    # Convert the list of dictionaries into a DataFrame
    curies_asserted = pd.DataFrame(curies_list.tolist())

    # Use the obo_ids_to_preferred_prefixes to get the correct casing for the prefix
    curies_asserted['reassembled_curie'] = curies_asserted['curie_prefix'].apply(
        lambda prefix: get_preferred_prefix(prefix, obo_ids_to_preferred_prefixes)
    ) + ":" + curies_asserted['curie_local_id'].fillna('')

    curies_asserted = curies_asserted.drop(columns=['curie_delimiter', 'curie_local_id'])

    curies_asserted = curies_asserted.rename(columns={
        'row_id': 'id',
        'curie_prefix': 'prefix_lc',
        'reassembled_curie': 'curie'
    })

    with biosamples_duckdb_engine.connect() as connection:
        curies_asserted.to_sql('curies_asserted', connection, if_exists='replace', index=False)

    asserted_curies_prefixes_counts = curies_asserted['prefix_lc'].value_counts()

    obo_id_to_titles = get_obo_ids(obo_ontologies_yaml_url)
    obo_ids = list(obo_id_to_titles.keys())

    # Add a new column 'in_obo' to asserted_curies_prefixes_counts
    asserted_curies_prefixes_counts = asserted_curies_prefixes_counts.to_frame(
        name='count')  # Convert to DataFrame for easier manipulation
    asserted_curies_prefixes_counts['in_obo'] = asserted_curies_prefixes_counts.index.isin(obo_ids)

    asserted_curies_prefixes_counts.to_csv('asserted_curies_prefixes_counts.tsv', index=True, sep='\t')

    ###

    ontology_adapters = create_ontology_adapters(ner_ontologies)

    # agg = AggregatorImplementation(implementations=ontology_adapters)

    # 10 minutes with envo and po, no manipulation of the input except for (lowercase ) uniqification
    annotations_list = normalized_context_strings.apply(
        lambda row: class_detection_by_label(
            row["normalized_context_string"],
            ontology_adapters,
            row["normalized_context_string_id"]
        ), axis=1
    ).explode().dropna()

    # Convert the list of dictionaries into a DataFrame
    curies_of_strings = pd.DataFrame(annotations_list.tolist())

    # more efficient to do this earlier?
    curies_of_strings = curies_of_strings.drop_duplicates()

    curies_of_strings['prefix_native'] = curies_of_strings['curie'].str.split(':').str[0]

    with biosamples_duckdb_engine.connect() as connection:
        curies_of_strings.to_sql('curies_ner', connection, if_exists='replace', index=False)

    biosamples_duckdb_engine.dispose()

    list_tables(biosamples_duckdb_engine)

    print(curies_of_strings['predicate_id'].value_counts())

    print(curies_of_strings['prefix_native'].value_counts())


if __name__ == '__main__':
    main()

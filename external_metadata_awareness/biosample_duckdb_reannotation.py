import pprint
from datetime import datetime

import click
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

import re
from typing import List

from oaklib import get_adapter

import xml.etree.ElementTree as ET
import requests
import pandas as pd


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


def create_engine_connection(db_path: str) -> Engine:
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


def list_tables(engine: Engine) -> None:
    """
    Prints a list of all tables in the current schema.

    Args:
        engine (sqlalchemy.engine.Engine): SQLAlchemy engine for the database.
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SHOW TABLES"))
            print("Tables in the current schema:")
            for row in result:
                print(f" - {row[0]}")
    except Exception as e:
        raise RuntimeError(f"Error listing tables: {e}")


def verify_table_creation(connection, schema_name: str, table_name: str) -> bool:
    """
    Verifies that a table exists and has data.

    Args:
        connection: The active SQLAlchemy connection.
        schema_name (str): Schema containing the table.
        table_name (str): Name of the table to verify.

    Returns:
        bool: True if table exists and has data, False otherwise.
    """
    try:
        # Check if table exists
        result = connection.execute(
            text(f"SELECT COUNT(*) FROM {schema_name}.{table_name}")
        )
        count = result.scalar()
        print(f"Table '{table_name}' contains {count} rows")
        return count > 0
    except Exception as e:
        print(f"Error verifying table '{table_name}': {e}")
        return False


def create_and_normalize_tables_with_keys(connection, schema_name: str) -> None:
    source_table = f'{schema_name}."attributes"'
    intermediate_table = f'{schema_name}."context_content_count"'
    normalized_table = f'{schema_name}."normalized_context_content_count"'

    with connection.begin():  # Begin a transaction
        try:
            # Drop intermediate and final tables if they exist
            connection.execute(text(f"DROP TABLE IF EXISTS {intermediate_table}"))
            connection.execute(text(f"DROP TABLE IF EXISTS {normalized_table}"))

            # Create intermediate table
            connection.execute(text(f"""
                CREATE TABLE {intermediate_table} AS
                SELECT content, COUNT(*) AS count
                FROM {source_table}
                WHERE harmonized_name IN ('env_broad_scale', 'env_local_scale', 'env_medium')
                GROUP BY content
                ORDER BY COUNT(*) DESC
            """))

            # Add a normalized content column to the intermediate table
            connection.execute(text(f"ALTER TABLE {intermediate_table} ADD COLUMN normalized_content VARCHAR"))

            # Populate the normalized content column
            connection.execute(text(f"""
                UPDATE {intermediate_table}
                SET normalized_content = regexp_replace(
                    trim(lower(content)),
                    '\\s+',
                    ' ',
                    'g'
                )
            """))

            # Create final table with unique keys
            connection.execute(text(f"""
                CREATE TABLE {normalized_table} AS
                SELECT 
                    row_number() OVER () AS id,  -- Add a unique key
                    normalized_content, 
                    SUM(count) AS count
                FROM {intermediate_table}
                GROUP BY normalized_content
                ORDER BY count DESC
            """))

            if verify_table_creation(connection, schema_name, "normalized_context_content_count"):
                print("All tables created and normalized successfully, with unique keys added to the final table")

        except Exception as e:
            raise RuntimeError(f"Error creating and normalizing tables: {e}")


def extract_curies_from_text(
        text: str,
        prefix_min_len: int = 3,
        prefix_max_len: int = 5,
        local_id_min_len: int = 6,
        local_id_max_len: int = 9,
        prefix_chars_allowed: str = r"[a-zA-Z]",
        local_id_chars_allowed: str = r"[0-9]",
        delimiter_chars_allowed: str = r"[_:]",
) -> List[tuple]:
    """
    Extract ontology class CURIEs from text and return them as tuples (prefix, delimiter, local_id).

    Args:
        text (str): The input text.
        prefix_min_len (int): Minimum length of the prefix part of the CURIE.
        prefix_max_len (int): Maximum length of the prefix part of the CURIE.
        local_id_min_len (int): Minimum length of the local ID part of the CURIE.
        local_id_max_len (int): Maximum length of the local ID part of the CURIE.
        prefix_chars_allowed (str): Allowed characters for the prefix.
        local_id_chars_allowed (str): Allowed characters for the local ID.
        delimiter_chars_allowed (str): Allowed delimiters between prefix and local ID.

    Returns:
        List[tuple]: A list of tuples containing (prefix, delimiter, local_id).
    """
    pattern = rf"""
        \b                                      # Word boundary
        (?P<prefix>{prefix_chars_allowed}{{{prefix_min_len},{prefix_max_len}}})  # Prefix
        (?P<delimiter>{delimiter_chars_allowed})                               # Delimiter
        (?P<local_id>{local_id_chars_allowed}{{{local_id_min_len},{local_id_max_len}}})  # Local ID
        \b                                      # Word boundary
    """
    matches = re.findall(pattern, text, re.VERBOSE)
    return [(prefix, delimiter, local_id) for prefix, delimiter, local_id in matches]


def process_table_and_extract_curies(connection, schema_name: str) -> None:
    """
    Extract ontology class CURIE parts (prefix, delimiter, local_id) from the first N rows
    of the normalized_context_content_count table, save them to a new table, and persist CURIE-free strings.

    Args:
        connection: The active SQLAlchemy connection.
        schema_name (str): Schema containing the table.
    """
    source_table = f'{schema_name}."normalized_context_content_count"'
    curies_to_save = []
    curie_free_strings_to_save = []

    try:
        # Fetch the rows from the normalized_content column
        query = text(f"SELECT id, normalized_content FROM {source_table}")
        result = connection.execute(query).fetchall()

        for row in result:
            id_, normalized_content = row

            # Ensure normalized_content is a string
            if not isinstance(normalized_content, str):
                normalized_content = ""  # Or use None, depending on your needs

            # Extract CURIE parts
            curies = extract_curies_from_text(normalized_content)

            # Save CURIE parts (prefix, delimiter, local_id) for each extraction
            for prefix, delimiter, local_id in curies:
                curies_to_save.append((id_, prefix, delimiter, local_id))

            # Generate CURIE-free strings by removing the CURIE parts
            curie_free_content = normalized_content
            for prefix, delimiter, local_id in curies:
                # Concatenate the prefix, delimiter, and local_id to form the full CURIE
                full_curie = f"{prefix}{delimiter}{local_id}"
                curie_free_content = curie_free_content.replace(full_curie, "\n")  # Use a delimiter

            # Remove parentheses and square brackets
            curie_free_content = curie_free_content.replace("(", "").replace(")", "").replace("[", "").replace("]",
                                                                                                               "").replace(
                "|", "")

            # Split into CURIE-free substrings and clean up
            curie_free_strings = [
                section.strip() for section in curie_free_content.split("\n")
                if section.strip()  # Exclude empty or whitespace-only strings
            ]

            # Save CURIE-free strings for each row
            for string in curie_free_strings:
                curie_free_strings_to_save.append((id_, string))

        # Persist the extracted CURIE parts (prefix, delimiter, local_id) to a new table
        save_extracted_curies_to_table(connection, schema_name, curies_to_save)

        # Persist the CURIE-free strings to a new table
        save_curie_free_strings_to_table(connection, schema_name, curie_free_strings_to_save)

        # Commit the transaction to ensure persistence
        connection.commit()

    except Exception as e:
        raise RuntimeError(f"Error processing table: {e}")


def save_extracted_curies_to_table(
        connection,
        schema_name: str,
        curies: List[tuple],
) -> None:
    """
    Save extracted CURIE parts (prefix, delimiter, local_id) to a new table.

    Args:
        connection: The active SQLAlchemy connection.
        schema_name (str): Schema containing the source table.
        curies (List[tuple]): A list of tuples with (source_id, prefix, delimiter, local_id).
    """
    table_name = f'{schema_name}."extracted_curies"'

    try:
        # Drop the table if it already exists
        connection.execute(text(f"DROP TABLE IF EXISTS {table_name}"))

        # Create the new table with separate columns for prefix, delimiter, and local_id
        connection.execute(text(f"""
            CREATE TABLE {table_name} (
                source_id INTEGER,
                prefix TEXT,
                delimiter TEXT,
                local_id TEXT
            )
        """))

        # Insert extracted CURIE parts in a loop
        insert_query = text(f"""
            INSERT INTO {table_name} (source_id, prefix, delimiter, local_id)
            VALUES (:source_id, :prefix, :delimiter, :local_id)
        """)
        for source_id, prefix, delimiter, local_id in curies:
            connection.execute(insert_query, {
                "source_id": source_id,
                "prefix": str(prefix),  # Ensure the prefix is inserted as a string
                "delimiter": str(delimiter),  # Ensure the delimiter is inserted as a string
                "local_id": str(local_id)  # Ensure the local_id is inserted as a string
            })

        print(f"Extracted CURIE parts saved to table '{table_name}' successfully.")

    except Exception as e:
        raise RuntimeError(f"Error saving extracted CURIE parts: {e}")


def save_curie_free_strings_to_table(
        connection,
        schema_name: str,
        strings: List[tuple],
) -> None:
    """
    Save CURIE-free strings to a new table.

    Args:
        connection: The active SQLAlchemy connection.
        schema_name (str): Schema containing the source table.
        strings (List[tuple]): A list of tuples with (source_id, curie_free_string).
    """
    table_name = f'{schema_name}."curie_free_strings"'

    try:
        # Drop the table if it already exists
        connection.execute(text(f"DROP TABLE IF EXISTS {table_name}"))

        # Create the new table
        connection.execute(text(f"""
            CREATE TABLE {table_name} (
                source_id INTEGER,
                curie_free_string TEXT
            )
        """))

        # Insert CURIE-free strings in a loop
        insert_query = text(f"""
            INSERT INTO {table_name} (source_id, curie_free_string)
            VALUES (:source_id, :curie_free_string)
        """)
        for source_id, string in strings:
            connection.execute(insert_query, {"source_id": source_id, "curie_free_string": string})

        print(f"CURIE-free strings saved to table '{table_name}' successfully.")

    except Exception as e:
        raise RuntimeError(f"Error saving CURIE-free strings: {e}")


def count_curie_free_strings(connection, schema_name: str) -> None:
    """
    Create a new table with unique value counts from the curie_free_string column
    in the curie_free_strings table, with an added unique identifier.

    Args:
        connection: The active SQLAlchemy connection.
        schema_name (str): Schema containing the source table.
    """
    source_table = f'{schema_name}."curie_free_strings"'
    target_table = f'{schema_name}."curie_free_string_counts"'

    try:
        # Begin the transaction
        trans = connection.begin()

        # Drop the target table if it already exists
        connection.execute(text(f"DROP TABLE IF EXISTS {target_table}"))

        # Create the new table with unique value counts and a unique id
        connection.execute(text(f"""
            CREATE TABLE {target_table} AS
            SELECT 
                ROW_NUMBER() OVER () AS id,  -- Generate unique identifier for each row
                curie_free_string,
                COUNT(*) AS count
            FROM {source_table}
            GROUP BY curie_free_string
            -- HAVING COUNT(*) > 1
            ORDER BY count DESC
        """))

        print(f"CURIE-free string counts saved to table '{target_table}' successfully with unique ids.")

        # Commit the transaction
        trans.commit()

    except Exception as e:
        if 'trans' in locals():
            trans.rollback()  # Rollback in case of any errors
        raise RuntimeError(f"Error creating CURIE-free string counts table: {e}")


def get_curie_free_strings(db_path: str, schema_name: str) -> pd.DataFrame:
    """
    Retrieve curie_free_string values and their unique id from the curie_free_string_counts table
    where the count is greater than 1, in preparation for annotation.

    Args:
        db_path (str): Path to the DuckDB file.
        schema_name (str): Schema name where the table resides.

    Returns:
        pd.DataFrame: A DataFrame containing curie_free_string values with their ids and counts.
    """
    # Create the database connection
    engine = create_engine(f"duckdb:///{db_path}")

    # Define the query to retrieve curie_free_string values with count > 1
    query = f"""
    SELECT id, curie_free_string
    FROM {schema_name}."curie_free_string_counts"
    WHERE count > 1
    ORDER BY count DESC
    """

    # Execute the query and load the result into a pandas DataFrame
    with engine.connect() as connection:
        df = pd.read_sql(text(query), connection)

    return df


def annotate_curie_free_strings(curie_free_strings_df, ontology_adapters,
                                min_annotated_length: int = 3) -> pd.DataFrame:
    """
    Annotate curie-free strings using multiple ontology adapters and collect the annotations.
    Only annotations with a match string length >= min_annotated_length are included.
    Additionally, a flag 'is_longest_match' is added to indicate the longest match for each curie_free_string.

    Args:
        curie_free_strings_df (pd.DataFrame): DataFrame containing curie_free_string and its id.
        ontology_adapters (dict): Dictionary of ontology adapters.
        min_annotated_length (int): Minimum length for the annotated match string to be included.

    Returns:
        pd.DataFrame: A DataFrame with the annotations, deduplicated and filtered by length, with a flag for the longest match.
    """
    curie_free_string_annotations = []

    # Loop over each row in the DataFrame
    for _, row in curie_free_strings_df.iterrows():
        curie_free_string = row['curie_free_string']
        curie_free_string_id = row['id']

        # List to store all annotations for the current curie_free_string
        annotations_for_this_string = []

        # Annotate curie_free_string using each ontology adapter
        for _, adapter in ontology_adapters.items():
            annotations = adapter.annotate_text(curie_free_string)

            if annotations:  # If there are annotations
                for annotation in annotations:
                    subject_string = annotation.match_string

                    # Only include annotations where subject_string length is >= min_annotated_length
                    if len(subject_string) >= min_annotated_length:
                        # Build the annotation dictionary
                        annotations_dict = {
                            "id": curie_free_string_id,
                            "subject_string": subject_string,
                            "subject_start": annotation.subject_start,
                            "subject_end": annotation.subject_end,
                            "predicate_id": annotation.predicate_id,
                            "concluded_curie": annotation.object_id,
                            "object_string": annotation.object_label,
                        }
                        annotations_for_this_string.append(annotations_dict)

        # Determine the longest match for this curie_free_string
        if annotations_for_this_string:
            longest_annotation = max(annotations_for_this_string, key=lambda x: len(x['subject_string']))

            # Mark each annotation as the longest or not
            for annotation in annotations_for_this_string:
                annotation['is_longest_match'] = annotation['subject_string'] == longest_annotation['subject_string']

            # Append the annotations for this curie_free_string to the final list
            curie_free_string_annotations.extend(annotations_for_this_string)

    # Convert the list of annotations to a DataFrame
    curie_free_string_annotations_frame = pd.DataFrame(curie_free_string_annotations)

    # Deduplicate the DataFrame
    curie_free_string_annotations_frame = curie_free_string_annotations_frame.drop_duplicates()

    return curie_free_string_annotations_frame


def save_annotations_to_duckdb(connection, schema_name: str, df: pd.DataFrame, table_name: str) -> None:
    """
    Save the annotations DataFrame to a new DuckDB table.

    Args:
        connection: The active SQLAlchemy connection.
        schema_name (str): Schema name for the DuckDB database.
        df (pd.DataFrame): DataFrame containing the annotations.
        table_name (str): Name of the table where data will be inserted.
    """
    # Ensure the table name is properly formatted for DuckDB
    full_table_name = f'{schema_name}."{table_name}"'

    try:
        # Start a transaction
        trans = connection.begin()

        # If the table exists, drop it to prevent conflicts
        connection.execute(text(f"DROP TABLE IF EXISTS {full_table_name}"))

        # Write the DataFrame to the DuckDB table
        df.to_sql(table_name, con=connection, schema=schema_name, if_exists='replace', index=False)

        print(f"Annotations saved to table '{full_table_name}' successfully.")

        # Commit the transaction
        trans.commit()

    except Exception as e:
        if 'trans' in locals():
            trans.rollback()  # Rollback in case of any errors
        raise RuntimeError(f"Error saving annotations to DuckDB: {e}")


def create_by_re_annotation_table(connection, schema_name: str) -> None:
    """
    Creates a table 'by_re_annotation' based on the provided SQL query,
    which extracts annotations and merges in the corresponding CURIE labels.

    Args:
        connection: The active SQLAlchemy connection.
        schema_name (str): The schema where the tables reside.
    """
    target_table = f'{schema_name}."by_re_annotation"'

    query = f"""
    CREATE TABLE {target_table} AS
    SELECT DISTINCT
        a.accession,
        a.package_content,
        np.group AS package_group,
        np.EnvPackage,
        a.harmonized_name,
        a.content,
        'by re-annotation' as conclusion_method,
        cfsa.predicate_id,
        cfsa.concluded_curie,
        cfsa.object_string,
        cl.label AS concluded_label,  -- Join curie_labels to get the label
        cl.ontology AS label_source
    FROM
        {schema_name}."attributes" a
    LEFT JOIN {schema_name}."context_content_count" ccc
        ON a.content = ccc.content
    LEFT JOIN {schema_name}."normalized_context_content_count" nccc
        ON ccc.normalized_content = nccc.normalized_content
    LEFT JOIN {schema_name}."curie_free_strings" cfs
        ON nccc.id = cfs.source_id
    LEFT JOIN {schema_name}."curie_free_string_counts" cfsc
        ON cfs.curie_free_string = cfsc.curie_free_string
    LEFT JOIN {schema_name}."curie_free_string_annotations" cfsa
        ON cfsc.id = cfsa.id
    LEFT JOIN {schema_name}."curie_labels" cl
        ON cfsa.concluded_curie = cl.curie
    LEFT JOIN {schema_name}."ncbi_packages" np
        ON a.package_content = np.Name  -- Join with ncbi_packages
    WHERE
        cfsa.is_longest_match
        AND a.harmonized_name IN ('env_broad_scale', 'env_local_scale', 'env_medium');
    """

    try:
        # Drop the target table if it already exists
        connection.execute(text(f"DROP TABLE IF EXISTS {target_table}"))

        # Create the target table using the provided query
        connection.execute(text(query))

        print(f"Table '{target_table}' created successfully.")

    except Exception as e:
        raise RuntimeError(f"Error creating '{target_table}' table: {e}")


def create_by_curie_extraction_table(connection, schema_name: str) -> None:
    target_table = f'{schema_name}."by_curie_extraction"'

    query = f"""
    CREATE TABLE {target_table} AS
    SELECT DISTINCT
        a.accession,
        a.package_content,
        np.group AS package_group,
        np.EnvPackage,
        a.harmonized_name,
        a.content,
        'by curie extraction' as conclusion_method,
        '' as predicate_id,
        concat(upper(ec.prefix), ':', ec.local_id) AS concluded_curie,
        '' as object_string,
        cl.label AS concluded_label,
        cl.ontology AS label_source
    FROM
        {schema_name}."attributes" a
    LEFT JOIN {schema_name}."context_content_count" ccc
        ON a.content = ccc.content
    LEFT JOIN {schema_name}."normalized_context_content_count" nccc
        ON ccc.normalized_content = nccc.normalized_content
    LEFT JOIN {schema_name}."extracted_curies" ec
        ON nccc.id = ec.source_id
    LEFT JOIN {schema_name}."curie_labels" cl
        ON concat(upper(ec.prefix), ':', ec.local_id) = cl.curie
    LEFT JOIN {schema_name}."ncbi_packages" np
        ON a.package_content = np.Name
    WHERE
        a.harmonized_name IN ('env_broad_scale', 'env_local_scale', 'env_medium')
        AND ec.local_id IS NOT NULL;
    """

    try:
        # Directly execute the SQL commands using the active transaction
        connection.execute(text(f"DROP TABLE IF EXISTS {target_table}"))
        connection.execute(text(query))
        print(f"Table '{target_table}' created successfully.")
    except Exception as e:
        raise RuntimeError(f"Error creating '{target_table}' table: {e}")


def create_curie_labels_table(connection, schema_name: str, ontology_adapters: dict) -> None:
    """
    Fetch CURIEs and their labels from the provided ontology adapters,
    filter out tuples where the label is None, and store the results in a new 'curie_labels' table,
    including the ontology key (short name) for each CURIE.

    Args:
        connection: The active SQLAlchemy connection.
        schema_name (str): The schema where the tables reside.
        ontology_adapters (dict): A dictionary of ontology adapters.
    """
    target_table = f'{schema_name}."curie_labels"'

    try:
        # Start a transaction
        trans = connection.begin()

        # Prepare a list to collect CURIEs, their labels, and ontology keys
        all_curies_and_labels = []

        # Fetch CURIEs and labels for each ontology adapter
        for short_name, adapter in ontology_adapters.items():
            # Get all CURIEs and their labels from the adapter
            curies_and_labels = list(adapter.labels(curies=list(adapter.entities())))

            # Filter out tuples where the label is None
            filtered_curies_and_labels = [
                (curie, label, short_name)  # Add ontology key (short_name) to each tuple
                for curie, label in curies_and_labels if label is not None
            ]

            # Add the filtered results to the overall list
            all_curies_and_labels.extend(filtered_curies_and_labels)

        # Convert the filtered data into a DataFrame
        curie_labels_df = pd.DataFrame(all_curies_and_labels, columns=["curie", "label", "ontology"])

        # Create the 'curie_labels' table in DuckDB
        connection.execute(text(f"DROP TABLE IF EXISTS {target_table}"))

        # Write the DataFrame to DuckDB
        curie_labels_df.to_sql('curie_labels', con=connection, schema=schema_name, if_exists='replace', index=False)

        print(f"Table '{target_table}' created and populated successfully.")

        # Commit the transaction to ensure persistence
        trans.commit()

    except Exception as e:
        if 'trans' in locals():
            trans.rollback()  # Rollback in case of errors
        raise RuntimeError(f"Error creating and saving 'curie_labels' table: {e}")


def create_ontology_class_candidates_view(connection, schema_name: str) -> None:
    """
    Create a view `ontology_class_candidates` in the DuckDB database.

    This view is a union of all rows from the `by_curie_extraction` table
    and the `by_re_annotation` table in the specified schema.

    Args:
        connection: SQLAlchemy connection object to the DuckDB database.
        schema_name (str): Name of the schema where the tables are located.
    """
    # Define the SQL for creating the view
    create_view_sql = f"""
    CREATE VIEW {schema_name}.ontology_class_candidates AS
    SELECT
        *
    FROM
        {schema_name}.by_curie_extraction
    UNION
    SELECT
        *
    FROM
        {schema_name}.by_re_annotation;
    """

    # Wrap the raw SQL string with sqlalchemy.text()
    create_view_query = text(create_view_sql)

    try:
        # Execute the SQL using the provided connection
        connection.execute(create_view_query)
        print(f"View '{schema_name}.ontology_class_candidates' created successfully.")
    except Exception as e:
        raise RuntimeError(f"Error creating view '{schema_name}.ontology_class_candidates': {e}")


def create_ncbi_packages_table(schema_name: str, connection) -> None:
    """Creates and populates the ncbi_packages table with data from NCBI BioSample packages XML."""
    import requests
    import xml.etree.ElementTree as ET
    import pandas as pd

    target_table = f'{schema_name}."ncbi_packages"'

    try:
        trans = connection.begin()

        url = "https://www.ncbi.nlm.nih.gov/biosample/docs/packages/?format=xml"
        response = requests.get(url)
        root = ET.fromstring(response.content)

        node_names = {child.tag for package in root.findall('.//Package')
                      for child in package if child.tag not in ['Antibiogram', 'Name']}

        data = []
        for package in root.findall('.//Package'):
            row = {
                'Name': package.find('Name').text,
                'group': package.get('group', '')
            }
            for node in node_names:
                element = package.find(node)
                row[node] = element.text if element is not None else ''
            data.append(row)

        df = pd.DataFrame(data)
        cols = ['Name', 'group'] + [col for col in df.columns if col not in ['Name', 'group']]
        df = df[cols]

        connection.execute(text(f"DROP TABLE IF EXISTS {target_table}"))
        df.to_sql(target_table.replace(f'{schema_name}."', '').replace('"', ''),
                  connection,
                  schema=schema_name,
                  if_exists='append',
                  index=False)

        trans.commit()

        if verify_table_creation(connection, schema_name, "ncbi_packages"):
            print("NCBI packages table created successfully")

    except Exception as e:
        if 'trans' in locals():
            trans.rollback()
        raise RuntimeError(f"Error creating NCBI packages table: {e}")


@click.command()
@click.option(
    "--db-path",
    required=True,
    type=click.Path(exists=True, file_okay=True, readable=True),
    help="Path to the DuckDB file.",
)
@click.option(
    "--schema-name",
    default="main",
    type=str,
    help="Schema name where the source table resides (default is 'main').",
)
@click.option(
    "--ontologies",
    multiple=True,
    type=str,
    help="List of ontology short names to use for annotation (e.g., 'envo', 'po')."
)
def main(db_path: str, schema_name: str, ontologies: list) -> None:
    ontology_adapters = create_ontology_adapters(ontologies)
    engine = create_engine_connection(db_path)

    try:
        print("\nTables before operations:")
        list_tables(engine)

        # Use a connection for all operations
        with engine.connect() as connection:  # Open a connection
            # Pass the connection object instead of the engine
            create_and_normalize_tables_with_keys(connection, schema_name)

            print("\nTables after operations:")
            list_tables(engine)

            # Process tables and extract CURIEs
            process_table_and_extract_curies(connection, schema_name)

            print("\nTables after CURIE extraction:")
            list_tables(engine)

            # Count CURIE-free strings
            count_curie_free_strings(connection, schema_name)

            print("\nTables after CURIE-free string count:")
            list_tables(engine)

            # Retrieve CURIE-free strings for annotation
            curie_free_strings_df = get_curie_free_strings(db_path, schema_name)

            # Annotate CURIE-free strings
            curie_free_string_annotations_frame = annotate_curie_free_strings(
                curie_free_strings_df, ontology_adapters
            )

            # Save annotations to DuckDB
            save_annotations_to_duckdb(
                connection, schema_name, curie_free_string_annotations_frame, "curie_free_string_annotations"
            )

            # Create CURIE labels table
            create_curie_labels_table(connection, schema_name, ontology_adapters)

            # Create NCBI packages table
            create_ncbi_packages_table(schema_name, connection)

            # Create `by_re_annotation` table
            print("\nStarting to create by_re_annotation table")
            print("Current Time =", datetime.now().strftime("%H:%M:%S"))
            create_by_re_annotation_table(connection, schema_name)
            print("\nFinished creating by_re_annotation table")
            print("Current Time =", datetime.now().strftime("%H:%M:%S"))

            # Create `by_curie_extraction` table
            print("\nStarting to create by_curie_extraction table")
            print("Current Time =", datetime.now().strftime("%H:%M:%S"))
            create_by_curie_extraction_table(connection, schema_name)
            print("\nFinished creating by_curie_extraction table")
            print("Current Time =", datetime.now().strftime("%H:%M:%S"))

            # Create `ontology_class_candidates` view
            create_ontology_class_candidates_view(connection, schema_name)

            # Explicit commit at the end
            print("\nCommitting transaction...")
            connection.commit()

        print("\nTables after all operations:")
        list_tables(engine)

    except Exception as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()

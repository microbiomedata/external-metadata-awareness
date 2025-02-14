import pprint

import pymongo


def get_mongo_client(
        username: str = None,
        password: str = None,
        host: str = "localhost",
        port: int = 27017,
        direct_connection: bool = True,  # Changed default to True
        auth_mechanism: str = "SCRAM-SHA-256",
        auth_source: str = "admin"
) -> pymongo.MongoClient:
    """
    Establishes a connection to a MongoDB server.

    Args:
        username: Username for authentication (optional).
        password: Password for authentication (optional).
        host: Hostname of the MongoDB server (defaults to localhost).
        port: Port of the MongoDB server (defaults to 27017).
        direct_connection: Use a direct connection (defaults to True).
        auth_mechanism: Authentication mechanism (defaults to SCRAM-SHA-256).
        auth_source: Authentication source database (defaults to admin).

    Returns:
        A pymongo.MongoClient instance.
    """

    if username and password:
        mongo_uri = f"mongodb://{username}:{password}@{host}:{port}/"
        client = pymongo.MongoClient(
            mongo_uri,
            directConnection=direct_connection,
            authMechanism=auth_mechanism,
            authSource=auth_source
        )
    else:
        client = pymongo.MongoClient(
            host,
            port,
            directConnection=direct_connection
        )

    return client


def fetch_mongodb_records_by_text(
        client: pymongo.MongoClient,
        db_name: str,
        collection_name: str,
        search_text: str,
        case_insensitive: bool = True
) -> pymongo.cursor.Cursor:
    """
    Fetches records from a MongoDB collection using an existing text index.

    This function assumes that a text index already exists on the
    specified collection. It does not attempt to create an index.

    Args:
        client: A pymongo.MongoClient instance.
        db_name: Name of the MongoDB database.
        collection_name: Name of the MongoDB collection.
        search_text: Text to search for.
        case_insensitive: Whether to perform a case-insensitive search.

    Returns:
        A MongoDB cursor with the search results.
    """

    db = client[db_name]
    collection = db[collection_name]

    # Construct the search query
    if case_insensitive:
        search_query = {
            "$text": {
                "$search": search_text.lower(),
                "$caseSensitive": False
            }
        }
    else:
        search_query = {
            "$text": {"$search": search_text}
        }

    return collection.find(search_query)


def fetch_mongodb_records_by_path(
        client: pymongo.MongoClient,
        db_name: str,
        collection_name: str,
        search_path: str,
        search_value: str,
) -> pymongo.cursor.Cursor:
    """
    Fetches records from a MongoDB collection by searching for a specific value
    at a given path within the documents.

    Args:
        client: A pymongo.MongoClient instance.
        db_name: Name of the MongoDB database.
        collection_name: Name of the MongoDB collection.
        search_path: Path within the document to search (e.g., "Attributes.Attribute.harmonized_name").
        search_value: Value to search for at the specified path.

    Returns:
        A MongoDB cursor with the search results.
    """

    db = client[db_name]
    collection = db[collection_name]

    # Construct the search query
    search_query = {search_path: search_value}

    return collection.find(search_query)


def fetch_mongodb_records_by_path_in(
        client: pymongo.MongoClient,
        db_name: str,
        collection_name: str,
        search_path: str,
        search_values: list
) -> pymongo.cursor.Cursor:
    """
    Fetches records from a MongoDB collection where the field at the specified path
    matches any of the values in the provided list.

    Args:
        client: A pymongo.MongoClient instance.
        db_name: Name of the MongoDB database.
        collection_name: Name of the MongoDB collection.
        search_path: Path within the document to search (e.g., "Attributes.Attribute.harmonized_name").
        search_values: A list of values to search for at the specified path.

    Returns:
        A MongoDB cursor with the search results.
    """

    db = client[db_name]
    collection = db[collection_name]

    # Construct the search query using $in
    search_query = {search_path: {"$in": search_values}}

    return collection.find(search_query)


def lod_to_dod(list_of_dicts, key_to_extract):
    """
    Transforms a list of dictionaries into a dictionary of dictionaries.

    The keys of the outer dictionary are extracted from the inner dictionaries
    using the specified key. This key is then removed from the inner dictionaries.

    Args:
      list_of_dicts: A list of dictionaries.
      key_to_extract: The key to extract from each inner dictionary to use as
                      the key in the outer dictionary.

    Returns:
      A dictionary of dictionaries.
    """

    transformed_dict = {}
    for inner_dict in list_of_dicts:
        if key_to_extract in inner_dict:
            outer_key = inner_dict.pop(key_to_extract)
            transformed_dict[outer_key] = inner_dict
        else:
            # Handle the case where the key is not found, if necessary
            pass  # or raise an exception, or print a warning, etc.

    return transformed_dict

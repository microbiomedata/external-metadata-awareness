import time
import os
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import click
import lxml.etree as ET
from external_metadata_awareness.mongodb_connection import get_mongo_client


@click.command()
@click.option('--file-path', default='../downloads/biosample_set.xml', help='Path to the XML file.')
@click.option('--collection-name', default='biosamples', help='Collection name.')
@click.option('--node-type', default='BioSample', help='Type of the XML node to process.')
@click.option('--id-field', default='id', help='Name of the ID attribute within the node.')
@click.option('--max-elements', default=100000, type=int,
              help='Maximum number of elements to process.')
@click.option('--anticipated-last-id', default=45000000, type=int,
              help='Anticipated last ID for progress calculation.')
@click.option('--mongo-uri', required=True, help='MongoDB connection URI (must start with mongodb:// and include database name).')
@click.option('--env-file', default=None, help='Path to .env file for credentials (should contain MONGO_USER and MONGO_PASSWORD).')
@click.option('--verbose', is_flag=True, help='Show verbose connection output.')
def load_xml_to_mongodb(file_path: str, collection_name: str, node_type: str,
                        id_field: str, max_elements: Optional[int] = None,
                        anticipated_last_id: Optional[int] = None, mongo_uri: str = None,
                        env_file: Optional[str] = None, verbose: bool = False):
    """
    Loads data from an XML file into MongoDB, preserving the nested structure.

    This script uses lxml's iterparse for incremental processing, handles
    different node types, and allows specifying the ID attribute for progress
    calculation.
    """

    def element_to_dict(elem):
        """
        Recursively converts an XML element to a nested dictionary.
        """
        doc = {}
        if elem.text and elem.text.strip():
            doc['content'] = elem.text.strip()
        doc.update(elem.attrib)
        for child in elem:
            child_doc = element_to_dict(child)
            if child.tag in doc:
                if isinstance(doc[child.tag], list):
                    doc[child.tag].append(child_doc)
                else:
                    doc[child.tag] = [doc[child.tag], child_doc]
            else:
                doc[child.tag] = child_doc
        return doc

    try:
        client = get_mongo_client(
            mongo_uri=mongo_uri,
            env_file=env_file,
            debug=verbose
        )
        
        # Extract database name from URI
        parsed = urlparse(mongo_uri)
        db_name = parsed.path.lstrip("/").split("?")[0]
        
        if verbose:
            print(f"Using database: {db_name}")
            
        db = client[db_name]
        collection = db[collection_name]

        start_time = time.time()
        processed_count = 0

        for event, elem in ET.iterparse(file_path, events=('end',)):
            if elem.tag == node_type:
                doc = element_to_dict(elem)
                collection.insert_one(doc)
                processed_count += 1

                # Show progress based on max_elements if provided, otherwise use anticipated_last_id
                if processed_count % 10000 == 0:
                    if max_elements:
                        progress = (processed_count / max_elements) * 100
                    elif anticipated_last_id:
                        progress = (int(elem.attrib.get(id_field, 0)) / anticipated_last_id) * 100
                    else:
                        progress = 0
                        
                    elapsed_time = time.time() - start_time
                    print(f"Processed {processed_count} {node_type} nodes ({progress:.2f}%), "
                          f"elapsed time: {elapsed_time:.2f} seconds")

                if max_elements and processed_count >= max_elements:
                    print(f"Reached max_elements ({max_elements}). Stopping.")
                    break

                elem.clear()

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    load_xml_to_mongodb()

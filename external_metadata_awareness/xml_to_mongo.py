import time
from typing import Optional

import click
from pymongo import MongoClient
import lxml.etree as ET


@click.command()
@click.option('--file-path', default='../downloads/biosample_set.xml', help='Path to the XML file.')
@click.option('--db-name', default='biosamples_dev', help='Database name.')
@click.option('--collection-name', default='biosamples_dev', help='Collection name.')
@click.option('--node-type', default='BioSample', help='Type of the XML node to process.')
@click.option('--id-field', default='id', help='Name of the ID attribute within the node.')
@click.option('--max-elements', default=100000, type=int,
              help='Maximum number of elements to process.')
@click.option('--anticipated-last-id', default=45000000, type=int,
              help='Anticipated last ID for progress calculation.')
@click.option('--mongo-host', default='localhost', help='MongoDB host address.')
@click.option('--mongo-port', default=27017, type=int, help='MongoDB port.')
def load_xml_to_mongodb(file_path: str, db_name: str, collection_name: str, node_type: str,
                        id_field: str, max_elements: Optional[int] = None,
                        anticipated_last_id: Optional[int] = None, mongo_host: str = 'localhost',
                        mongo_port: int = 27017):
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
        client = MongoClient(host=mongo_host, port=mongo_port)
        db = client[db_name]
        collection = db[collection_name]

        start_time = time.time()
        processed_count = 0

        for event, elem in ET.iterparse(file_path, events=('end',)):
            if elem.tag == node_type:
                doc = element_to_dict(elem)
                collection.insert_one(doc)
                processed_count += 1

                if anticipated_last_id:
                    if processed_count % 10000 == 0:
                        progress = (int(elem.attrib.get(id_field, 0)) / anticipated_last_id) * 100
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

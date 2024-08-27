import click
from datetime import datetime
import lxml.etree as ET
from pymongo import MongoClient
from typing import Any, Dict


@click.command()
@click.option('--file-path', default='../downloads/biosample_set.xml', help='Path to the XML file.')
@click.option('--node-type', default='BioSample')
@click.option('--id-field', default='id')
@click.option('--db-name', default='biosamples_dev', help='Database name.')
@click.option('--collection-name', default='biosamples_dev', help='Collection name.')
@click.option('--max-elements', default=100000, type=int,
              help='Maximum number of elements to process.')  # expecting ~ 45 million
@click.option('--anticipated-last-id', default=100000, type=int, help='Anticipated last ID for progress calculation.')
def process_xml_with_progress(file_path: str, db_name: str, collection_name: str, max_elements: int,
                              anticipated_last_id: int, node_type: str, id_field: str):
    """
    Process the specified XML file and store its contents into a MongoDB collection with progress reporting.

    :param id_field:
    :param node_type:
    :param file_path: Path to the XML file.
    :param db_name: Name of the MongoDB database.
    :param collection_name: Name of the MongoDB collection.
    :param max_elements: Maximum number of XML elements to process.
    :param anticipated_last_id: Highest expected ID in the XML elements for progress calculation.
    """
    client = MongoClient('localhost', 27017)
    db = client[db_name]
    collection = db[collection_name]

    context = ET.iterparse(file_path, events=('end',), tag=node_type)
    count = 0
    last_reported_progress = 0

    for event, elem in context:
        if count >= max_elements:
            break

        current_id = int(elem.get(id_field))
        progress = current_id / anticipated_last_id

        if progress - last_reported_progress >= 0.001:
            current_time = datetime.now().isoformat()
            print(f"{current_time}: {current_id}, {progress * 100:.1f}%")
            last_reported_progress = progress

        element_dict = xml_to_dict(elem)
        wrapped_dict = {node_type: element_dict}
        collection.insert_one(wrapped_dict)
        count += 1

        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]

    del context
    client.close()


def xml_to_dict(elem: ET.Element) -> Dict[str, Any]:
    """
    Converts an XML element into a dictionary, handling attributes and child elements recursively.

    :param elem: The XML element to convert.
    :return: A dictionary representing the XML element.
    """
    if not elem.getchildren() and elem.text:
        text = elem.text.strip()
        return {**elem.attrib, 'content': text} if elem.attrib else text

    result = {child.tag: xml_to_dict(child) for child in elem}
    return {**elem.attrib, **result}


if __name__ == '__main__':
    process_xml_with_progress()

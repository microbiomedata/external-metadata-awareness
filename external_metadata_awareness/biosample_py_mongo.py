import pprint
from datetime import datetime

import lxml.etree as ET
from pymongo import MongoClient

# file_path = "../local/books.xml"
# node_type = "book"


file_path = "../local/biosample_set.xml"
node_type = "BioSample"
db_name = "biosamples"
collection_name = "biosamples"
id_field = "id"
max_elements = 44000000  # Set the maximum number of elements to process
anticipated_last_id = 40000000  # Example: user specified last ID # percent progress will always go over 100%. Possibly 115.


def xml_to_dict(elem):
    # Base case for simple elements with no children
    if not elem.getchildren() and elem.text:
        text = elem.text.strip()
        if elem.attrib:
            # If the element has attributes, return it as a dictionary with those attributes and text
            attrib_dict = {**elem.attrib, 'value': text}
            return attrib_dict
        else:
            # If no attributes, return the text directly
            return text

    # Create a dictionary to accumulate children
    result = {}
    for child in elem:
        child_result = xml_to_dict(child)
        # Check if child tag is already present in the result
        if child.tag in result:
            # If it's not a list yet, make it a list
            if not isinstance(result[child.tag], list):
                result[child.tag] = [result[child.tag]]
            # Append the new child result to the list
            result[child.tag].append(child_result)
        else:
            # If not present, just add it to the result
            result[child.tag] = child_result

    # Merge element's attributes with its children
    result = {**elem.attrib, **result}

    return result


def process_xml(file_path, db, collection_name, max_elements):
    # Connect to MongoDB
    client = MongoClient('localhost', 27017)
    db = client[db]
    collection = db[collection_name]

    # Use iterparse to iterate over elements
    context = ET.iterparse(file_path, events=('end',))
    count = 0  # Initialize counter for processed elements
    for event, elem in context:
        if elem.tag == node_type:  # Specify the tag you're interested in
            if 0 < max_elements <= count:
                break  # Stop processing if the limit is reached
            element_dict = xml_to_dict(elem)
            print(element_dict[id_field])
            # pprint.pprint(element_dict)
            # Insert the dictionary into MongoDB
            collection.insert_one(element_dict)
            count += 1  # Increment the counter

            # Once processed, clear the element to free up memory
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]

    del context  # Explicitly delete the context to free memory
    client.close()  # Close the MongoDB connection


def process_xml_with_progress(file_path, db, collection_name, max_elements, anticipated_last_id):
    # Connect to MongoDB
    client = MongoClient('localhost', 27017)
    db = client[db]
    collection = db[collection_name]

    # Setup the parser for end events to capture each BioSample
    context = ET.iterparse(file_path, events=('end',), tag='BioSample')
    count = 0  # Initialize counter for processed elements
    last_reported_progress = 0  # To keep track of the last reported progress step

    # Iterate over each BioSample element
    for event, elem in context:
        if elem.tag == 'BioSample':
            current_id = int(elem.get('id'))
            progress = current_id / anticipated_last_id
            # Check if we should report progress
            if progress - last_reported_progress >= 0.001:
                current_time = datetime.now().isoformat()
                print(f"{current_time}: {current_id}, {progress * 100:.1f}%")
                last_reported_progress = progress

            if count >= max_elements:
                break  # Stop processing if the limit is reached

            # Assume xml_to_dict is a previously defined function to convert XML element to dict
            element_dict = xml_to_dict(elem)
            collection.insert_one(element_dict)
            count += 1  # Increment the counter

            # Once processed, clear the element to free up memory
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]

    del context  # Explicitly delete the context to free memory
    client.close()  # Close the MongoDB connection


# Replace 'your_file.xml' with your XML file's path and specify your MongoDB database and collection
# process_xml(file_path, db_name, collection_name, max_elements)
process_xml_with_progress(file_path, db_name, collection_name, max_elements, anticipated_last_id)

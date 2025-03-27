#%%
import requests
import json
from datetime import datetime
import pprint

from pymongo import MongoClient

from collections import Counter
from collections import defaultdict

import pandas as pd

from dotenv import dotenv_values
#%%
# Specify the path to your .env file
env_path = "../../local/.env"
#%%
# Load variables into a dictionary
env_vars = dotenv_values(env_path)
#%%
REFRESH_TOKEN = env_vars['NMDC_DATA_SUBMISSION_REFRESH_TOKEN']
#%%
# Connect to the local MongoDB instance (default connection)
client = MongoClient('mongodb://localhost:27017/')  # Connect to your local MongoDB
db = client['misc_metadata']  # for alignment with mongo-ncbi-loadbalancer
collection = db['nmdc_submissions']
#%%
# Set the API endpoint for refreshing the token
url = 'https://data.microbiomedata.org/auth/refresh'
#%%
# Set the payload with the Refresh Token
payload = {
    "refresh_token": REFRESH_TOKEN
}
#%%
# Set the headers
headers = {
    'Content-Type': 'application/json'
}
#%%
# Make the POST request to refresh the token
response = requests.post(url, data=json.dumps(payload), headers=headers)
#%%
# Check if the request was successful
if response.status_code == 200:
    data = response.json()
    access_token = data['access_token']
    print(f"Access Token: {access_token}")
else:
    print(f"Failed to get access token: {response.status_code}")
    print(response.text)

#%%
# Set the API endpoint for metadata submissions
url = 'https://data.microbiomedata.org/api/metadata_submission'

#%%
# Set the headers with the Access Token
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {access_token}'
}

#%%
# Set the query parameters (default values)
params = {
    'column_sort': 'created',  # Sorting by 'created' column
    'sort_order': 'desc',      # Descending order
    'offset': 0,               # Starting from the first record (default value)
    'limit': 25                # Default to 25 records per page
}

#%%
# Initialize an empty list to hold all the records
all_records = []
#%%
# Start the pagination loop
while True:
    # Print timestamp for each request
    print(f"Request sent at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Make the GET request to fetch metadata submissions
    response = requests.get(url, headers=headers, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()

        # If there are no records, stop pagination
        if not data.get('results'):
            break

        # Insert the fetched records into MongoDB
        if data.get('results'):
            collection.insert_many(data['results'])  # Insert all records at once

        # Check if we've fetched all records (compare the number of records with the total count)
        if len(list(collection.find())) >= data['count']:
            break

        # Update the offset for the next page (next 25 records)
        params['offset'] += params['limit']
    else:
        print(f"Failed to fetch submissions: {response.status_code}")
        print(response.text)
        break
#%%
# Initialize a Counter to keep track of the keys
key_counter = Counter()
#%%
# Initialize a defaultdict to store lists of record IDs
key_dict = defaultdict(list)
#%%
for record in collection.find():
    record_id = record.get('id', None)  # Default to 'N/A' if id is missing

    metadata_submission = record.get('metadata_submission', {})
    sampleData = metadata_submission.get('sampleData', {})
        # Check if sampleData is non-empty
    if len(sampleData) > 0:
        # Update the Counter with the keys of the current sampleData
        key_counter.update(sampleData.keys())

        # Update the dictionary with record_id for each sampleData key
        for key in sampleData.keys():
            key_dict[key].append(record_id)


#%%
key_counter
#%%
key_dict
#%%
# List to hold transformed documents
transformed_docs = []

# Iterate over the documents in the collection
for record in collection.find():
    submission_id = record.get('id', 'N/A')  # Get the submission ID (default to 'N/A' if missing)

    # Get the sampleData (assuming it contains lists of dictionaries)
    sample_data = record.get('metadata_submission', {}).get('sampleData', {})

    # Iterate over each key (list) in sampleData
    for key, rows in sample_data.items():
        # For each "row" in the list (which is a dictionary)
        for row in rows:
            # Create a new document for each row with the submission ID and key-value pairs
            transformed_doc = {
                "submission_id": submission_id,
                "key": key,
                "row_data": [{"field": field, "value": value} for field, value in row.items()]
            }
            # Append the transformed document to the list
            transformed_docs.append(transformed_doc)

#%%
biosample_row_collection = db["submission_biosample_rows"]  # Replace with your collection name
#%%
# Insert the documents into the collection
result = biosample_row_collection.insert_many(transformed_docs)
#%% md
# Where, in any column from any row in any template in any submission, does the value "YSISB-Stream Sediment" appear?
#%%
query = {
    "row_data": {
        "$elemMatch": {
            "value": "YSISB-Stream Sediment"
        }
    }
}
#%%
# Execute the query
results = biosample_row_collection.find(query)
#%%
# Print results
for doc in results:
    pprint.pprint(doc)
#%% md
# Now retrieve the submission with the id from that result
#%%
# Query to get the document with the given submission_id
query = {"id": "6128ea79-f122-4d14-8588-30f06ce3f1f6"}
#%%
# Initialize an empty list to hold all rows
all_rows = []
#%%
template = "sediment_data"
#%%
# Iterate through all documents in the collection
for document in collection.find(query):
    # Extract 'sediment_data' from 'metadata_submission.sampleData'
    template_data = document.get('metadata_submission', {}).get('sampleData', {}).get(template, [])

    for row in template_data:
        row['submission_id'] = document.get('id', None)  # Add document ID to the row
        row['template'] = template  # Add document ID to the row

    # Append the rows to the list
    all_rows.extend(template_data)
#%%
submissions_samples_frame = pd.DataFrame(all_rows)
#%%
submissions_samples_frame
#%%

import os

from dotenv import load_dotenv
from google.cloud import bigquery

# Load environment variables from local/.env
load_dotenv(os.path.join('..', 'local', '.env'))

GCP_PROJECT_NAME = os.environ.get('GCP_PROJECT_NAME')


# running this script requires installing system dependencies, python dependencies, authenticating and setting some default configurations

def list_public_datasets(project_id='bigquery-public-data'):
    client = bigquery.Client(project=GCP_PROJECT_NAME)
    datasets = list(client.list_datasets(project_id))

    if datasets:
        print(f"Datasets in project {project_id}:")
        for dataset in datasets:
            print(f"\t{dataset.dataset_id}")
    else:
        print(f"{project_id} project has no datasets.")


def search_datasets(search_term, project_id='bigquery-public-data'):
    client = bigquery.Client(project=GCP_PROJECT_NAME)
    datasets = list(client.list_datasets(project_id))

    matching_datasets = [dataset for dataset in datasets if search_term.lower() in dataset.dataset_id.lower()]

    if matching_datasets:
        print(f"Datasets matching '{search_term}' in project {project_id}:")
        for dataset in matching_datasets:
            print(f"\t{dataset.dataset_id}")
    else:
        print(f"No datasets matching '{search_term}' found in {project_id}.")


# List all public datasets
list_public_datasets()

# # Search for SRA and BioSample datasets
# search_terms = [
#     'biosample',
#     'ncbi',
#     'nih',
#     'sample',
#     'sequence',
#     'sra',
# ]
# for term in search_terms:
#     search_datasets(term)

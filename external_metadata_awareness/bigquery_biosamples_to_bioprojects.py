import os
from dotenv import load_dotenv
from google.cloud import bigquery

# Load environment variables but we'll override the project name
load_dotenv(os.path.join('..', 'local', '.env'))

# Important: We're using the known working project ID instead of getting it from env
GCP_PROJECT_NAME = "nmdc-377118"  # Override whatever might be in the .env file


def query_sra_relationships():
    """
    Query the SRA metadata store to find relationships between biosamples and bioprojects.
    """
    # Initialize the BigQuery client with our specific project
    client = bigquery.Client(project=GCP_PROJECT_NAME)

    # Define our query
    query = """
    SELECT
      DISTINCT biosample,
      bioproject
    FROM
      `nih-sra-datastore.sra.metadata`
    LIMIT 10;
    """

    try:
        print(f"Executing query using project: {GCP_PROJECT_NAME}")
        query_job = client.query(query)
        results = query_job.result()

        print("\nBiosample-Bioproject relationships:")
        print("-" * 50)
        for row in results:
            print(f"Biosample: {row.biosample} -> Bioproject: {row.bioproject}")

    except Exception as e:
        print(f"An error occurred while querying: {str(e)}")
        print(f"Current project: {GCP_PROJECT_NAME}")


if __name__ == "__main__":
    print("Starting SRA metadata query...")
    query_sra_relationships()

from google.cloud import bigquery
import csv
from datetime import datetime

# Important: We're using the known working project ID instead of getting it from env
GCP_PROJECT_NAME = "nmdc-377118"  # Override whatever might be in the .env file


def count_sra_relationships():
    """
    Query the SRA metadata store to count the total number of unique
    biosample-bioproject relationships. This gives us a sense of the
    dataset size before we try to retrieve all relationships.
    """
    client = bigquery.Client(project=GCP_PROJECT_NAME)

    # We use COUNT(DISTINCT) to get unique pairs since some biosamples
    # might be associated with multiple bioprojects or vice versa
    count_query = """
    SELECT COUNT(DISTINCT CONCAT(biosample, bioproject)) as relationship_count
    FROM `nih-sra-datastore.sra.metadata`
    """

    try:
        print("Counting unique biosample-bioproject relationships...")
        count_job = client.query(count_query)

        # The result will have just one row with one column
        count_result = next(iter(count_job.result()))
        total_count = count_result.relationship_count

        print(f"Found {total_count:,} unique relationships")
        return total_count

    except Exception as e:
        print(f"An error occurred while counting: {str(e)}")
        return None


def query_sra_relationships():
    """
    After getting the count, we can proceed with retrieving the actual relationships
    if the count seems reasonable.
    """
    total_count = count_sra_relationships()

    if total_count is None:
        return

    client = bigquery.Client(project=GCP_PROJECT_NAME)
    query = """
    SELECT
      DISTINCT biosample,
      bioproject
    FROM
      `nih-sra-datastore.sra.metadata`
    LIMIT 10;
    """

    try:
        print("\nRetrieving sample of relationships...")
        query_job = client.query(query)
        results = query_job.result()

        print("\nBiosample-Bioproject relationships (sample):")
        print("-" * 50)
        for row in results:
            print(f"Biosample: {row.biosample} -> Bioproject: {row.bioproject}")

    except Exception as e:
        print(f"An error occurred while querying: {str(e)}")


def export_sra_relationships(batch_size=100000):
    """
    Export biosample-bioproject relationships to a TSV file using batched processing.
    We use batching to handle the large dataset without consuming excessive memory.
    """
    client = bigquery.Client(project=GCP_PROJECT_NAME)

    # Create a timestamp-based filename to avoid overwriting previous exports
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'sra_relationships_{timestamp}.tsv'

    # Our query template for batch processing
    batch_query = """
    SELECT DISTINCT biosample, bioproject
    FROM `nih-sra-datastore.sra.metadata`
    ORDER BY biosample
    LIMIT @batch_size
    OFFSET @offset
    """

    try:
        # First, get total count to track progress
        count_query = """
        SELECT COUNT(DISTINCT CONCAT(biosample, bioproject)) as relationship_count
        FROM `nih-sra-datastore.sra.metadata`
        """
        count_job = client.query(count_query)
        total_count = next(iter(count_job.result())).relationship_count

        print(f"Beginning export of {total_count:,} relationships to {output_file}")

        # Open our output file and write the header
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerow(['biosample', 'bioproject'])

            # Process in batches
            offset = 0
            rows_processed = 0

            while offset < total_count:
                # Configure and run query for this batch
                job_config = bigquery.QueryJobConfig(
                    query_parameters=[
                        bigquery.ScalarQueryParameter("batch_size", "INT64", batch_size),
                        bigquery.ScalarQueryParameter("offset", "INT64", offset)
                    ]
                )

                query_job = client.query(batch_query, job_config=job_config)

                # Write this batch to our file
                batch_rows = 0
                for row in query_job.result():
                    writer.writerow([row.biosample, row.bioproject])
                    batch_rows += 1

                # Update our progress
                rows_processed += batch_rows
                offset += batch_size

                # Show progress
                progress = (rows_processed / total_count) * 100
                print(f"Progress: {progress:.1f}% ({rows_processed:,} / {total_count:,} relationships)")

                # If we got fewer rows than our batch size, we're done
                if batch_rows < batch_size:
                    break

        print(f"\nExport complete! File saved as: {output_file}")
        print(f"Total relationships exported: {rows_processed:,}")

    except Exception as e:
        print(f"An error occurred during export: {str(e)}")


if __name__ == "__main__":
    print("Starting SRA metadata analysis...")
    query_sra_relationships()
    export_sra_relationships()

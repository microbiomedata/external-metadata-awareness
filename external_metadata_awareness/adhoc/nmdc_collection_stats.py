import requests
import pandas as pd


def make_collection_stats_table():
    # Fetch the data from the API
    url = "https://api.microbiomedata.org/nmdcschema/collection_stats"
    tsv_out_filename = "nmdc_collection_stats.tsv"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return

    data = response.json()

    # Extract data into a pandas DataFrame
    records = []
    for item in data:
        # remove it initial "nmdc." from item["ns"]
        collection_name = item["ns"].replace("nmdc.", "")
        record = {"collection": collection_name}  # Start with the 'ns' field
        record.update(item["storageStats"])  # Add all the storageStats fields
        records.append(record)

    df = pd.DataFrame(records)

    # Display the table
    print(df)

    # Save to a CSV file
    df.to_csv(tsv_out_filename, index=False, sep="\t")
    print(f"Collection stats saved to '{tsv_out_filename}'")


if __name__ == "__main__":
    make_collection_stats_table()

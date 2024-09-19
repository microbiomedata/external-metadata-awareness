import duckdb
import requests


# Query NCBI using requests.get()
def get_ncbi_biosample_ids(query):
    params = {
        "db": "biosample",
        "term": query,
        "retmax": 999999,
        "retmode": "json"
    }
    response = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi", params=params)

    if response.status_code == 200:
        data = response.json()
        biosample_ids = data.get("esearchresult", {}).get("idlist", [])
        return biosample_ids
    else:
        raise Exception(f"Error retrieving data from NCBI (Status code: {response.status_code})")


# Query DuckDB
def get_duckdb_biosample_ids(duckdb_file):
    con = duckdb.connect(duckdb_file)
    query = """
    SELECT id
    FROM main.overview
    WHERE package_content = 'MIMS.me.water.6.0';
    """
    result = con.execute(query).fetchall()
    con.close()

    # Flatten the list of tuples into a list of IDs
    return [row[0] for row in result]


# # Get BioSample IDs from NCBI
# ncbi_query = '"mims me"[filter] AND "water"[filter]'
ncbi_query = '"mims me water 6 0"[filter]"'
ncbi_biosample_ids = get_ncbi_biosample_ids(ncbi_query)
print(len(ncbi_biosample_ids))

# Get BioSample IDs from DuckDB
duckdb_file = '../local/ncbi_biosamples.duckdb'
duckdb_biosample_ids = get_duckdb_biosample_ids(duckdb_file)
print(len(duckdb_biosample_ids))

# Trim and compare IDs
entrez_only = set(id.strip() for id in ncbi_biosample_ids) - set(str(id).strip() for id in duckdb_biosample_ids)
duckdb_only = set(str(id).strip() for id in duckdb_biosample_ids) - set(id.strip() for id in ncbi_biosample_ids)

# Convert the sets to lists to allow indexing
entrez_only_list = list(entrez_only)
entrez_only_list.sort()
duckdb_only_list = list(duckdb_only)
duckdb_only_list.sort()

# Print lengths and the first 10 elements (if they exist)
print(f"{len(entrez_only_list) = }")
print(entrez_only_list[:10])  # Slicing now works
print(f"{len(duckdb_only_list) = }")
print(duckdb_only_list[:10])

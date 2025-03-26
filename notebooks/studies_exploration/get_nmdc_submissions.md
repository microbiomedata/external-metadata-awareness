
# Summary of Code

This notebook connects to the **NMDC Data Submission API**, pulls metadata submission records, stores them in MongoDB, transforms and flattens the `sampleData` into a row-wise format, and stores those rows in a second MongoDB collection.

---

## Infrastructure Setup

### 1. Load environment variables
```python
env_vars = dotenv_values("../../local/.env")
REFRESH_TOKEN = env_vars['NMDC_DATA_SUBMISSION_REFRESH_TOKEN']
```

### 2. Connect to MongoDB
```python
client = MongoClient('mongodb://localhost:27017/')
db = client['misc_metadata']
collection = db['nmdc_submissions']
```

### 3. Authenticate and get access token
```python
POST https://data.microbiomedata.org/auth/refresh
Payload: {"refresh_token": REFRESH_TOKEN}
→ Returns: access_token
```

---

## Core Input

###  Input
- **API**: `https://data.microbiomedata.org/api/metadata_submission`
- **Authorization**: Bearer access_token
- **Query params**:
  - `column_sort`: `"created"`
  - `sort_order`: `"desc"`
  - `offset`: `0`
  - `limit`: `25`

### Pull data (paginated)
- All metadata submission records are downloaded using paginated `GET` requests.
- Stored in MongoDB collection: `misc_metadata.nmdc_submissions`

---

## Core Transformation

### Flatten `sampleData` rows from each submission into row-level documents:
```python
for record in collection.find():
    for key, rows in sample_data.items():
        for row in rows:
            transformed_docs.append({
                "submission_id": submission_id,
                "key": key,
                "row_data": [{"field": field, "value": value} for field, value in row.items()]
            })
```

### Output collection:
Flattened row-wise documents are stored in: `misc_metadata.submission_biosample_rows`

Each document looks like:
```json
{
  "submission_id": "...",
  "key": "sediment_data",
  "row_data": [
    {"field": "env_material", "value": "YSISB-Stream Sediment"},
    ...
  ]
}
```

---

## Example of Use

### Search for a specific value across all rows:
```python
query = {
    "row_data": {
        "$elemMatch": {
            "value": "YSISB-Stream Sediment"
        }
    }
}
results = biosample_row_collection.find(query)
```

### Get the full submission based on `submission_id` found:
```python
query = {"id": "6128ea79-f122-4d14-8588-30f06ce3f1f6"}
template = "sediment_data"
for document in collection.find(query):
    rows = document['metadata_submission']['sampleData'][template]
```

### Output: DataFrame of sample rows
The extracted rows are converted to a `pandas.DataFrame` named:
```python
submissions_samples_frame
```

---

## MongoDB Collections Created

| MongoDB Collection                         | Purpose                                                |
|--------------------------------------------|--------------------------------------------------------|
| `misc_metadata.nmdc_submissions`           | Stores raw NMDC metadata submission documents          |
| `misc_metadata.submission_biosample_rows`  | Stores flattened row-wise documents for sampleData     |

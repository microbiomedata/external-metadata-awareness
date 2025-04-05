from pymongo import MongoClient
from collections import defaultdict
import csv
from tqdm import tqdm

# 25 minutes for NCBI? use XYZ installed

# db_name = "gold_metadata"
# collection_name = "flattened_biosamples"

# db_name = "ncbi_metadata"
# collection_name = "biosamples_flattened"

db_name = "nmdc"
collection_name = "biosample_set"

tsv_out = "field_counts.tsv"

client = MongoClient()
db = client[db_name]
collection = db[collection_name]

sample_size = None  # Set to an int like 10000 for sampling

doc_count = collection.count_documents({})
# doc_count = collection.estimated_document_count()

# Step 1: Get all fields across documents
all_fields = set()
cursor = collection.find({}, projection=None, limit=sample_size or 0)
for doc in tqdm(cursor, total=doc_count, desc="Discovering fields"):
    for key, value in doc.items():
        if key != "_id":
            all_fields.add(key)

# Step 2: Count non-null/non-empty values
field_counts = defaultdict(int)
cursor = collection.find({}, projection=None, limit=sample_size or 0)
for doc in tqdm(cursor, total=doc_count, desc="Counting non-empty fields"):
    for field in all_fields:
        value = doc.get(field, None)
        if value is None:
            continue
        if isinstance(value, str) and value.strip() == "":
            continue
        if isinstance(value, list) and len(value) == 0:
            continue
        if isinstance(value, dict) and len(value) == 0:
            continue
        field_counts[field] += 1

# Step 3: Write to TSV
with open(tsv_out, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, delimiter="\t")
    writer.writerow(["field", "count"])
    for field, count in sorted(field_counts.items(), key=lambda x: x[1], reverse=True):
        writer.writerow([field, count])

print("✅ Field counts written to field_counts.tsv")

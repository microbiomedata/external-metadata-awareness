from pymongo import MongoClient
from tqdm import tqdm  # optional, for progress bar

client = MongoClient("mongodb://localhost:27017")
db = client["ncbi_metadata"]
source = db["biosamples"]
target = db["biosample_attributes"]

# ⚙️ Aggregation pipeline — same logic, no $out stage
pipeline = [
    {"$match": {"Attributes.Attribute": {"$exists": True, "$type": "array"}}},
    {"$unwind": "$Attributes.Attribute"},
    {"$project": {
        "_id": 0,
        "biosample_id": "$id",
        "accession": "$accession",
        "attribute_name": "$Attributes.Attribute.attribute_name",
        "harmonized_name": "$Attributes.Attribute.harmonized_name",
        "display_name": "$Attributes.Attribute.display_name",
        "unit": "$Attributes.Attribute.unit",
        "content": "$Attributes.Attribute.content"
    }},
    # Optional limit:
    # { "$limit": 100 }
]

# 🌀 Stream results with a cursor (efficient and observable)
cursor = source.aggregate(pipeline, allowDiskUse=True, batchSize=100)

# 🔁 Print or insert each record (tqdm tracks progress)
for doc in tqdm(cursor, desc="Processing attributes"):
    # print(doc)  # Or use logging
    target.insert_one(doc)  # Optionally write to new collection

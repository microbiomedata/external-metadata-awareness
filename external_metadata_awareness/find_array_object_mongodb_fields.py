from pymongo import MongoClient

client = MongoClient()  # Adjust as needed

db_name = "gold_metadata"
# collection_name = "biosamples"
collection_name = "flattened_biosamples"
db = client[db_name]
collection = db[collection_name]

pipeline = [
    {"$project": {
        "fieldTypes": {
            "$objectToArray": "$$ROOT"
        }
    }},
    {"$unwind": "$fieldTypes"},
    {"$group": {
        "_id": "$fieldTypes.k",
        "types": {"$addToSet": {"$type": "$fieldTypes.v"}}
    }},
    {"$match": {
        "types": {"$in": ["object", "array"]}
    }}
]

results = collection.aggregate(pipeline)
for doc in results:
    print(f"Field: {doc['_id']}, Types: {doc['types']}")

### GOLD biosamples
# Field: contacts, Types: ['array']
# Field: longhurst, Types: ['null', 'object']
# Field: envoBroadScale, Types: ['null', 'object']
# Field: envoLocalScale, Types: ['null', 'object']
# Field: envoMedium, Types: ['null', 'object']
# Field: hostDiseases, Types: ['array']

### GOLD flattened_biosamples all scalar
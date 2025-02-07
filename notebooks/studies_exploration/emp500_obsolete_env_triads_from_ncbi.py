#%%
import csv
import json
import pprint
import re
from collections import Counter

from oaklib import get_adapter
from oaklib.datamodels.vocabulary import IS_A
from pymongo import MongoClient

#%%
# For Ontology Access Kit (OAK)
envo_adapter_string = "sqlite:obo:envo"
#%%
BIOME = "ENVO:00000428"
ENV_MAT = "ENVO:00010483"
ABP = "ENVO:01000813"
#%%
# For the BBOP/NMDC MongoDB containing NCBI metadata

MONGO_USERNAME = None
MONGO_PASSWORD = None
MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_DATABASE = "ncbi_metadata"
BIOPROJECTS_COLLECTION = "bioprojects"
BIOSAMPLES_COLLECTION = "biosamples"
BIOSAMPLES_BIOPROJECTS_COLLECTION = "sra_biosamples_bioprojects"

#%%
if MONGO_USERNAME is not None and MONGO_PASSWORD is not None:
    # Replace these with your actual credentials and connection details.
    username = MONGO_USERNAME
    password = MONGO_PASSWORD
    host = MONGO_HOST
    port = MONGO_PORT

    # Build the connection string with authentication.
    connection_string = f"mongodb://{username}:{password}@{host}:{port}"
else:
    # Default connection to unauthenticated MongoDB.
    host = MONGO_HOST
    port = MONGO_PORT
    connection_string = f"mongodb://{host}:{port}"

# Create the client connection.
client = MongoClient(connection_string)
#%%
# --------------------------
# Select Database
# --------------------------

db = client[MONGO_DATABASE]  # Dynamically select database

#%%
bioprojects_collection = db[BIOPROJECTS_COLLECTION]
#%%
# --------------------------
# Search for NCBI BioProject records "about" EMP500
# --------------------------
# This query searches for the term "EMP500" using the $text operator,
# projects the text relevance score into the "score" field,
# and sorts the results by that relevance score.
cursor = bioprojects_collection.find(
    {"$text": {"$search": "EMP500"}},
    {"score": {"$meta": "textScore"}}
).sort([("score", {"$meta": "textScore"})])

#%%
emp500_candidate_bioprojects = []
#%%
# --------------------------
# Print the Results for Review
# --------------------------
for doc in cursor:
    pprint.pprint(doc)
    emp500_candidate_bioprojects.append(doc)
#%% md
# Use the BioProject with the ProjectDescr.Description.Title 'Earth Microbiome Project Multi-omics (EMP500)'
# 
# I.e. the zeroth element in the list `emp500_candidate_bioprojects`.
# 
# What's the accession?
#%%
emp500_bioproject_accession = emp500_candidate_bioprojects[0]['ProjectID']['ArchiveID']['accession']
#%%
print(emp500_bioproject_accession)
#%%
# Select the collection 'sra_biosamples_bioprojects'
sra_biosamples_bioprojects_collection = db[BIOSAMPLES_BIOPROJECTS_COLLECTION]

# Define the query to find documents with bioproject_accession equal to "PRJEB42019"
query = {"bioproject_accession": "PRJEB42019"}

# Execute the query
cursor = sra_biosamples_bioprojects_collection.find(query)

emp500_biosample_accessions = set()

# Iterate over the cursor and print each document
for doc in cursor:
    emp500_biosample_accessions.add(doc['biosample_accession'])

#%%
print(len(emp500_biosample_accessions))
#%%
biosamples_collection = db.biosamples  # Replace 'xxx' with your actual collection name

# Assuming emp500_biosample_accessions is a Python set containing 1024 values
# Use the $in operator to match documents where 'accession' is in your set.
query = {"accession": {"$in": list(emp500_biosample_accessions)}}

# Execute the query
cursor = biosamples_collection.find(query)

emp500_biosample_docs = []

# Iterate over the cursor and print each matching document
for doc in cursor:
    emp500_biosample_docs.append(doc)
#%%
print(len(emp500_biosample_docs))
#%%
# Define the target harmonized names
target_harmonized_names = {"env_broad_scale", "env_local_scale", "env_medium"}

# Extract relevant data
emp500_env_triad_rows = []  # Store the env triads themselves
env_content_counter = Counter()  # Store counts of all strings used as env triad values

for doc in emp500_biosample_docs:
    accession = doc.get("accession", "")
    package_content = doc.get("Package", {}).get("content", "")

    # Extract harmonized values
    env_values = {key: "" for key in target_harmonized_names}
    attributes = doc.get("Attributes", {}).get("Attribute", [])

    for attr in attributes:
        harmonized_name = attr.get("harmonized_name")
        content_value = attr.get("content", "")
        if harmonized_name in target_harmonized_names:
            env_values[harmonized_name] = content_value
            env_content_counter[content_value] += 1  # Count occurrences

    # Add extracted values to the list
    emp500_env_triad_rows.append({
        "accession": accession,
        "package": package_content,
        "env_broad_scale": env_values["env_broad_scale"],
        "env_local_scale": env_values["env_local_scale"],
        "env_medium": env_values["env_medium"]
    })

#%%
pprint.pprint(emp500_env_triad_rows[0:3])
#%% md
# The env triads consist of labels only, no CURIes
#%%
pprint.pprint(env_content_counter)
#%%
print(len(env_content_counter))
#%%
envo_adapter = get_adapter(envo_adapter_string)
#%%
biome_curies = list(envo_adapter.descendants(BIOME, predicates=[IS_A]))
env_mat_curies = list(envo_adapter.descendants(ENV_MAT, predicates=[IS_A]))
abp_curies = list(envo_adapter.descendants(ABP, predicates=[IS_A]))
#%%
non_biome_non_env_mat_abp_curies = set(abp_curies) - set(biome_curies) - set(env_mat_curies)
#%%
# use the OAK annotator to match the submitted env triad values to ENVO terms
# Don't panic about red error messages

# List to store all annotations
env_triad_terms_annotations_list = []

for content_value, count in env_content_counter.items():
    try:
        annotations = envo_adapter.annotate_text(content_value)
        for annotation in annotations:
            # Fetch the label for the object_id
            object_label = envo_adapter.label(annotation.object_id) if annotation.object_id else "Unknown"

            annotation_dict = {
                "content_value": content_value,
                "count": count,  # Frequency of this content value in the dataset
                "predicate_id": annotation.predicate_id,
                "object_id": annotation.object_id,
                "object_label": object_label,  # Looked up label
                "subject_start": annotation.subject_start,
                "subject_end": annotation.subject_end,
                "match_string": annotation.match_string,
                "matches_whole_text": annotation.matches_whole_text,
            }
            env_triad_terms_annotations_list.append(annotation_dict)

    except Exception as e:
        print(f"Error processing '{content_value}': {e}")

#%%
for annotation in env_triad_terms_annotations_list:
    annotation["match_string_len"] = len(annotation["match_string"]) if annotation["match_string"] else 0
#%%
# Pretty-print some sample results
for annotation in env_triad_terms_annotations_list[:10]:  # Show first 10 annotations
    pprint.pprint(annotation)
#%%
# Configurable match length cutoff
MATCH_LENGTH_CUTOFF = 3  # Exclude matches with length < 3 from needs_review_list

# Lists for categorization
perfect_match_list = []
needs_review_list = []
unmatched_content_values = set()  # Store content_values that are neither in perfect_match_list nor needs_review_list
non_perfect_match_content_values = set()  # Track all content_values that didn’t make it into perfect matches

# Identify content_values that have at least one perfect match with predicate_id='rdfs:label'
perfect_match_content_values = set()
all_annotated_content_values = set()  # Track all content_values that were annotated

for annotation in env_triad_terms_annotations_list:
    content_value = annotation["content_value"]
    all_annotated_content_values.add(content_value)

    if annotation["matches_whole_text"] and annotation["predicate_id"] == "rdfs:label":
        perfect_match_list.append(annotation)
        perfect_match_content_values.add(content_value)

# Identify content_values that have no perfect match and meet the length cutoff
needs_review_content_values = set()

for annotation in env_triad_terms_annotations_list:
    content_value = annotation["content_value"]
    annotation["match_string_len"] = len(annotation["match_string"]) if annotation["match_string"] else 0

    if (
            content_value not in perfect_match_content_values and
            annotation["match_string_len"] >= MATCH_LENGTH_CUTOFF
    ):
        needs_review_list.append(annotation)
        needs_review_content_values.add(content_value)

# Identify content_values that are in env_content_counter but not in perfect_match_list or needs_review_list
for content_value in env_content_counter.keys():
    if content_value not in perfect_match_content_values and content_value not in needs_review_content_values:
        unmatched_content_values.add(content_value)

#%%
obsoletes_curies_labelled = list()

obsoletes_curies_envo = set(envo_adapter.obsoletes())
for curie in obsoletes_curies_envo:
    temp_dict = dict()
    temp_dict["curie"] = curie
    temp_dict["label"] = envo_adapter.label(curie)
    obsoletes_curies_labelled.append(temp_dict)
#%%
# Helper function: Normalize text (lowercase + remove extra spaces)
def normalize_text(text):
    return re.sub(r'\s+', ' ', text).strip().lower()  # Replace multiple spaces & trim


# Create a lookup set of normalized obsolete labels
obsolete_label_set = {normalize_text(entry["label"]) for entry in obsoletes_curies_labelled}

# Prepare result storage
exact_obsolete_matches = []

# Check if "obsolete " + content_value exists in the obsolete labels
for content_value in needs_review_content_values | unmatched_content_values:  # Union of both sets
    obsolete_label_candidate = normalize_text(f"obsolete {content_value}")
    if obsolete_label_candidate in obsolete_label_set:
        # Find the corresponding CURIE using normalized comparison
        matching_entry = next(entry for entry in obsoletes_curies_labelled
                              if normalize_text(entry["label"]) == obsolete_label_candidate)
        exact_obsolete_matches.append({
            "content_value": content_value,  # ORIGINAL content_value
            "obsolete_label": matching_entry["label"],  # ORIGINAL obsolete label
            "obsolete_curie": matching_entry["curie"]
        })

#%%
pprint.pprint(exact_obsolete_matches)
#%%
obsolete_curies = {entry["obsolete_curie"] for entry in
                   exact_obsolete_matches}  # obsolete values that were used (indirectly)
# obsolete_curies = {entry["curie"] for entry in obsoletes_curies_labelled} # all obsolete values in EnvO

obsoletes_metadata_list = []

for curie in obsolete_curies:
    entity_metadata = envo_adapter.entity_metadata_map(curie)  # Fetch metadata
    if entity_metadata:
        obsoletes_metadata_list.append(entity_metadata)

#%%
pprint.pprint(obsoletes_metadata_list)
#%%
obsoletes_predicate_counter = Counter()

for metadata in obsoletes_metadata_list:
    if isinstance(metadata, dict):  # Ensure it's a dictionary
        obsoletes_predicate_counter.update(metadata.keys())

#%%
for key, count in obsoletes_predicate_counter.most_common():
    print(f"{key}: {count}")
#%%
# Compute high-level summary statistics
summary = {
    "total_unique_terms": len(env_content_counter),  # Unique terms submitted
    "perfect_matches": len(perfect_match_content_values),  # Unique perfect matches
    "matches_need_review": len(needs_review_content_values),  # Unique terms needing review
    "no_valid_oak_match": len(unmatched_content_values),  # Terms that didn't get a valid OAK annotation
    "exact_obsolete_matches": len(exact_obsolete_matches),  # Unique terms that exactly matched an obsolete label
    "obsolete_terms_with_replacement": sum(
        1 for m in obsoletes_metadata_list if "IAO:0100001" in m
    ),  # Obsolete terms with a clear replacement
    "obsolete_terms_with_consider": sum(
        1 for m in obsoletes_metadata_list if "oio:consider" in m
    ),  # Obsolete terms with "consider" alternatives
}

# Consistency check
if summary["perfect_matches"] + summary["matches_need_review"] + summary["no_valid_oak_match"] != summary[
    "total_unique_terms"]:
    print(
        f"WARNING: perfect_matches ({summary['perfect_matches']}) + matches_need_review ({summary['matches_need_review']}) "
        f"+ no_valid_oak_match ({summary['no_valid_oak_match']}) ≠ total_unique_terms ({summary['total_unique_terms']})"
    )

# Save to JSON
summary_json_file = "emp500_summary.json"
with open(summary_json_file, "w", encoding="utf-8") as json_file:
    json.dump(summary, json_file, indent=4)

print(f"Summary saved to {summary_json_file}")

#%%
import csv

# Save Detailed Term Legitimacy Report
detailed_tsv = "emp500_term_legitimacy.tsv"

with open(detailed_tsv, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, delimiter="\t", fieldnames=[
        "content_value", "emp500_usages", "perfect_match", "matched_label", "matched_curie",
        "is_obsolete", "obsolete_label", "obsolete_curie", "replacement_curie", "replacement_label",
        "consider_replacements"
    ])
    writer.writeheader()

    for content_value, emp500_usages in env_content_counter.items():
        # Determine perfect match status
        is_perfect_match = content_value in perfect_match_content_values

        # Get matched_label and matched_curie from perfect_match_list
        perfect_match_entry = next(
            (entry for entry in perfect_match_list if entry["content_value"] == content_value),
            None
        )
        matched_label = perfect_match_entry["object_label"] if perfect_match_entry else ""
        matched_curie = perfect_match_entry["object_id"] if perfect_match_entry else ""

        # Determine obsolete status
        obsolete_entry = next((e for e in exact_obsolete_matches if e["content_value"] == content_value), None)
        is_obsolete = bool(obsolete_entry)
        obsolete_label = obsolete_entry["obsolete_label"] if obsolete_entry else ""
        obsolete_curie = ""

        # Get obsolete CURIE from obsoletes_curies_labelled
        if obsolete_entry:
            obsolete_curie_entry = next(
                (o for o in obsoletes_curies_labelled if obsolete_label in o["label"]),
                None
            )
            obsolete_curie = obsolete_curie_entry["curie"] if obsolete_curie_entry else ""

        # Determine replacement term (IAO:0100001)
        replacement_curie = ""
        replacement_label = ""
        consider_replacements = ""

        if obsolete_curie:
            metadata = next((m for m in obsoletes_metadata_list if "id" in m and obsolete_curie in m["id"]), None)

            # Process replacement_curie
            if metadata and "IAO:0100001" in metadata:
                replacement_curie = metadata["IAO:0100001"][0]  # Extract replacement CURIE
                replacement_label = envo_adapter.label(replacement_curie) if replacement_curie else ""

            # Process oio:consider replacements
            if metadata and "oio:consider" in metadata:
                consider_list = metadata["oio:consider"]
                consider_replacements = " | ".join(
                    f"{curie}/{envo_adapter.label(curie)}" for curie in consider_list
                )

        writer.writerow({
            "content_value": content_value,
            "emp500_usages": emp500_usages,
            "perfect_match": is_perfect_match,
            "matched_label": matched_label,
            "matched_curie": matched_curie,
            "is_obsolete": is_obsolete,
            "obsolete_label": obsolete_label,
            "obsolete_curie": obsolete_curie,
            "replacement_curie": replacement_curie,
            "replacement_label": replacement_label,
            "consider_replacements": consider_replacements
        })

print(f"Term Legitimacy Report saved to {detailed_tsv}")

#%%
import csv

# Step 1: Extract `content_value` entries from `emp500_term_legitimacy.tsv` where `is_obsolete` is True
obsolete_content_values = set()

with open("emp500_term_legitimacy.tsv", mode="r", encoding="utf-8") as file:
    reader = csv.DictReader(file, delimiter="\t")
    for row in reader:
        if row["is_obsolete"].lower() == "true":  # Convert string to boolean
            obsolete_content_values.add(row["content_value"])

# Step 2: Create a filtered version of `needs_review_list` without modifying the original
filtered_needs_review_entries = [
    {**entry, "emp500_usages": entry.pop("count", 0)}  # ✅ Rename "count" to "emp500_usages"
    for entry in needs_review_list if entry["content_value"] not in obsolete_content_values
]

# Step 3: Prepare `unmatched_content_values` for inclusion
# ✅ Ensure unmatched terms do not include obsolete terms
filtered_unmatched_content_values = unmatched_content_values - obsolete_content_values

unmatched_rows = [
    {"content_value": content_value, "emp500_usages": env_content_counter.get(content_value, 0)}
    for content_value in filtered_unmatched_content_values
]

# Step 4: Save Needs Review to TSV
needs_review_tsv = "emp500_needs_review.tsv"

# Define fieldnames based on actual expected columns
fieldnames = [
    "content_value", "emp500_usages", "predicate_id", "object_id", "object_label",
    "subject_start", "subject_end", "match_string", "match_string_len", "matches_whole_text"
]

with open(needs_review_tsv, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, delimiter="\t", fieldnames=fieldnames)

    writer.writeheader()

    # Write filtered needs review entries
    for entry in filtered_needs_review_entries:
        row = {key: entry.get(key, "") for key in fieldnames}
        writer.writerow(row)

    # Write unmatched content values (only relevant fields)
    for row in unmatched_rows:
        row_filled = {key: row.get(key, "") for key in fieldnames}  # Ensure matching format
        writer.writerow(row_filled)

print(f"✅ Needs Review TSV saved to {needs_review_tsv} (Filtered & ensures obsolete terms do NOT reappear)")

#%%

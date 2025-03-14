#!/usr/bin/env python
# coding: utf-8

# In[1]:


import re
import urllib.parse
from collections import Counter

import pandas as pd
import requests
import requests_cache
import yaml
from curies import Converter
from dotenv import dotenv_values
from oaklib import get_adapter
from oaklib.interfaces.text_annotator_interface import TextAnnotatorInterface
from oaklib.utilities.lexical.lexical_indexer import load_lexical_index
from prefixmaps.io.parser import load_converter
from pymongo import MongoClient, ASCENDING, errors
from pymongo.errors import DuplicateKeyError
from tqdm.notebook import tqdm


# when should no results be saved as an empty record in mongodb, and when should the field be omitted?

# In[2]:


envo_adapter_string = 'sqlite:obo:envo'
po_adapter_string = 'sqlite:obo:po'

# consider using an aggregated adapter
# that may not work with saving a YAML cache/index


# In[3]:


mongo_url = "mongodb://localhost:27017"


# In[4]:


requests_cache_name = "requests_cache"


# In[5]:


requests_cache_expire_after = 604800


# In[6]:


# Define threshold
COMPONENT_COUNT_THRESHOLD = 2
# COMPONENT_COUNT_THRESHOLD = 100
MIN_LABEL_LEN = 3

# # Database collection
# triad_components_labels_collection = db["triad_components_labels"]

# OLS Search API URL
OLS_SEARCH_URL = "https://www.ebi.ac.uk/ols/api/search"

# Ontologies to search

small_high_impact_targets_lc = [
    "envo", # db 19 MB, 7 030 classes
    "po", # db 24 MB
]
other_targets_lc = [
    "chebi", # db ~ 3 700 MB, 220 816 classes
    "doid", # 18 897 classes
    "dron", # 747 494 classes
    "efo", # db 779 MB
    "foodon", # db 280 MB
    "gaz", # 668 838 classes
    "mmo", # db 4 MB
    "ncbitaxon", # 736 927 classes
    "ohmi", # db 13 MB
    "opl", # 561 classes
    "pato", # db 151 MB
    "pco", # db 2 MB
    "po", # db 24 MB
    "uberon" # db 995 MB
]
# obi? agro?
# map from sources: bto, ncit, omit, agro, snomedct, dron
OLS_LABEL_SEARCH_ONTS = "chebi,doid,dron,efo,envo,foodon,gaz,mmo,ncbitaxon,ohmi,opl,pato,pco,po,uberon"

FIELDLIST = "ontology_name,is_defining_ontology,obo_id,label,synonym"

QUERYFIELDS = "label,synonym"

OLS_REQ_EXACT_MATCH = "true"


# In[7]:


# Specify the path to your .env file
env_path = "../../../local/.env"
bioportal_api_key_name = "BIOPORTAL_API_KEY"


# In[8]:


# Enable request caching
requests_cache.install_cache(requests_cache_name, expire_after=requests_cache_expire_after)  # Cache expires after 7 days


# In[9]:


# Connect to local MongoDB on default port
client = MongoClient(mongo_url)


# In[10]:


# Access the database and the collections
# use the connection builder from core.py>
db = client.ncbi_metadata


# In[11]:


triad_values_collection = db.unique_triad_values


# In[12]:


triad_components_labels_collection = db.triad_components_labels


# In[13]:


envo_adapter = get_adapter(envo_adapter_string)
po_adapter = get_adapter(po_adapter_string)


# In[14]:


# Estimate document count for tqdm
doc_count = triad_components_labels_collection.estimated_document_count()


# OAK annotate does not return any knowledge about the matching entity, like its label, synonyms, obsolete status, etc.
# 
# This search only annotates a small fraction of the component_labels, ~ 6%
# 
# TODO: add a lower case indicator of the object ontology

# In[15]:


# Process each document
# Initialize tqdm with manual updating
with tqdm(total=doc_count, desc="Processing documents") as pbar:
    for doc in triad_components_labels_collection.find():
        # todo skip excel formula_like values?
        component_label = doc.get("component_label")

        if not component_label:
            pbar.update(1)
            continue  # Skip if component_label is missing or empty

        # Collect annotations from both adapters
        envo_annotations = list(envo_adapter.annotate_text(component_label.lower()))
        po_annotations = list(po_adapter.annotate_text(component_label.lower()))

        # Use a set to track unique, whole-text keepers
        unique_keepers = set()

        keepers = []
        for annotation in envo_annotations + po_annotations:  # Combine both sources
            # todo skip if the predicate isn't rdfs:label, or oio:hasExactSynonym
            #   also seeing oio:hasRelatedSynonym, oio:hasNarrowSynonym and oio:hasBroadSynonym
            if annotation.matches_whole_text:
                keeper_tuple = (annotation.predicate_id, annotation.object_id)
                if keeper_tuple not in unique_keepers:
                    unique_keepers.add(keeper_tuple)
                    keepers.append({
                        "predicate_id": annotation.predicate_id,
                        "curie": annotation.object_id,
                    })

        if keepers:
            triad_components_labels_collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {"oak_text_annotations": keepers}}
            )

        pbar.update(1)

# progress bar updates in spurts, possibly due to 100-document cursor size
# there's a lag of ~ 15 seconds from building the lexical indices
# 3 minutes


# In[16]:


print(f"Estimated doc count: {doc_count}")


# In[17]:


has_matches = triad_components_labels_collection.count_documents({"oak_text_annotations": {"$exists": True}})


# In[18]:


print(f"Documents with 'matches' field: {has_matches}")


# In[19]:


needs_followup = triad_components_labels_collection.count_documents({"matches": {"$exists": False}, "count": {"$gt": 1}})


# In[20]:


print(f"Documents used at least twice, with no 'matches' field: {needs_followup}")


# In[21]:


# index!


# In[22]:


result = triad_components_labels_collection.aggregate([
    {"$project": {"count": 1}},  # Only keep the 'count' field
    {"$sort": {"count": -1}},  # Sort by 'count' in descending order
    {"$limit": 1}  # Get the document with the highest count
])


# In[23]:


highest_count = next(result, None)  # Fetch the result safely


# In[24]:


highest_count


# In[25]:


COMPONENT_COUNT_THRESHOLD


# In[26]:


docs = list(
    triad_components_labels_collection.find(
        {"count": {"$gte": COMPONENT_COUNT_THRESHOLD}, "oak_text_annotations": {"$exists": False}},  # Filter criteria
        {"component_label": 1}  # Projection (only fetch 'component_label')
    )
)


# In[27]:


# todo: is this indexed yet?


# It doesn't look like the OLS text search can tell us if a term is obsolete
# 
# https://www.ebi.ac.uk/ols4/api/search?q=pyrene+degrading+sulfate+reducing+enrichment+cultutre+obtained+using+a+freshwater+lake+sediment
# 
# https://www.ebi.ac.uk/ols4/ols3help
# 
# This gets even fewer annotations than the initial OAK phase

# In[28]:


# Iterate over documents with tqdm for progress tracking
for doc in tqdm(docs, desc="Processing components", unit="doc"):
    query = doc.get("component_label", "").strip().lower()
    # print(query)
    if len(query) < MIN_LABEL_LEN:
        continue  # Skip short labels

    start = 0  # Start pagination at 0
    rows = 1000  # Max per request (set to 100 for efficiency)
    ols_hits = []  # Store matching results

    while True:
        params = {
            "q": query,
            "exact": OLS_REQ_EXACT_MATCH,
            "fieldList": FIELDLIST,
            "ontology": OLS_LABEL_SEARCH_ONTS,
            "queryFields": QUERYFIELDS,
            "rows": rows,
            "start": start,
        }

        # # Create a Request object
        # req = requests.Request('GET', OLS_SEARCH_URL, params=params)
        #
        # # Prepare it
        # prepared_req = req.prepare()
        #
        # # Now you can see the URL
        # print(prepared_req.url)

        response = requests.get(OLS_SEARCH_URL, params=params)
        response.raise_for_status()
        data = response.json()

        # Extract results
        results = data.get("response", {}).get("docs", [])

        # If no results, break loop
        if not results:
            break

        # Process results
        for result in results:
            # pprint.pprint(result)
            if result.get("is_defining_ontology", False):
                label_lower = result.get("label", "").lower()
                label_lower_match = label_lower == query

                temp_dict = {
                    "exact_label_match": label_lower_match,
                    "label": result.get("label", ""),
                    "synonyms": result.get("synonym", []),
                    "obo_id": result.get("obo_id", ""),
                    "ontology_lc": result.get("ontology_name", "").lower(),
                }
                if OLS_REQ_EXACT_MATCH == "true":
                    temp_dict['exact_something_match'] = True

                ols_hits.append(temp_dict)

        # Check if we need to fetch more results
        num_found = data.get("response", {}).get("numFound", 0)
        start += rows  # Move to the next page

        if start >= num_found:  # Stop if we've retrieved all records
            break

    # Update the document with OLS hits if any
    if ols_hits:
        triad_components_labels_collection.update_one({"_id": doc["_id"]}, {"$set": {"ols_text_annotation": ols_hits}})

# 1.8 docs per second
# OLS_LABEL_SEARCH_ONTS = "envo,ncit,ncbitaxon,uberon,snomed,foodon,micro,genepio,po,obi,ohmi,agro,pco,exo,mco,pato"
# FIELDLIST = "ontology_name,is_defining_ontology,obo_id,label,synonym"
# QUERYFIELDS = "label,synonym"
# "exact": "true",
# exact false brings it down to 1 docs/6 seconds, like bioportal (via OAK)?


# In[29]:


target_collection = db["class_label_cache"]
target_collection.drop()


# In[30]:


target_collection = db["class_label_cache"]


# In[31]:


# Ensure unique index on 'curie' to enforce "first one wins"
target_collection.create_index([("curie", ASCENDING)], unique=True)


# In[32]:


# triad_components_labels_collection
# triad_values_collection = db.unique_triad_values
# triad_components_labels_collection = db.triad_components_labels


# start collecting a cache of curies with their labels and synonyms
# 
# start with ols_text_annotations
# 
# inconsistently including obsolete flag?

# In[33]:


# Iterate through source collection
for doc in triad_components_labels_collection.find({}):
    hits = doc.get("ols_text_annotation", [])  # Get list or empty list
    for hit in hits:
        curie = hit.get("obo_id")
        label = hit.get("label")
        synonyms = hit.get("synonyms", [])

        try:
            target_collection.insert_one({
                "curie": curie,
                "label": label,
                "synonyms": synonyms,
            })

        except DuplicateKeyError:
            # Ignore duplicates and continue
            pass


# start keeping track  of unlabelled curies anywhere in the database, as an in-memory set

# In[34]:


unlabelleds = set()


# In[35]:


# is this indexed yet?


# include oak_text_annotations in unlabeleds because the OAK text annotator does not return the matched term's label, only information about which of its annotations was matched (label, synonym, etc)

# In[36]:


for doc in triad_components_labels_collection.find({}, {"oak_text_annotations.curie": 1}):
    annotations = doc.get("oak_text_annotations", [])  # Get list or empty list
    if isinstance(annotations, list):
        for annotation in annotations:
            curie = annotation.get("curie")
            if curie:
                unlabelleds.add(curie)


# In[37]:


len(unlabelleds)


# now add asserted curies discovered during parsing, if their prefix suggest that the term is present in Bioportal

# In[38]:


# Iterate through source collection and insert CURIes from parsed_annotations[].repaired_curie
for doc in triad_values_collection.find({},
                                        {"parsed_annotations.repaired_curie": 1, "parsed_annotations.bioportal_prefix": 1}):
    annotations = doc.get("parsed_annotations", [])  # Get list or empty list
    if isinstance(annotations, list):
        for annotation in annotations:
            curie = annotation.get("repaired_curie")
            bioportal_prefix = annotation.get("bioportal_prefix")

            if curie and bioportal_prefix:  # Exclude if obo_prefix is present
                unlabelleds.add(curie)  # Add to set (ensures uniqueness)



# In[39]:


len(unlabelleds)


# In[40]:


labelleds = []
still_unlabelled_envo = []
still_unlabelled_other = []


# TODO: add obsolete indicator

# In[41]:


def attempt_oak_labelling(unlabelled, adapter, labelleds):
    label = adapter.label(unlabelled)
    if label:
        aliases = adapter.entity_aliases(unlabelled) or []
        if not isinstance(aliases, list):
            print(aliases)
        aliases = [i for i in aliases if i != label]
        labelleds.append({"curie": unlabelled, "label": label, "synonyms": aliases})
        return True  # Indicates that labeling was successful
    return False  # Indicates that the CURIE remains unlabelled


# now try to find labels for the items in the unlabelled set with the EnvO or PO OAK annotators
# 
# if no label is found, then add the curie to either an unlabelled EnvO term list (which is probably all bogus curies)
# 
# or an unlabelled other list, which likely contains a lot or valid curies from other namespaces

# In[42]:


for unlabelled in unlabelleds:
    labelled = attempt_oak_labelling(unlabelled, envo_adapter, labelleds)
    labelled |= attempt_oak_labelling(unlabelled, po_adapter, labelleds)  # |= ensures labelled stays True if either succeeds

    if not labelled:  # Only add to unlabelled lists if neither adapter provided a label
        if "envo" in unlabelled.lower():
            still_unlabelled_envo.append(unlabelled)
        else:
            still_unlabelled_other.append(unlabelled)

# 10 seconds


# In[43]:


len(labelleds)


# In[44]:


if labelleds:  # Ensure the list is not empty
    try:
        target_collection.insert_many(labelleds, ordered=False)  # Bulk insert, ignore order
    except errors.BulkWriteError as e:
        pass # todo


# In[45]:


# todo: index


# In[46]:


len(still_unlabelled_envo)


# In[47]:


len(still_unlabelled_other)


# In[48]:


# Function to get the label etc from BioPortal safely, using a term URI and prefix as input
def get_bioportal_info(uri, prefix, BIOPORTAL_API_KEY):
    temp_dict = {
        "label": None,
        "obsolete": None,
        "synonyms": None,
        "status": None
    }
    if not isinstance(uri, str) or not uri.startswith(("http://", "https://")):
        temp_dict["status"] = "non-string URI"
        return temp_dict  # todo better handling/reporting

    if not isinstance(prefix, str):
        temp_dict["status"] = "non-string ontology slug"
        return temp_dict  # todo better handling/reporting

    # Upper-case the ontology prefix
    ontology = prefix.upper()

    # URL-encode the inferred URI
    encoded_uri = urllib.parse.quote(uri, safe="")

    # Correct API request URL format
    url = f"https://data.bioontology.org/ontologies/{ontology}/classes/{encoded_uri}?apikey={BIOPORTAL_API_KEY}"

    try:
        response = requests.get(url, headers={"Authorization": f"apikey {BIOPORTAL_API_KEY}"})

        if response.status_code == 200:
            data = response.json()
            pref_label = data.get("prefLabel", "")
            obsolete = data.get("obsolete", False)  # Default to False if missing
            if not obsolete:
                obsolete = False
            synonyms = data.get("synonym", [])  # Default to False if missing

            # todo GET MAPPINGS

            if not synonyms:
                synonyms = []

            links = data.get("links", {})  # Default to False if missing
            mappings_link = links.get("mappings", {})

            temp_dict = {
                "label": pref_label,
                "obsolete": obsolete,
                "synonyms": synonyms,
                "status": "success",
                "ontology_lc": prefix.lower(),
                "mappings_link": mappings_link
            }

            return temp_dict
        else:
            temp_dict["status"] = f"response: {response.status_code}"
            return temp_dict  # todo better handling/reporting
    except Exception as e:
        temp_dict["status"] = f"exception: {e}"
        return temp_dict  # todo better handling/reporting


# In[49]:


# Function to safely expand CURIEs, ignoring invalid ones
def safe_expand(curie):
    if isinstance(curie, str) and ":" in curie:  # Ensure it's a CURIE
        return converter.expand(curie.upper())
    return None  # Return None for invalid CURIEs


# using the Bioportal API requires an API key

# In[50]:


# Load variables into a dictionary
env_vars = dotenv_values(env_path)
BIOPORTAL_API_KEY = env_vars[bioportal_api_key_name]


# create a CURIe/URI converted prioritizing Bioportal style

# In[51]:


converter: Converter = load_converter(["bioportal", "obo"])


# try to get the label, synonyms, etc. for the unlabeled other asserted curies from Bioportal

# In[52]:


for curie in tqdm(still_unlabelled_other, desc="Processing CURIEs"):

    # split the curie into the prefix and the local_id
    onto_slug = curie.split(":")[0].upper()
    term_uri = safe_expand(curie)
    term_info = get_bioportal_info(term_uri, onto_slug, BIOPORTAL_API_KEY)
    term_info['curie'] = curie

    if term_info["status"] == "success":
        del term_info["status"]
        try:
            # Attempt to insert into MongoDB
            target_collection.insert_one(term_info)

        except DuplicateKeyError:
            pass  # todo better handling/reporting

        except Exception as e:
            pass  # todo better handling/reporting

# 50 minutes
# retrieved 3768 from 4519


# In[53]:


preferred_ontologies = set(small_high_impact_targets_lc) | set(other_targets_lc)


# In[54]:


preferred_ontologies


# Fetch documents where mappings_link exists and ontology_lc is in preferred ontologies

# In[55]:


docs = list(target_collection.find(
    {
        "mappings_link": {"$exists": True, "$ne": None},
        "ontology_lc": {"$nin": list(preferred_ontologies)}  # Ensure lowercase matching
    }
))
# .limit(100))


# In[56]:


# Function to fetch mappings from BioPortal
def fetch_mappings(mappings_url):
    """Fetch mappings from BioPortal using mappings_link."""
    try:

        # Properly append the API key based on the existing URL structure
        if "?" in mappings_url:
            mappings_url += f"&apikey={BIOPORTAL_API_KEY}"
        else:
            mappings_url += f"?apikey={BIOPORTAL_API_KEY}"

        response = requests.get(mappings_url, timeout=10)
        response.raise_for_status()
        mappings_obj = response.json()

        mappings_list = []
        for item in mappings_obj:
            if item.get("source") == "LOOM":
                for cls in item.get("classes", []):
                    # ontology_slug = cls["links"]["ontology"].split("/")[-1].lower()
                    #
                    # # Only store CURIE if mapped ontology is in the preferred list
                    # if ontology_slug in preferred_ontologies:
                    curie = converter.compress(cls["@id"])
                    if curie:
                        curie_prefix = curie.split(":")[0].lower()
                        if curie_prefix and curie_prefix in preferred_ontologies:  # Ensure CURIE conversion was successful
                            mappings_list.append(curie)

        return set(mappings_list)  # Return list of valid CURIE mappings

    except requests.RequestException as e:
        print(f"Failed to fetch mappings from {mappings_url}: {e}")
        return []


# Fetch mappings from asserted CURIes to CURIes from preferred ontologies

# In[57]:


# Iterate through docs and fetch mappings where needed
for doc in docs:
    if doc.get("mappings_link"):
        temp_mappings = fetch_mappings(doc["mappings_link"])
        # print(f"from {doc['curie']}/{doc['label']} to {temp_mappings}")
        if temp_mappings:
            target_collection.update_one({"_id": doc["_id"]},
                                         {"$set": {"preferred_mappings_curies": list(temp_mappings)}})  # Update in DB

# 45 minutes without cache
# todo add tqdm
# 7 seconds with cache


# start to find the curies, from mapping asserted curies into preferred ontologies, that don't already have labels in the `target_collection` "class_label_cache"

# In[58]:


# Create a set of lowercase curies from the class_label_cache collection (where label exists)
labelled_curies_set = {
    doc["curie"].lower() for doc in target_collection.find(
        {"label": {"$exists": True, "$ne": ""}}, {"curie": 1}
    ) if "curie" in doc
}


# In[59]:


len(labelled_curies_set)


# In[60]:


# Create a set of lowercase curies from the "preferred_mappings_curies" field
preferred_mappings_curies_set = {
    curie.lower() for doc in target_collection.find(
        {"preferred_mappings_curies": {"$exists": True, "$ne": []}}, {"preferred_mappings_curies": 1}
    ) for curie in doc["preferred_mappings_curies"]
}


# In[61]:


len(preferred_mappings_curies_set)


# In[62]:


# Find values in preferred_mappings_curies that are NOT in curies_set
# todo are we redefining unlabelleds here?
unlabelleds = preferred_mappings_curies_set - labelled_curies_set


# In[63]:


len(unlabelleds)


# Use the Bioportal API to get the label, synonyms, etc for the unlabelled CURIes mapped from the asserted curies
# 
# Previous experience shows that these are almost all NON EnvO UCRIes

# In[64]:


# almost 100% duplicated code
for curie in tqdm(unlabelleds, desc="Processing CURIEs"):

    # split the curie into the prefix and the local_id
    onto_slug = curie.split(":")[0].upper()
    term_uri = safe_expand(curie)
    term_info = get_bioportal_info(term_uri, onto_slug, BIOPORTAL_API_KEY)
    term_info['curie'] = converter.compress(term_uri)

    if term_info["status"] == "success":
        del term_info["status"]
        try:
            # Attempt to insert into MongoDB
            target_collection.insert_one(term_info)

        except DuplicateKeyError:
            pass  # todo better handling/reporting

        except Exception as e:
            pass  # todo better handling/reporting


# now create an oak lexical index from classes with precedent and do a non-whole word match

# In[65]:


# Normalize text: lowercase and remove excess whitespace
# todo this probably duplicates some other previous function
def normalize(text):
    return re.sub(r'\s+', ' ', text.strip().lower())


# In[66]:


# Initialize index structure
lexical_index = {
    "groupings": {},
    "pipelines": {
        "default": {
            "name": "default",
            "transformations": [
                {"type": "CaseNormalization"},
                {"type": "WhitespaceNormalization"}
            ]
        }
    }
}


# Populate the lexical_index dict's groupings with label, synonyms in `target_collection` "class_label_cache"
# 
# TODO would ideally instantiate the index directly instead of treating it as a dict and yaml file first

# In[67]:


# Process each document in MongoDB
for doc in target_collection.find():
    curie = doc["curie"]
    label = normalize(doc["label"])
    synonyms = [normalize(s) for s in doc.get("synonyms", [])]

    # Ensure label is in the groupings
    if label not in lexical_index["groupings"]:
        lexical_index["groupings"][label] = {
            "term": label,
            "relationships": []
        }

    # Add label relationship
    lexical_index["groupings"][label]["relationships"].append({
        "predicate": "rdfs:label",
        "element": curie,
        "element_term": label,
        "pipeline": ["default"],
        "synonymized": False
    })

    # Process synonyms
    for synonym in synonyms:
        if synonym not in lexical_index["groupings"]:
            lexical_index["groupings"][synonym] = {
                "term": synonym,
                "relationships": []
            }

        lexical_index["groupings"][synonym]["relationships"].append({
            "predicate": "oio:hasRelatedSynonym",
            "element": curie,
            "element_term": synonym,
            "pipeline": ["default"],
            "synonymized": False
        })


# In[68]:


# todo would ideally instantiate the index directly instead of treating it as a dict and yaml file first
biosamples_env_triads_precedent_lexical_index_yaml = "biosamples_env_triads_precedent_lexical_index.yaml"


# In[69]:


biosamples_env_triads_precedent_lexical_filtered_index_yaml = "biosamples_env_triads_precedent_lexical_filtered_index.yaml"


# save the initial lexical index based on the documents in the `target_collection` "class_label_cache"

# In[105]:


with open(biosamples_env_triads_precedent_lexical_filtered_index_yaml, "w") as f:
    yaml.dump(lexical_index, f, default_flow_style=False, sort_keys=True)
# 15 seconds


# create an initial lexical index object
# biosamples_env_triads_precedent_lexical_index = load_lexical_index(biosamples_env_triads_precedent_lexical_index_yaml)
# # 20 seconds

# In[106]:


biosamples_env_triads_precedent_lexical_index = load_lexical_index(biosamples_env_triads_precedent_lexical_index_yaml)
# 20 seconds


# create an initial TextAnnotatorInterface

# In[107]:


# Initialize the TextAnnotatorInterface
biosamples_env_triads_precedent_interface = TextAnnotatorInterface()
biosamples_env_triads_precedent_interface.lexical_index = biosamples_env_triads_precedent_lexical_index


# In[108]:


def optimize_annotations(annotations, preferred_ontologies, min_length=3, text=""):
    """
    Selects the minimal set of annotations that maximizes coverage of input text.
    Returns the optimized annotations, uncovered text segments, and percent coverage.
    """
    # Sort by longest span first (descending order)
    annotations.sort(key=lambda a: (a.subject_end - a.subject_start), reverse=True)

    selected_annotations = []
    covered_intervals = []

    for a in annotations:
        prefix_of_mapped = a.object_id.split(":")[0].lower()
        annotation_length = a.subject_end - a.subject_start

        if prefix_of_mapped in preferred_ontologies and annotation_length >= min_length:
            # Check if this annotation overlaps with already selected ones
            overlap = any(start < a.subject_end and a.subject_start < end for start, end in covered_intervals)
            if not overlap:
                annotation_dict = {k: v for k, v in vars(a).items() if v}
                selected_annotations.append(annotation_dict)
                covered_intervals.append((a.subject_start, a.subject_end))

    # SIMPLIFIED APPROACH: Ignore single-character uncovered segments for coverage calculation
    uncovered_text = []

    # Create a set of covered positions
    covered_positions = set()
    for start, end in covered_intervals:
        covered_positions.update(range(start, end))

    # Find uncovered non-whitespace positions and ignore isolated characters
    non_whitespace_positions = set()
    for i, char in enumerate(text):
        if char.strip():  # Non-whitespace character
            non_whitespace_positions.add(i)

    uncovered_positions = non_whitespace_positions - covered_positions

    # Only consider segments of two or more consecutive characters as "uncovered"
    # (This ignores isolated characters like the "h", "a", "h" in your example)
    if uncovered_positions:
        sorted_positions = sorted(uncovered_positions)
        current_segment = [sorted_positions[0]]

        for pos in sorted_positions[1:]:
            if pos == current_segment[-1] + 1:
                current_segment.append(pos)
            else:
                # Only add segments with length >= 2
                if len(current_segment) >= 2:
                    segment_text = ''.join(text[i] for i in current_segment)
                    uncovered_text.append(segment_text)
                current_segment = [pos]

        # Don't forget the last segment
        if current_segment and len(current_segment) >= 2:
            segment_text = ''.join(text[i] for i in current_segment)
            uncovered_text.append(segment_text)

    # Adjust coverage calculation to ignore single character "gaps"
    single_char_positions = set()
    for pos in uncovered_positions:
        # Check if this is an isolated character
        is_isolated = (pos-1 not in uncovered_positions) and (pos+1 not in uncovered_positions)
        if is_isolated:
            single_char_positions.add(pos)

    # Consider single characters as "covered" for percentage calculation
    adjusted_uncovered = uncovered_positions - single_char_positions
    total_characters = len(non_whitespace_positions)
    covered_characters = total_characters - len(adjusted_uncovered)
    percent_coverage = (covered_characters / total_characters * 100) if total_characters > 0 else 0

    return selected_annotations, uncovered_text, round(percent_coverage, 2)


# annotate the `triad_components_labels_collection` "triad_components_labels" documents that don't have any oak_text_annotations or ols_text_annotations with the initial lexical index text annotator and find the best coverage terms

# In[109]:


# Process triad_components_labels collection for missing annotations
for doc in triad_components_labels_collection.find(
        {"oak_text_annotations": {"$exists": False}, "ols_text_annotations": {"$exists": False}}):
    component_label = doc.get("component_label", "")

    if component_label:
        annotations = list(biosamples_env_triads_precedent_interface.annotate_text(component_label))
        optimized_annotations, uncovered_segments, percent_coverage = optimize_annotations(annotations,
                                                                                           preferred_ontologies,
                                                                                           text=component_label)
        if len(optimized_annotations) > 0:
            # Update the document with the new field
            triad_components_labels_collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {
                    "partial_matches_vs_precedent": {
                        "partial_matches_vs_precedent": optimized_annotations,
                        "uncovered_text_segments": uncovered_segments,
                        "percent_coverage": percent_coverage, }
                }}
            )

# 3 minutes


# fetch the spans that are still not annotated

# In[110]:


# Retrieve all uncovered_text_segments from the collection
cursor = triad_components_labels_collection.find(
    {"partial_matches_vs_precedent.uncovered_text_segments": {"$exists": True}},
    {"partial_matches_vs_precedent.uncovered_text_segments": 1}
)


# do some stopword removal. see https://github.com/igorbrigadir/stopwords/blob/master/en_stopwords.csv
# 
# may not want to remove negaters

# In[111]:


# Set frequency threshold (change this value as needed)
min_word_frequency = 3
min_word_len = 3
stopwords_url = "https://raw.githubusercontent.com/igorbrigadir/stopwords/master/en/lexisnexis.txt"


# In[112]:


# Fetch the stopword list from the URL
response = requests.get(stopwords_url)


# In[113]:


# Check if request was successful
if response.status_code == 200:
    # Process the stopwords: split by lines and remove empty entries
    stop_words = set(response.text.splitlines())
    stop_words.discard("")  # Remove any empty strings from the set
else:
    print("Failed to fetch stopwords. HTTP Status Code:", response.status_code)


# Flatten all uncovered text segments/spans into a single list of words

# In[114]:


all_uncovered_words = []


# In[115]:


for doc in cursor:
    uncovered_segments = doc.get("partial_matches_vs_precedent", {}).get("uncovered_text_segments", [])
    for segment in uncovered_segments:
        words = segment.split()
        for w in words:
            if len(w) >= min_word_len and w not in stop_words:
                all_uncovered_words.extend(words)


# Create a word frequency table

# In[116]:


word_frequencies = Counter(all_uncovered_words)


# Filter out words below the frequency threshold
# 
# Create a dict of words from relevant uncovered spans, with their counts

# In[117]:


filtered_frequencies = {word: count for word, count in word_frequencies.items() if count > min_word_frequency}


# In[118]:


filtered_frequencies


# In[119]:


# Convert dictionary to DataFrame
df = pd.DataFrame(list(filtered_frequencies.items()), columns=['Term', 'Frequency'])


# In[120]:


absent_from_lexical_index_tsv = "absent_from_lexical_index.tsv"


# In[121]:


# Save as TSV
df.to_csv(absent_from_lexical_index_tsv, sep='\t', index=False)


# get annotations of the uncovered words from OLS

# In[122]:


ols_hits_for_frequent_uncovered_words = []


# In[123]:


# todo highly duplicative
for query in tqdm(filtered_frequencies, desc="Processing frequent words", unit="word"):
    query = query.strip().lower()
    if len(query) < MIN_LABEL_LEN:
        continue  # Skip short labels

    start = 0  # Start pagination at 0
    ols_hits = []  # Store matching results

    while True:
        params = {
            "q": query,
            "exact": OLS_REQ_EXACT_MATCH,
            "fieldList": FIELDLIST,
            "ontology": OLS_LABEL_SEARCH_ONTS,
            "queryFields": QUERYFIELDS,
            "rows": rows,
            "start": start,
        }

        response = requests.get(OLS_SEARCH_URL, params=params)
        response.raise_for_status()
        data = response.json()

        # Extract results
        results = data.get("response", {}).get("docs", [])

        # If no results, break loop
        if not results:
            break

        # Process results
        for result in results:
            if result.get("is_defining_ontology", False):
                label_lower = result.get("label", "").lower()
                label_lower_match = label_lower == query

                temp_dict = {
                    "query": query,
                    "exact_label_match": label_lower_match,
                    "label": result.get("label", ""),
                    "synonyms": result.get("synonym", []),
                    "obo_id": result.get("obo_id", ""),
                    "ontology_lc": result.get("ontology_name", "").lower(),
                }
                if OLS_REQ_EXACT_MATCH == "true":
                    temp_dict['exact_something_match'] = True

                ols_hits.append(temp_dict)

        # Check if we need to fetch more results
        num_found = data.get("response", {}).get("numFound", 0)
        start += rows  # Move to the next page

        if start >= num_found:  # Stop if we've retrieved all records
            break

    # Store results in output list if any
    if ols_hits:
        ols_hits_for_frequent_uncovered_words.append({"query": query, "ols_text_annotation": ols_hits})


# insert the annotations of words from uncovered spans into `target_collection` "class_label_cache"

# In[124]:


# todo highly duplicative
for doc in ols_hits_for_frequent_uncovered_words:
    hits = doc.get("ols_text_annotation", [])  # Get list or empty list
    for hit in hits:
        curie = hit.get("obo_id")
        label = hit.get("label")
        synonyms = hit.get("synonyms", [])

        try:
            target_collection.insert_one({
                "curie": curie,
                "label": label,
                "synonyms": synonyms,
            })

        except DuplicateKeyError:
            # Ignore duplicates and continue
            pass


# add the results from the last OLS annotations to the `lexical_index` dict

# stop here unless more lexical index refinement is desired

# In[125]:


# todo highly duplicative
for doc in target_collection.find():
    curie = doc["curie"]
    label = normalize(doc["label"])
    synonyms = [normalize(s) for s in doc.get("synonyms", [])]

    # Ensure label is in the groupings
    if label not in lexical_index["groupings"]:
        lexical_index["groupings"][label] = {
            "term": label,
            "relationships": []
        }

    # Add label relationship
    lexical_index["groupings"][label]["relationships"].append({
        "predicate": "rdfs:label",
        "element": curie,
        "element_term": label,
        "pipeline": ["default"],
        "synonymized": False
    })

    # Process synonyms
    for synonym in synonyms:
        if synonym not in lexical_index["groupings"]:
            lexical_index["groupings"][synonym] = {
                "term": synonym,
                "relationships": []
            }

        lexical_index["groupings"][synonym]["relationships"].append({
            "predicate": "oio:hasRelatedSynonym",
            "element": curie,
            "element_term": synonym,
            "pipeline": ["default"],
            "synonymized": False
        })

# 15 seconds


# In[126]:


type(lexical_index)


# In[127]:


lexical_index.keys()


# In[128]:


len(lexical_index['groupings'])


# In[129]:


def get_prefix(element):
    """Extract the ontology prefix from an element ID (e.g., 'UBERON:0003201' -> 'uberon')."""
    return element.split(":")[0].lower()


# In[130]:


# Define the set of forbidden characters in terms
FORBIDDEN_CHARS_PATTERN = re.compile(r"[\(\)\[\]\{\}'\"!@#$%^&*=\;:|\\<>?]")

def process_groupings(groupings, preferred_ontologies):
    """Modify groupings to remove elements not in preferred ontologies, delete invalid groupings,
    deduplicate relationships, and remove groupings with non-ASCII keys."""
    processed_groupings = {}

    for term, data in groupings.items():
        # Skip groupings with forbidden characters in the term
        if FORBIDDEN_CHARS_PATTERN.search(data["term"]):
            continue

        # Skip groupings whose keys contain non-ASCII characters
        if any(ord(char) > 127 for char in term):
            continue

        seen_elements = set()
        filtered_relationships = []

        for rel in data["relationships"]:
            element_id = rel["element"]

            # Only keep elements from preferred ontologies and ensure no duplicates
            if get_prefix(element_id) in preferred_ontologies and element_id not in seen_elements:
                seen_elements.add(element_id)
                filtered_relationships.append(rel)

        # Only keep non-empty groupings
        if filtered_relationships:
            processed_groupings[term] = {
                "relationships": filtered_relationships,
                "term": data["term"]
            }

    return processed_groupings


# filter the lexical index dict to remove duplicate relations, relations from non-preferred ontologies, and groupings that either have no relations at that point or groupings whose text contains suspicious punctuation characters
# 
# this code may expect a real lexical index, not a lexical index dict

# In[131]:


# Process the groupings
lexical_index["groupings"] = process_groupings(
    lexical_index["groupings"], preferred_ontologies)


# In[132]:


len(lexical_index['groupings'])


# In[133]:


# biosamples_env_triads_precedent_lexical_filtered_index_yaml = "biosamples_env_triads_precedent_lexical_filtered_index.yaml"


# In[134]:


# Save the cleaned YAML file
with open(biosamples_env_triads_precedent_lexical_filtered_index_yaml, "w") as f:
    yaml.dump(lexical_index, f, default_flow_style=False, sort_keys=True)


# In[ ]:





from collections import defaultdict
from collections.abc import Mapping
from datetime import datetime

import click
from pymongo import uri_parser
from tqdm import tqdm

from external_metadata_awareness.mongodb_connection import get_mongo_client


def component_has_valid_label(components, min_len):
    return any(
        "label" in comp and isinstance(comp["label"], str) and len(comp["label"]) >= min_len for comp in components)


def recreate_index(collection, keys, **kwargs):
    index_name = "_".join(f"{k}_{v}" for k, v in keys)
    timestamp = datetime.now().isoformat(timespec='seconds')
    print(f"[{timestamp}] Creating index: {collection.name}.{index_name}")
    try:
        collection.drop_index(index_name)
        print(f"   ↪ Dropped existing index: {index_name}")
    except Exception:
        pass
    collection.create_index(keys, **kwargs)
    print(f"   ↪ Created index: {index_name}")


def normalize_annotations(annotations):
    normalized = []
    for ann in annotations:
        if ann is None:
            continue
        elif isinstance(ann, Mapping):
            normalized.append(ann)
        elif isinstance(ann, list):
            for sub_ann in ann:
                if isinstance(sub_ann, Mapping):
                    normalized.append(sub_ann)
                else:
                    print(f"⚠️ Skipping non-dict in nested list: {sub_ann}")
        else:
            print(f"⚠️ Skipping unknown annotation shape: {ann}")
    return normalized


def deduplicate_annotations(annotations):
    seen = set()
    deduped = []
    for ann in annotations:
        ann_tuple = tuple(sorted((k, v) for k, v in ann.items() if k != "source"))
        if ann_tuple not in seen:
            seen.add(ann_tuple)
            deduped.append(ann)
    return deduped


def add_triads_to_samples(field_name, collection, sample_map, annotation_map):
    query = {field_name: {"$ne": None}}
    projection = {"accession": 1, field_name: 1, "_id": 0}
    docs = list(collection.find(query, projection))

    for doc in docs:
        accession = doc["accession"]
        raw_value = doc[field_name]
        components = []
        for component in annotation_map.get(raw_value, []):
            components.append({
                "raw": component.get("raw", raw_value),
                **{k: v for k, v in component.items() if k != "raw"}
            })

        if accession not in sample_map:
            sample_map[accession] = {}
        sample_map[accession][field_name] = {
            "raw": raw_value,
            "components": components
        }


@click.command()
@click.option('--mongo-uri', default='mongodb://localhost:27017/ncbi_metadata', help='MongoDB connection URI (must start with mongodb:// and include database name)')
@click.option('--env-file', default=None, help='Path to .env file for credentials (should contain MONGO_USER and MONGO_PASSWORD)')
@click.option('--dest-collection', default='env_triads', help='Destination collection for output')
@click.option('--min-label-length', default=3, show_default=True, help='Minimum label length')
@click.option('--recreate-indices/--no-recreate-indices', default=True, help='Whether to recreate indices')
@click.option('--acceptable-prefix', multiple=True,
              default=["DOID", "ENVO", "FOODON", "MONDO", "NCBITAXON", "PO", "UBERON"])
@click.option('--verbose', is_flag=True, help='Show verbose connection output')
def populate(mongo_uri, env_file, dest_collection, min_label_length, acceptable_prefix, recreate_indices, verbose):
    # Connect to MongoDB
    client = get_mongo_client(
        mongo_uri=mongo_uri,
        env_file=env_file,
        debug=verbose
    )
    
    # Extract database name from URI
    parsed = uri_parser.parse_uri(mongo_uri)
    db_name = parsed.get('database')
    
    if not db_name:
        raise ValueError("MongoDB URI must include a database name")
        
    db = client[db_name]

    biosamples_flattened = db["biosamples_flattened"]
    biosamples_env_triad_value_counts_gt_1 = db["biosamples_env_triad_value_counts_gt_1"]
    env_triad_component_labels = db["env_triad_component_labels"]
    env_triad_component_curies_uc = db["env_triad_component_curies_uc"]

    # Drop existing destination collection if it exists
    db.drop_collection(dest_collection)
    env_triads = db[dest_collection]

    if recreate_indices:
        print("Creating indexes...")

        # These indexes can improve performance if the collections are queried frequently or joined manually later
        recreate_index(biosamples_flattened, [("env_broad_scale", 1)])
        recreate_index(biosamples_flattened, [("env_local_scale", 1)])
        recreate_index(biosamples_flattened, [("env_medium", 1)])
        recreate_index(biosamples_flattened, [("accession", 1)], unique=True)

        recreate_index(biosamples_env_triad_value_counts_gt_1, [("components.label", 1)])

        recreate_index(env_triad_component_labels, [("label", 1)])
        recreate_index(env_triad_component_labels, [("oak_text_annotations", 1)])
        recreate_index(env_triad_component_labels, [("oak_text_annotations.prefix_uc", 1)])
        recreate_index(env_triad_component_labels, [("ols_text_annotations", 1)])
        recreate_index(env_triad_component_labels, [("ols_text_annotations.ontology_prefix_uc", 1)])

        recreate_index(env_triad_component_curies_uc, [("curie_uc", 1)])
        recreate_index(env_triad_component_curies_uc, [("prefix_uc", 1)])

        recreate_index(env_triads, [("accession", 1)], unique=True)
        print("✅ Index setup complete.\n")

    print("Retrieving triad documents with labels... (this takes ~5 minutes)")
    triad_docs = list(biosamples_env_triad_value_counts_gt_1.find(
        {"components": {"$elemMatch": {"label": {"$exists": True}}}},
        {"env_triad_value": 1, "components.label": 1, "components.curie_uc": 1, "components.raw": 1, "_id": 0}))

    # Filter documents to only include those with valid labels of sufficient length
    triad_docs = [doc for doc in triad_docs if component_has_valid_label(doc.get("components", []), min_label_length)]
    print(f"Found {len(triad_docs)} triad documents with valid labels")

    print("Retrieving OAK annotations...")
    oak_annotations = list(env_triad_component_labels.find(
        {'oak_text_annotations': {'$elemMatch': {'prefix_uc': {'$in': list(acceptable_prefix)}}}},
        {'_id': 0, 'label': 1, 'oak_text_annotations': 1}))
    print(f"Found {len(oak_annotations)} OAK annotations")

    print("Retrieving OLS annotations...")
    ols_annotations = list(env_triad_component_labels.find(
        {'ols_text_annotations': {'$elemMatch': {'ontology_prefix_uc': {'$in': list(acceptable_prefix)}}}},
        {'_id': 0, 'label': 1, 'ols_text_annotations': 1}))
    print(f"Found {len(ols_annotations)} OLS annotations")

    # Map labels to their annotations
    label_to_annotations = defaultdict(list)

    print("Processing OAK annotations...")
    for item in oak_annotations:
        for ann in item.get("oak_text_annotations", []):
            label = ann.get("rdfs_label") or ann.get("object_label")
            prefix_uc = ann.get("prefix_uc")
            if prefix_uc in acceptable_prefix and isinstance(label, str) and len(label) >= min_label_length:
                label_to_annotations[item["label"]].append({
                    "id": ann.get("object_id"),
                    "label": label,
                    "prefix_uc": prefix_uc,
                    "source": "OAK"
                })

    print("Processing OLS annotations...")
    for item in ols_annotations:
        for ann in item.get("ols_text_annotations", []):
            label = ann.get("label")
            prefix_uc = ann.get("ontology_prefix_uc")
            if prefix_uc in acceptable_prefix and isinstance(label, str) and len(label) >= min_label_length:
                label_to_annotations[item["label"]].append({
                    "id": ann.get("obo_id"),
                    "label": label,
                    "prefix_uc": prefix_uc,
                    "source": "OLS"
                })

    # Deduplicate annotations for each label
    for label in label_to_annotations:
        label_to_annotations[label] = deduplicate_annotations(label_to_annotations[label])

    print("Retrieving CURIE lookup data...")
    curie_lookup = list(env_triad_component_curies_uc.find(
        {"curie_uc": {"$exists": True}, "prefix_uc": {"$in": list(acceptable_prefix)}, "label": {"$exists": True}},
        {"curie_uc": 1, "label": 1, "prefix_uc": 1, "mappings": 1, "_id": 0}))
    print(f"Found {len(curie_lookup)} CURIE lookup entries")

    # Map CURIEs to their annotations
    curie_uc_to_annotation = defaultdict(list)
    for item in curie_lookup:
        curie_uc = item.get("curie_uc")
        label = item.get("label")
        if curie_uc and isinstance(label, str) and len(label) >= min_label_length:
            curie_uc_to_annotation[curie_uc].append({
                "id": curie_uc,
                "label": label,
                "prefix_uc": item.get("prefix_uc"),
                "source": "asserted CURIe"
            })
            for mapping in item.get("mappings", []):
                label_lc = mapping.get("label_lc")
                if isinstance(label_lc, str) and len(label_lc) >= min_label_length:
                    curie_uc_to_annotation[curie_uc].append({
                        "id": mapping.get("curie"),
                        "label": label_lc,
                        "prefix_uc": mapping.get("prefix"),
                        "source": "asserted CURIe mapping"
                    })

    print("Building environmental triad annotations map...")
    env_triad_to_annotations = defaultdict(list)
    for item in tqdm(triad_docs, desc="Processing triad documents"):
        raw_value = item.get("env_triad_value")
        for comp in item.get("components", []):
            label = comp.get("label")
            curie_uc = comp.get("curie_uc")
            annotations = []
            if label in label_to_annotations:
                annotations.extend(label_to_annotations[label])
            if curie_uc in curie_uc_to_annotation:
                annotations.extend(curie_uc_to_annotation[curie_uc])
            normalized = deduplicate_annotations(normalize_annotations(annotations))
            if normalized:
                env_triad_to_annotations[raw_value].append({
                    "raw": comp.get("raw", label),
                    **normalized[0]  # Only use the first deduplicated, normalized annotation
                })
            else:
                env_triad_to_annotations[raw_value].append({
                    "raw": comp.get("raw", label)
                })

    # Deduplicate the components for each environmental triad value
    for key in env_triad_to_annotations:
        env_triad_to_annotations[key] = deduplicate_annotations(env_triad_to_annotations[key])

    print("Building accession-to-structured-sample map...")
    accession_to_structured_sample = {}
    for field in ["env_broad_scale", "env_local_scale", "env_medium"]:
        print(f"Processing {field}...")
        add_triads_to_samples(field, biosamples_flattened, accession_to_structured_sample, env_triad_to_annotations)

    print(f"Creating index on {dest_collection}.accession...")
    env_triads.create_index("accession", unique=True)
    
    print(f"Upserting {len(accession_to_structured_sample)} documents to {dest_collection}...")
    for accession, triad_data in tqdm(accession_to_structured_sample.items(), desc="Upserting env_triads"):
        env_triads.update_one({"accession": accession}, {"$set": triad_data}, upsert=True)

    print(f"Successfully populated {dest_collection} collection with {len(accession_to_structured_sample)} documents")


if __name__ == '__main__':
    populate()

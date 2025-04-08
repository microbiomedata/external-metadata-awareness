from collections import defaultdict
from collections.abc import Mapping
from datetime import datetime

import click
from pymongo import MongoClient
from tqdm import tqdm


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
@click.option('--db-name', default='ncbi_metadata', help='Database name')
@click.option('--dest-collection', default='env_triads', help='Destination collection for output')
@click.option('--min-label-length', default=3, show_default=True, help='Minimum label length')
@click.option('--mongo-uri', default='mongodb://localhost:27017', help='Mongo URI')
@click.option('--recreate-indices/--no-recreate-indices', default=True)
@click.option('--acceptable-prefix', multiple=True,
              default=["DOID", "ENVO", "FOODON", "MONDO", "NCBITAXON", "PO", "UBERON"])
def populate(mongo_uri, db_name, dest_collection, min_label_length, acceptable_prefix, recreate_indices):
    client = MongoClient(mongo_uri)
    db = client[db_name]

    biosamples_flattened = db["biosamples_flattened"]
    biosamples_env_triad_value_counts_gt_1 = db["biosamples_env_triad_value_counts_gt_1"]
    env_triad_component_labels = db["env_triad_component_labels"]
    env_triad_component_curies_uc = db["env_triad_component_curies_uc"]

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

    triad_docs = list(biosamples_env_triad_value_counts_gt_1.find(
        {"components": {"$elemMatch": {"label": {"$exists": True}}}},
        {"env_triad_value": 1, "components.label": 1, "components.curie_uc": 1, "components.raw": 1, "_id": 0})) # todo let the user know that this takes ~ 5 minutes

    # todo all takes place in memory. swap exhausted on 32 GB 2020 ish macbook pro

    triad_docs = [doc for doc in triad_docs if component_has_valid_label(doc.get("components", []), min_label_length)]

    oak_annotations = list(env_triad_component_labels.find(
        {'oak_text_annotations': {'$elemMatch': {'prefix_uc': {'$in': list(acceptable_prefix)}}}},
        {'_id': 0, 'label': 1, 'oak_text_annotations': 1}))

    ols_annotations = list(env_triad_component_labels.find(
        {'ols_text_annotations': {'$elemMatch': {'ontology_prefix_uc': {'$in': list(acceptable_prefix)}}}},
        {'_id': 0, 'label': 1, 'ols_text_annotations': 1}))

    label_to_annotations = defaultdict(list)

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

    for label in label_to_annotations:
        label_to_annotations[label] = deduplicate_annotations(label_to_annotations[label])

    curie_lookup = list(env_triad_component_curies_uc.find(
        {"curie_uc": {"$exists": True}, "prefix_uc": {"$in": list(acceptable_prefix)}, "label": {"$exists": True}},
        {"curie_uc": 1, "label": 1, "prefix_uc": 1, "mappings": 1, "_id": 0}))

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

    env_triad_to_annotations = defaultdict(list)
    for item in triad_docs:
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

    for key in env_triad_to_annotations:
        env_triad_to_annotations[key] = deduplicate_annotations(env_triad_to_annotations[key])

    accession_to_structured_sample = {}
    for field in ["env_broad_scale", "env_local_scale", "env_medium"]:
        add_triads_to_samples(field, biosamples_flattened, accession_to_structured_sample, env_triad_to_annotations)

    env_triads.create_index("accession", unique=True)
    for accession, triad_data in tqdm(accession_to_structured_sample.items(), desc="Upserting env_triads"):
        env_triads.update_one({"accession": accession}, {"$set": triad_data}, upsert=True)


if __name__ == '__main__':
    populate()

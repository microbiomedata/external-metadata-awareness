#!/usr/bin/env python3
"""
Standalone script to annotate documents in the env_triad_component_labels collection.

This script first loads a lexical index for text annotation from
"expanded_envo_po_lexical_index.yaml" if that file exists; otherwise, it builds
the index from the ENVO connection string and saves it for future use.
It then uses the lexical index via a TextAnnotatorInterface to annotate the
"label" field in each document, filtering out short or subsumed annotations,
computing the combined coverage, and updating the document with:
  - "oak_text_annotations"
  - "combined_oak_coverage"
  - "oak_annotations_count"

Notes:
  - Annotation coordinates are 1-based and inclusive.
  - Combined coverage is computed by merging overlapping or adjacent intervals.
"""

import os
from pymongo import MongoClient
from oaklib import get_adapter
from oaklib.interfaces.text_annotator_interface import TextAnnotatorInterface
from oaklib.utilities.lexical.lexical_indexer import load_lexical_index, create_lexical_index, save_lexical_index
from tqdm import tqdm

# Set the minimum annotation length for retaining an annotation.
MIN_ANNOTATION_LENGTH = 3
LEX_INDEX_FILE = "expanded_envo_po_lexical_index.yaml"


def annotation_to_dict(ann, label_length):
    """
    Convert an annotation object to a dictionary, filtering out keys with None or empty list values.
    Also calculates and adds the annotation's coverage of the label using 1-based inclusive indexing:
         coverage = (subject_end - subject_start + 1) / label_length.
    """
    result = {}
    for key, value in vars(ann).items():
        # Skip if value is None.
        if value is None:
            continue
        # Skip if value is an empty list.
        if isinstance(value, list) and len(value) == 0:
            continue
        result[key] = value
    if hasattr(ann, "subject_start") and hasattr(ann, "subject_end"):
        ann_length = ann.subject_end - ann.subject_start + 1
        result["coverage"] = ann_length / label_length if label_length > 0 else 0
    return result


def filter_subsumed_annotations(annotations):
    """
    Filter out annotations whose ranges are completely subsumed by another annotation's range.

    An annotation A is subsumed if there exists another annotation B (B != A)
    such that B.subject_start <= A.subject_start and B.subject_end >= A.subject_end,
    and the ranges are not exactly equal.

    Annotations without range information are retained.
    """
    filtered = []
    for i, a in enumerate(annotations):
        if "subject_start" not in a or "subject_end" not in a:
            filtered.append(a)
            continue

        subsumed = False
        a_start, a_end = a["subject_start"], a["subject_end"]
        for j, b in enumerate(annotations):
            if i == j:
                continue
            if "subject_start" in b and "subject_end" in b:
                b_start, b_end = b["subject_start"], b["subject_end"]
                if b_start <= a_start and b_end >= a_end:
                    if (b_start, b_end) != (a_start, a_end):
                        subsumed = True
                        break
        if not subsumed:
            filtered.append(a)
    return filtered


def compute_combined_oak_coverage(annotations, label_length):
    """
    Compute the combined coverage provided by the union of all annotation ranges.
    Each annotation range is defined by its subject_start and subject_end,
    and uses 1-based inclusive indexing.

    The function merges overlapping or adjacent intervals, then computes:
         combined_oak_coverage = (total_covered_characters) / label_length.
    """
    intervals = []
    for ann in annotations:
        if "subject_start" in ann and "subject_end" in ann:
            intervals.append((ann["subject_start"], ann["subject_end"]))
    if not intervals or label_length == 0:
        return 0
    # Sort intervals by start coordinate.
    intervals.sort(key=lambda x: x[0])
    merged = []
    current_start, current_end = intervals[0]
    for start, end in intervals[1:]:
        if start <= current_end + 1:  # Merge overlapping or adjacent intervals.
            current_end = max(current_end, end)
        else:
            merged.append((current_start, current_end))
            current_start, current_end = start, end
    merged.append((current_start, current_end))
    total_covered = sum(end - start + 1 for start, end in merged)
    return total_covered / label_length


def main():
    # MongoDB connection configuration.
    mongo_url = "mongodb://localhost:27017"
    client = MongoClient(mongo_url)
    db = client.ncbi_metadata
    collection = db.env_triad_component_labels

    # Attempt to load the lexical index from file if it exists.
    if os.path.exists(LEX_INDEX_FILE):
        print(f"Loading lexical index from {LEX_INDEX_FILE}...")
        lexical_index = load_lexical_index(LEX_INDEX_FILE)
    else:
        print(f"Lexical index file {LEX_INDEX_FILE} not found; building from ENVO adapter...")
        envo_adapter = get_adapter("sqlite:obo:envo")
        lexical_index = create_lexical_index(envo_adapter)
        # Optionally save the newly built index for future runs.
        save_lexical_index(lexical_index, LEX_INDEX_FILE)
        print(f"Lexical index saved to {LEX_INDEX_FILE}")

    # Set up the TextAnnotatorInterface with the lexical index.
    annotator = TextAnnotatorInterface()
    annotator.lexical_index = lexical_index

    total_docs = collection.estimated_document_count()
    print(f"Processing {total_docs} documents from env_triad_component_labels collection.")

    min_length = 3
    query = {
        "label_digits_only": False,
        "label_length": {"$gte": min_length}
    }

    for doc in tqdm(collection.find(query), total=total_docs, desc="Annotating documents"):
        label = doc.get("label")
        if not label:
            continue

        # Annotate using the lexical index via the TextAnnotatorInterface.
        annotations = list(annotator.annotate_text(label))
        processed_annotations = []
        label_length = len(label)

        for ann in annotations:
            if hasattr(ann, "subject_start") and hasattr(ann, "subject_end"):
                ann_length = ann.subject_end - ann.subject_start + 1
                if ann_length < MIN_ANNOTATION_LENGTH:
                    continue  # Skip too-short annotations.
            ann_dict = annotation_to_dict(ann, label_length)
            processed_annotations.append(ann_dict)

        filtered_annotations = filter_subsumed_annotations(processed_annotations)
        combined_coverage = compute_combined_oak_coverage(filtered_annotations, label_length)
        annotations_count = len(filtered_annotations)

        update_data = {
            "oak_text_annotations": filtered_annotations,
            "combined_oak_coverage": combined_coverage,
            "oak_annotations_count": annotations_count
        }
        collection.update_one({"_id": doc["_id"]}, {"$set": update_data})

    print("Annotation processing complete.")


if __name__ == '__main__':
    main()

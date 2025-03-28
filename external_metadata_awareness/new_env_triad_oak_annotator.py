#!/usr/bin/env python3
"""
Standalone script to annotate documents in the env_triad_component_labels collection.

For each document:
  - Retrieve the "label" field (e.g., "ocean water").
  - Use the ENVO ontology adapter’s annotate_text method (via your semantic SQL/OAK database)
    to obtain matching annotations.
  - For each annotation:
      * If the annotation's span length (subject_end - subject_start + 1) is at least MIN_ANNOTATION_LENGTH,
        calculate its individual coverage.
      * Convert the annotation object to a dictionary, omitting keys with None values.
  - Filter out any annotations whose ranges are completely subsumed by another annotation's range.
  - Compute the combined coverage from the union of annotation ranges.
  - Update the document by inserting the filtered annotations under "oak_text_annotations",
    the computed combined coverage as "combined_oak_envo_coverage", and the count of annotations
    as "oak_envo_annotations_count".

Notes:
  - Annotation coordinates are 1-based and inclusive.
  - The combined coverage is computed by merging overlapping or adjacent intervals.

Requirements:
  • MongoDB database "ncbi_metadata" with collection "env_triad_component_labels".
  • ENVO ontology adapter (e.g., "sqlite:obo:envo") that supports annotate_text.
"""

from pymongo import MongoClient
from oaklib import get_adapter
from tqdm import tqdm

# Set the minimum annotation length for retaining an annotation.
MIN_ANNOTATION_LENGTH = 3


def annotation_to_dict(ann, label_length):
    """
    Convert an annotation object to a dictionary, filtering out keys with None values.
    Also calculates and adds the annotation's coverage of the label.
    Uses 1-based inclusive indexing:
       coverage = (subject_end - subject_start + 1) / label_length.
    """
    result = {}
    for key, value in vars(ann).items():
        if value is not None:
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


def compute_combined_oak_envo_coverage(annotations, label_length):
    """
    Compute the combined coverage provided by the union of all annotation ranges.
    Each annotation range is defined by its subject_start and subject_end,
    and uses 1-based inclusive indexing.

    The function merges overlapping or adjacent intervals, then computes:
        combined_oak_envo_coverage = (total_covered_characters) / label_length.
    """
    intervals = []
    for ann in annotations:
        if "subject_start" in ann and "subject_end" in ann:
            intervals.append((ann["subject_start"], ann["subject_end"]))
    if not intervals or label_length == 0:
        return 0
    # Sort intervals by their start coordinate.
    intervals.sort(key=lambda x: x[0])
    merged = []
    current_start, current_end = intervals[0]
    for start, end in intervals[1:]:
        # If the next interval overlaps or is immediately adjacent (inclusive), merge them.
        if start <= current_end + 1:
            current_end = max(current_end, end)
        else:
            merged.append((current_start, current_end))
            current_start, current_end = start, end
    merged.append((current_start, current_end))
    # For each merged interval, compute its length using inclusive indexing.
    total_covered = sum(end - start + 1 for start, end in merged)
    return total_covered / label_length


def main():
    # MongoDB connection configuration.
    mongo_url = "mongodb://localhost:27017"
    client = MongoClient(mongo_url)
    db = client.ncbi_metadata
    collection = db.env_triad_component_labels

    # Set up the ENVO ontology adapter (using your semantic SQL/OAK database).
    envo_adapter_string = "sqlite:obo:envo"
    envo_adapter = get_adapter(envo_adapter_string)

    total_docs = collection.estimated_document_count()
    print(f"Processing {total_docs} documents from env_triad_component_labels collection.")

    # Process each document.
    for doc in tqdm(collection.find(), total=total_docs, desc="Annotating documents"):
        label = doc.get("label")
        if not label:
            continue

        # Obtain annotations using the adapter.
        annotations = list(envo_adapter.annotate_text(label))
        processed_annotations = []
        label_length = len(label)

        for ann in annotations:
            if hasattr(ann, "subject_start") and hasattr(ann, "subject_end"):
                ann_length = ann.subject_end - ann.subject_start + 1
                if ann_length < MIN_ANNOTATION_LENGTH:
                    continue  # Skip annotations that are too short.
            ann_dict = annotation_to_dict(ann, label_length)
            processed_annotations.append(ann_dict)

        # Remove annotations whose ranges are subsumed by others.
        filtered_annotations = filter_subsumed_annotations(processed_annotations)
        # Compute the combined coverage from the union of annotation ranges.
        combined_coverage = compute_combined_oak_envo_coverage(filtered_annotations, label_length)
        # Calculate the number of (filtered) annotations.
        annotations_count = len(filtered_annotations)

        update_data = {
            "oak_text_annotations": filtered_annotations,
            "combined_oak_envo_coverage": combined_coverage,
            "oak_envo_annotations_count": annotations_count
        }
        collection.update_one({"_id": doc["_id"]}, {"$set": update_data})

    print("Annotation processing complete.")


if __name__ == '__main__':
    main()

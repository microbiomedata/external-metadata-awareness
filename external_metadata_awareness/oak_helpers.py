from typing import Dict, Any, Optional
from oaklib.datamodels.text_annotator import TextAnnotation
from types import SimpleNamespace

def build_element_to_label_map(lexical_index) -> Dict[str, str]:
    """
    Given a loaded lexical index (from oaklib), extract a mapping from
    ontology term CURIEs to their authoritative rdfs:label values.

    Parameters:
    - lexical_index: a LexicalIndex object (oaklib), typically returned from create_lexical_index() or load_lexical_index()

    Returns:
    - A dict mapping from CURIE (e.g., 'ENVO:02000023') → label (e.g., 'bile material')
    """
    index_data = lexical_index._as_dict  # no parens
    element_to_label = {}

    for term, grouping in index_data["groupings"].items():
        for rel in grouping["relationships"]:
            if rel["predicate"] == "rdfs:label":
                element = rel["element"]
                label = rel["element_term"]
                element_to_label[element] = label

    return element_to_label


def annotation_to_dict(
    ann: TextAnnotation | SimpleNamespace,
    label_length: int,
    element_to_label: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Convert a TextAnnotation to a dict for MongoDB storage.

    Adds:
    - `coverage`: float between 0 and 1
    - `rdfs_label`: if mapping is provided
    """
    result = {}
    for key, value in vars(ann).items():
        if value is None or (isinstance(value, list) and not value):
            continue
        result[key] = value

    if hasattr(ann, "subject_start") and hasattr(ann, "subject_end"):
        ann_length = ann.subject_end - ann.subject_start + 1
        result["coverage"] = ann_length / label_length if label_length > 0 else 0

    if element_to_label and hasattr(ann, "object_id"):
        result["rdfs_label"] = element_to_label.get(ann.object_id)

    return result

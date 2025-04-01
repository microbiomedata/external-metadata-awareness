#!/usr/bin/env python3
"""
Standalone script to combine lexical indices for ENVO and PO.

This script:
  - Obtains a punctuation-insensitive lexical index from each ontology adapter.
  - Adds obsolete terms from each ontology with the "obsolete " prefix removed.
  - For any term that contains punctuation, creates an alternate entry with punctuation replaced by whitespace.
  - Merges the two indices.
  - Saves the merged index as "envo_inc_obsoletes_po_punct_free_index.yaml".

Requirements:
  • oaklib and its dependencies
  • The ENVO and PO ontology adapters (e.g., "sqlite:obo:envo" and "sqlite:obo:po")
  • A writable location for the output YAML file.
"""

import re
from oaklib import get_adapter
from oaklib.datamodels.lexical_index import (
    LexicalIndex,
    LexicalTransformationPipeline,
    RelationshipToTerm,
    LexicalGrouping,
    LexicalTransformation,
    TransformationType
)
from oaklib.datamodels.synonymizer_datamodel import Synonymizer
from oaklib.utilities.lexical.lexical_indexer import (
    apply_transformation,
    create_lexical_index,
    save_lexical_index
)

# Adapter strings for the two ontologies.
ENVO_ADAPTER_STRING = "sqlite:obo:envo"
PO_ADAPTER_STRING = "sqlite:obo:po"


def are_pipelines_compatible(pipeline1, pipeline2):
    """
    Check if two pipelines are functionally equivalent.
    """
    if len(pipeline1.transformations) != len(pipeline2.transformations):
        return False
    for t1, t2 in zip(pipeline1.transformations, pipeline2.transformations):
        t1_type = getattr(t1.type, 'text', str(t1.type))
        t2_type = getattr(t2.type, 'text', str(t2.type))
        if t1_type != t2_type:
            return False
        t1_params = getattr(t1, 'params', [])
        t2_params = getattr(t2, 'params', [])
        if len(t1_params) != len(t2_params):
            return False
    return True


def relationship_equals(rel1, rel2):
    """
    Compare two relationships for functional equality.
    """
    key_attrs = ['predicate', 'element', 'element_term', 'source']
    return all(getattr(rel1, attr, None) == getattr(rel2, attr, None)
               for attr in key_attrs)


def deduplicate_lexical_index(lexical_index):
    """
    Remove duplicate relationships from all groupings in a lexical index.
    """
    for term, grouping in lexical_index.groupings.items():
        unique_relationships = []
        for rel in grouping.relationships:
            if not any(relationship_equals(rel, unique_rel) for unique_rel in unique_relationships):
                unique_relationships.append(rel)
        grouping.relationships = unique_relationships
    return lexical_index


def merge_lexical_indexes(index1, index2, validate_pipelines=True):
    """
    Merge two lexical indexes ensuring pipeline compatibility.
    """
    merged_index = LexicalIndex()
    if validate_pipelines:
        for name, pipeline1 in index1.pipelines.items():
            if name in index2.pipelines:
                pipeline2 = index2.pipelines[name]
                if not are_pipelines_compatible(pipeline1, pipeline2):
                    raise ValueError(
                        f"Pipeline '{name}' is defined differently in the two indexes. "
                        "Set validate_pipelines=False to override this check."
                    )
    for name, pipeline in index1.pipelines.items():
        merged_index.pipelines[name] = pipeline
    for name, pipeline in index2.pipelines.items():
        if name not in merged_index.pipelines:
            merged_index.pipelines[name] = pipeline
    # Copy groupings from index1.
    for term, grouping in index1.groupings.items():
        merged_index.groupings[term] = LexicalGrouping(term=term)
        merged_index.groupings[term].relationships = list(grouping.relationships)
    # Merge groupings from index2.
    for term, grouping in index2.groupings.items():
        if term not in merged_index.groupings:
            merged_index.groupings[term] = LexicalGrouping(term=term)
            merged_index.groupings[term].relationships = list(grouping.relationships)
        else:
            merged_index.groupings[term].relationships.extend(grouping.relationships)
    return deduplicate_lexical_index(merged_index)


def add_obsolete_terms_to_lexical_index(oi, lexical_index):
    """
    Find all obsolete classes in an ontology, remove the "obsolete " prefix from their labels,
    and add them to an existing lexical index. Also applies punctuation normalization.
    """
    obsolete_classes = list(oi.obsoletes())
    print(f"Found {len(obsolete_classes)} obsolete classes")

    # Define a punctuation normalization rule.
    punctuation_rule = Synonymizer(
        description="Replace all punctuation with spaces",
        match=r"[^\w\s]|_",  # Match any non-alphanumeric, non-whitespace character or underscore.
        replacement=r" "  # Replace with a space.
    )

    for obsolete_entity in obsolete_classes:
        orig_label = oi.label(obsolete_entity)
        if not orig_label:
            continue
        if orig_label.lower().startswith("obsolete "):
            clean_label = re.sub(r'^obsolete\s+', '', orig_label, flags=re.IGNORECASE)
        else:
            clean_label = orig_label

        # Process the main label through each pipeline.
        for pipeline_name, pipeline in lexical_index.pipelines.items():
            transformed_label = clean_label
            punctuation_transformation = LexicalTransformation(
                TransformationType.Synonymization,
                params=[punctuation_rule]
            )
            result = apply_transformation(transformed_label, punctuation_transformation)
            if isinstance(result, tuple):
                transformed_label = result[1]
            else:
                transformed_label = result
            for transformation in pipeline.transformations:
                result = apply_transformation(transformed_label, transformation)
                if isinstance(result, tuple):
                    transformed_label = result[1]
                else:
                    transformed_label = result

            rel = RelationshipToTerm(
                predicate='rdfs:label',
                element=obsolete_entity,
                element_term=clean_label,
                pipeline=[pipeline_name],
                synonymized=False
            )
            if transformed_label not in lexical_index.groupings:
                lexical_index.groupings[transformed_label] = LexicalGrouping(term=transformed_label)
                lexical_index.groupings[transformed_label].relationships = [rel]
            else:
                exists = any(existing_rel.element == rel.element and existing_rel.predicate == rel.predicate
                             for existing_rel in lexical_index.groupings[transformed_label].relationships)
                if not exists:
                    lexical_index.groupings[transformed_label].relationships.append(rel)

        # Process aliases for the obsolete entity.
        alias_map = oi.entity_alias_map(obsolete_entity)
        for pipeline_name, pipeline in lexical_index.pipelines.items():
            for predicate, aliases in alias_map.items():
                for alias in aliases:
                    if alias == orig_label and predicate == 'rdfs:label':
                        continue
                    if alias.lower().startswith("obsolete "):
                        clean_alias = re.sub(r'^obsolete\s+', '', alias, flags=re.IGNORECASE)
                    else:
                        clean_alias = alias

                    transformed_alias = clean_alias
                    result = apply_transformation(transformed_alias, punctuation_transformation)
                    if isinstance(result, tuple):
                        transformed_alias = result[1]
                    else:
                        transformed_alias = result
                    for transformation in pipeline.transformations:
                        result = apply_transformation(transformed_alias, transformation)
                        if isinstance(result, tuple):
                            transformed_alias = result[1]
                        else:
                            transformed_alias = result

                    rel = RelationshipToTerm(
                        predicate=predicate,
                        element=obsolete_entity,
                        element_term=clean_alias,
                        pipeline=[pipeline_name],
                        synonymized=False
                    )
                    if transformed_alias not in lexical_index.groupings:
                        lexical_index.groupings[transformed_alias] = LexicalGrouping(term=transformed_alias)
                        lexical_index.groupings[transformed_alias].relationships = [rel]
                    else:
                        exists = any(existing_rel.element == rel.element and existing_rel.predicate == rel.predicate
                                     for existing_rel in lexical_index.groupings[transformed_alias].relationships)
                        if not exists:
                            lexical_index.groupings[transformed_alias].relationships.append(rel)
    return deduplicate_lexical_index(lexical_index)


def create_punctuation_insensitive_index(oi):
    """
    Create a lexical index that is insensitive to punctuation by replacing all punctuation with spaces.
    """
    punctuation_rules = [
        Synonymizer(
            description="Replace all punctuation with spaces",
            match=r"[^\w\s]|_",
            replacement=r" "
        )
    ]
    pipeline = LexicalTransformationPipeline(
        name="punctuation_insensitive",
        transformations=[
            LexicalTransformation(TransformationType.Synonymization, params=punctuation_rules),
            LexicalTransformation(TransformationType.CaseNormalization),
            LexicalTransformation(TransformationType.WhitespaceNormalization)
        ]
    )
    lexical_index = create_lexical_index(
        oi,
        pipelines=[pipeline],
        synonym_rules=punctuation_rules
    )
    return lexical_index


def main():
    # Obtain ontology adapters.
    envo_adapter = get_adapter(ENVO_ADAPTER_STRING)
    po_adapter = get_adapter(PO_ADAPTER_STRING)

    # Create punctuation-insensitive lexical indices for each ontology.
    print("Creating ENVO punctuation-insensitive index...")
    envo_index = create_punctuation_insensitive_index(envo_adapter)
    print("Adding obsolete ENVO terms...")
    envo_index = add_obsolete_terms_to_lexical_index(envo_adapter, envo_index)

    print("Creating PO punctuation-insensitive index...")
    po_index = create_punctuation_insensitive_index(po_adapter)
    # (If you wish to add obsolete terms for PO as well, you can call add_obsolete_terms_to_lexical_index for PO.)

    # Merge the two indices.
    try:
        merged_index = merge_lexical_indexes(envo_index, po_index, validate_pipelines=True)
    except ValueError as e:
        print(f"Merging failed: {e}\nProceeding with pipeline validation disabled.")
        merged_index = merge_lexical_indexes(envo_index, po_index, validate_pipelines=False)

    # Save the merged lexical index to a YAML file.
    output_file = "expanded_envo_po_lexical_index.yaml"
    save_lexical_index(merged_index, output_file)
    print(f"Merged lexical index saved to {output_file}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Create TSV directly from MongoDB collection flatness analysis.
"""

import click
from pymongo import MongoClient
from collections import defaultdict, Counter
import csv
from typing import Dict, Any


def analyze_document_structure(doc: Dict[str, Any], path: str = "") -> Dict[str, Any]:
    """Analyze a single document for nested structures."""
    analysis = {
        'nested_objects': [],
        'arrays': [],
        'simple_fields': [],
        'null_fields': [],
        'max_depth': 0
    }

    def traverse(obj, current_path="", depth=0):
        analysis['max_depth'] = max(analysis['max_depth'], depth)

        if isinstance(obj, dict):
            for key, value in obj.items():
                field_path = f"{current_path}.{key}" if current_path else key

                if value is None:
                    analysis['null_fields'].append(field_path)
                elif isinstance(value, dict):
                    analysis['nested_objects'].append(field_path)
                    traverse(value, field_path, depth + 1)
                elif isinstance(value, list):
                    analysis['arrays'].append(field_path)
                    if value:
                        traverse(value[0], f"{field_path}[0]", depth + 1)
                else:
                    analysis['simple_fields'].append(field_path)
        elif isinstance(obj, list):
            if obj:
                traverse(obj[0], f"{current_path}[0]", depth + 1)

    traverse(doc)
    return analysis


def calculate_flatness_score(analysis: Dict[str, Any]) -> float:
    """Calculate a flatness score (0-100, where 100 is completely flat)."""
    total_fields = (len(analysis['simple_fields']) +
                   len(analysis['nested_objects']) +
                   len(analysis['arrays']) +
                   len(analysis['null_fields']))

    if total_fields == 0:
        return 100.0

    flat_fields = len(analysis['simple_fields']) + len(analysis['null_fields'])
    depth_penalty = min(analysis['max_depth'] * 10, 50)
    base_score = (flat_fields / total_fields) * 100
    return max(0, base_score - depth_penalty)


@click.command()
@click.option('--mongo-uri', default='mongodb://localhost:27017/ncbi_metadata',
              help='MongoDB connection URI')
@click.option('--sample-size', default=100, type=int,
              help='Number of documents to sample per collection')
@click.option('--output-file', default='collection_flatness_analysis.tsv',
              help='Output TSV filename')
def main(mongo_uri, sample_size, output_file):
    """Analyze MongoDB collections and create TSV output."""

    client = MongoClient(mongo_uri)
    db_name = mongo_uri.split('/')[-1]
    db = client[db_name]

    collections = db.list_collection_names()
    results = []

    for collection_name in sorted(collections):
        collection = db[collection_name]
        total_docs = collection.count_documents({})

        if total_docs == 0:
            continue

        # Sample documents
        sample_docs = list(collection.aggregate([
            {'$sample': {'size': min(sample_size, total_docs)}}
        ]))

        # Analyze documents
        doc_analyses = []
        nested_paths = Counter()
        array_paths = Counter()

        for doc in sample_docs:
            analysis = analyze_document_structure(doc)
            doc_analyses.append(analysis)

            for field in analysis['nested_objects']:
                nested_paths[field] += 1
            for field in analysis['arrays']:
                array_paths[field] += 1

        # Calculate statistics
        flatness_scores = [calculate_flatness_score(analysis) for analysis in doc_analyses]
        avg_flatness = sum(flatness_scores) / len(flatness_scores)
        max_depth = max(analysis['max_depth'] for analysis in doc_analyses)

        # Count field types
        all_simple = set()
        all_nested = set()
        all_arrays = set()

        for analysis in doc_analyses:
            all_simple.update(analysis['simple_fields'])
            all_nested.update(analysis['nested_objects'])
            all_arrays.update(analysis['arrays'])

        results.append({
            'collection_name': collection_name,
            'total_documents': total_docs,
            'flatness_score': round(avg_flatness, 1),
            'max_depth': max_depth,
            'unique_simple_fields': len(all_simple),
            'unique_nested_fields': len(all_nested),
            'unique_array_fields': len(all_arrays),
            'sampled_documents': len(sample_docs),
            'top_nested_field': nested_paths.most_common(1)[0][0] if nested_paths else '',
            'top_array_field': array_paths.most_common(1)[0][0] if array_paths else ''
        })

    # Sort by flatness score (descending)
    results.sort(key=lambda x: x['flatness_score'], reverse=True)

    # Write TSV
    fieldnames = [
        'collection_name',
        'total_documents',
        'flatness_score',
        'max_depth',
        'unique_simple_fields',
        'unique_nested_fields',
        'unique_array_fields',
        'sampled_documents',
        'top_nested_field',
        'top_array_field'
    ]

    with open(output_file, 'w', newline='') as tsvfile:
        writer = csv.DictWriter(tsvfile, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        writer.writerows(results)

    print(f"✅ Created {output_file}")
    print(f"📊 Analyzed {len(results)} collections")

    # Show preview
    print(f"\n📋 Preview (top 10 flattest collections):")
    print("Collection\tDocs\tFlatness\tDepth\tSimple\tNested\tArrays")
    for result in results[:10]:
        print(f"{result['collection_name']}\t{result['total_documents']:,}\t{result['flatness_score']}\t{result['max_depth']}\t{result['unique_simple_fields']}\t{result['unique_nested_fields']}\t{result['unique_array_fields']}")


if __name__ == '__main__':
    main()
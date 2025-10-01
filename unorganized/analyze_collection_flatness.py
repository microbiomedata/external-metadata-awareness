#!/usr/bin/env python3
"""
Analyze MongoDB collections for "flatness" - detect nested objects, arrays, and complex structures.
"""

import click
from pymongo import MongoClient
from collections import defaultdict, Counter
import json
from typing import Dict, Any, List, Tuple


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
                    # Check array contents
                    if value:  # Non-empty array
                        traverse(value[0], f"{field_path}[0]", depth + 1)
                else:
                    analysis['simple_fields'].append(field_path)
        elif isinstance(obj, list):
            # Already counted as array above
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

    # Simple fields and nulls are "flat"
    flat_fields = len(analysis['simple_fields']) + len(analysis['null_fields'])

    # Penalty for depth
    depth_penalty = min(analysis['max_depth'] * 10, 50)  # Cap at 50% penalty

    base_score = (flat_fields / total_fields) * 100
    return max(0, base_score - depth_penalty)


@click.command()
@click.option('--mongo-uri', default='mongodb://localhost:27017/ncbi_metadata',
              help='MongoDB connection URI')
@click.option('--sample-size', default=100, type=int,
              help='Number of documents to sample per collection')
@click.option('--output-format', type=click.Choice(['table', 'json']), default='table',
              help='Output format')
def main(mongo_uri, sample_size, output_format):
    """Analyze MongoDB collections for structural flatness."""

    client = MongoClient(mongo_uri)
    db_name = mongo_uri.split('/')[-1]
    db = client[db_name]

    print(f"🔍 Analyzing collections in database: {db_name}")
    print(f"📊 Sample size per collection: {sample_size}")
    print("=" * 80)

    collection_analyses = {}

    # Get all collections
    collections = db.list_collection_names()

    for collection_name in sorted(collections):
        print(f"\n📁 Analyzing collection: {collection_name}")
        collection = db[collection_name]

        # Get collection stats
        total_docs = collection.count_documents({})

        if total_docs == 0:
            print(f"   ⚠️  Empty collection, skipping")
            continue

        # Sample documents
        sample_docs = list(collection.aggregate([
            {'$sample': {'size': min(sample_size, total_docs)}}
        ]))

        # Analyze each document
        doc_analyses = []
        field_paths = Counter()
        nested_paths = Counter()
        array_paths = Counter()

        for doc in sample_docs:
            analysis = analyze_document_structure(doc)
            doc_analyses.append(analysis)

            # Count field patterns
            for field in analysis['simple_fields']:
                field_paths[field] += 1
            for field in analysis['nested_objects']:
                nested_paths[field] += 1
            for field in analysis['arrays']:
                array_paths[field] += 1

        # Calculate aggregate statistics
        flatness_scores = [calculate_flatness_score(analysis) for analysis in doc_analyses]
        avg_flatness = sum(flatness_scores) / len(flatness_scores)
        max_depth = max(analysis['max_depth'] for analysis in doc_analyses)

        # Count unique field patterns
        total_simple_fields = len(field_paths)
        total_nested_fields = len(nested_paths)
        total_array_fields = len(array_paths)

        collection_analysis = {
            'collection_name': collection_name,
            'total_documents': total_docs,
            'sampled_documents': len(sample_docs),
            'flatness_score': round(avg_flatness, 1),
            'max_depth': max_depth,
            'unique_simple_fields': total_simple_fields,
            'unique_nested_fields': total_nested_fields,
            'unique_array_fields': total_array_fields,
            'most_common_nested': nested_paths.most_common(5),
            'most_common_arrays': array_paths.most_common(5)
        }

        collection_analyses[collection_name] = collection_analysis

        if output_format == 'table':
            print(f"   📊 Total documents: {total_docs:,}")
            print(f"   🎯 Flatness score: {avg_flatness:.1f}/100")
            print(f"   📏 Max nesting depth: {max_depth}")
            print(f"   🔧 Simple fields: {total_simple_fields}")
            print(f"   🏗️  Nested fields: {total_nested_fields}")
            print(f"   📋 Array fields: {total_array_fields}")

            if nested_paths:
                print(f"   🏗️  Top nested paths:")
                for path, count in nested_paths.most_common(3):
                    print(f"      {path} ({count}/{len(sample_docs)} docs)")

            if array_paths:
                print(f"   📋 Top array paths:")
                for path, count in array_paths.most_common(3):
                    print(f"      {path} ({count}/{len(sample_docs)} docs)")

    print("\n" + "=" * 80)
    print("📈 FLATNESS SUMMARY (sorted by flatness score)")
    print("=" * 80)

    if output_format == 'table':
        # Sort by flatness score
        sorted_collections = sorted(collection_analyses.values(),
                                  key=lambda x: x['flatness_score'], reverse=True)

        print(f"{'Collection':<35} {'Docs':<12} {'Flatness':<9} {'Depth':<6} {'Simple':<7} {'Nested':<7} {'Arrays':<7}")
        print("-" * 80)

        for analysis in sorted_collections:
            print(f"{analysis['collection_name']:<35} "
                  f"{analysis['total_documents']:<12,} "
                  f"{analysis['flatness_score']:<9} "
                  f"{analysis['max_depth']:<6} "
                  f"{analysis['unique_simple_fields']:<7} "
                  f"{analysis['unique_nested_fields']:<7} "
                  f"{analysis['unique_array_fields']:<7}")

    elif output_format == 'json':
        print(json.dumps(collection_analyses, indent=2))


if __name__ == '__main__':
    main()
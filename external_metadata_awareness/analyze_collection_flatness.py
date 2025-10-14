#!/usr/bin/env python3
"""
Analyze MongoDB collection structure complexity.

Calculates flatness scores (0-100) where:
- 100 = completely flat (no nesting/arrays)
- 0 = deeply nested structures

Useful for identifying which collections can be exported to tabular formats.
"""

import click
import csv
import json
import logging
import time
from collections import Counter
from typing import Dict, Any, List
from pymongo import MongoClient

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def analyze_document(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze single document structure."""
    analysis = {
        'nested_objects': [],
        'arrays': [],
        'simple_fields': [],
        'null_fields': [],
        'max_depth': 0
    }

    def traverse(obj, path="", depth=0):
        analysis['max_depth'] = max(analysis['max_depth'], depth)

        if isinstance(obj, dict):
            for key, value in obj.items():
                field_path = f"{path}.{key}" if path else key

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
        elif isinstance(obj, list) and obj:
            traverse(obj[0], f"{path}[0]", depth + 1)

    traverse(doc)
    return analysis


def calculate_flatness(analysis: Dict[str, Any]) -> float:
    """
    Calculate flatness score (0-100).

    Penalties:
    - Nested objects/arrays reduce score
    - Deep nesting reduces score further
    """
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
@click.option('--sample-percent', default=1.0, type=float,
              help='Percentage of documents to sample (default: 1.0%)')
@click.option('--min-sample-size', default=1000, type=int,
              help='Minimum documents to sample per collection (default: 1000)')
@click.option('--max-sample-size', default=100000, type=int,
              help='Maximum documents to sample per collection (default: 100000)')
@click.option('--output-format', type=click.Choice(['table', 'tsv', 'json']),
              default='table', help='Output format')
@click.option('--output-file', type=click.Path(),
              help='Output file (for tsv/json formats)')
@click.option('--collection', help='Analyze single collection (default: all)')
@click.option('--verbose', is_flag=True, help='Show detailed analysis')
def main(mongo_uri, sample_percent, min_sample_size, max_sample_size,
         output_format, output_file, collection, verbose):
    """Analyze MongoDB collection flatness for export compatibility."""

    client = MongoClient(mongo_uri)
    db_name = mongo_uri.split('/')[-1].split('?')[0]
    db = client[db_name]

    if verbose:
        logger.info(f"Database: {db_name}")
        logger.info(f"Sampling: {sample_percent}% (min: {min_sample_size}, max: {max_sample_size})")

    # Get collections to analyze
    collections = [collection] if collection else sorted(db.list_collection_names())
    results = []

    for idx, coll_name in enumerate(collections):
        coll_start = time.time()
        logger.info(f"[{idx+1}/{len(collections)}] Processing {coll_name}...")

        coll = db[coll_name]

        # Use fast approximate count (metadata-based, not full scan)
        total_docs = coll.estimated_document_count()

        if total_docs == 0:
            logger.info(f"  Skipping (empty)")
            continue

        # Calculate adaptive sample size
        desired_sample = max(int(total_docs * sample_percent / 100), min_sample_size)
        actual_sample = min(desired_sample, max_sample_size, total_docs)

        logger.info(f"  Documents: ~{total_docs:,}")
        logger.info(f"  Sampling {actual_sample:,} documents ({actual_sample/total_docs*100:.2f}%)...")

        # Sample and analyze
        sample_start = time.time()
        sample_docs = list(coll.aggregate([
            {'$sample': {'size': actual_sample}}
        ]))
        sample_elapsed = time.time() - sample_start

        logger.info(f"  Analyzing structure (sampled in {sample_elapsed:.1f}s)...")
        analyze_start = time.time()

        doc_analyses = [analyze_document(doc) for doc in sample_docs]

        # Aggregate statistics
        flatness_scores = [calculate_flatness(a) for a in doc_analyses]
        avg_flatness = sum(flatness_scores) / len(flatness_scores)
        max_depth = max(a['max_depth'] for a in doc_analyses)

        # Count unique field types
        all_simple = set()
        all_nested = set()
        all_arrays = set()
        nested_counter = Counter()
        array_counter = Counter()

        for analysis in doc_analyses:
            all_simple.update(analysis['simple_fields'])
            all_nested.update(analysis['nested_objects'])
            all_arrays.update(analysis['arrays'])

            for field in analysis['nested_objects']:
                nested_counter[field] += 1
            for field in analysis['arrays']:
                array_counter[field] += 1

        result = {
            'collection_name': coll_name,
            'total_documents': total_docs,
            'flatness_score': round(avg_flatness, 1),
            'max_depth': max_depth,
            'unique_simple_fields': len(all_simple),
            'unique_nested_fields': len(all_nested),
            'unique_array_fields': len(all_arrays),
            'sampled_documents': len(sample_docs),
            'top_nested_field': nested_counter.most_common(1)[0][0] if nested_counter else '',
            'top_array_field': array_counter.most_common(1)[0][0] if array_counter else ''
        }

        results.append(result)

        analyze_elapsed = time.time() - analyze_start
        coll_elapsed = time.time() - coll_start
        logger.info(f"  ✓ Flatness: {avg_flatness:.1f}/100, Depth: {max_depth} "
                   f"(analyzed in {analyze_elapsed:.1f}s, total {coll_elapsed:.1f}s)")

        if verbose and output_format == 'table':
            logger.info(f"    Fields: {len(all_simple)} simple, {len(all_nested)} nested, {len(all_arrays)} arrays")
            if nested_counter:
                logger.info(f"    Top nested: {nested_counter.most_common(1)[0][0]}")

    # Sort by flatness
    results.sort(key=lambda x: x['flatness_score'], reverse=True)

    # Output
    if output_format == 'json':
        output = json.dumps(results, indent=2)
        if output_file:
            with open(output_file, 'w') as f:
                f.write(output)
            logger.info(f"✅ Wrote {output_file}")
        else:
            print(output)

    elif output_format == 'tsv':
        fieldnames = ['collection_name', 'total_documents', 'flatness_score',
                     'max_depth', 'unique_simple_fields', 'unique_nested_fields',
                     'unique_array_fields', 'sampled_documents',
                     'top_nested_field', 'top_array_field']

        if not output_file:
            output_file = 'collection_flatness.tsv'

        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
            writer.writeheader()
            writer.writerows(results)

        logger.info(f"✅ Wrote {output_file}")

    else:  # table
        logger.info(f"\n{'Collection':<35} {'Docs':>12} {'Flatness':>8} {'Depth':>5} {'Simple':>6} {'Nested':>6} {'Arrays':>6}")
        logger.info("-" * 90)
        for r in results:
            logger.info(f"{r['collection_name']:<35} {r['total_documents']:>12,} "
                       f"{r['flatness_score']:>8} {r['max_depth']:>5} "
                       f"{r['unique_simple_fields']:>6} {r['unique_nested_fields']:>6} "
                       f"{r['unique_array_fields']:>6}")


if __name__ == '__main__':
    main()

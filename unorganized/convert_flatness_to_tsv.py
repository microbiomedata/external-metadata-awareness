#!/usr/bin/env python3
"""
Convert collection flatness analysis JSON to TSV format.
"""

import json
import csv
import sys


def main():
    # Read the JSON file
    with open('collection_flatness_analysis.json', 'r') as f:
        data = json.load(f)

    # Prepare TSV output
    with open('collection_flatness_analysis.tsv', 'w', newline='') as tsvfile:
        # Define columns
        fieldnames = [
            'collection_name',
            'total_documents',
            'flatness_score',
            'max_depth',
            'unique_simple_fields',
            'unique_nested_fields',
            'unique_array_fields',
            'sampled_documents'
        ]

        writer = csv.DictWriter(tsvfile, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()

        # Sort collections by flatness score (descending)
        collections = sorted(data.values(),
                           key=lambda x: x['flatness_score'],
                           reverse=True)

        # Write each collection
        for collection in collections:
            # Extract only the fields we want for TSV
            row = {field: collection[field] for field in fieldnames}
            writer.writerow(row)

    print("✅ Created collection_flatness_analysis.tsv")

    # Also show preview
    print("\n📋 Preview of TSV (first 10 rows):")
    with open('collection_flatness_analysis.tsv', 'r') as f:
        lines = f.readlines()
        for i, line in enumerate(lines[:11]):  # Header + 10 rows
            print(f"{i:2}: {line.rstrip()}")


if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
Analyze coverage of NMDC Biosample schema slots in flattened CSV export.

This script:
1. Fetches the NMDC LinkML schema from GitHub
2. Extracts Biosample class slots
3. Checks which slots appear as exact CSV column headers or with known flattening suffixes
4. Reports missing slots and population rates based on these matched columns
"""

import csv
import json
import logging
from pathlib import Path
from typing import List

import click
import requests
import yaml

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

NMDC_SCHEMA_URL = "https://raw.githubusercontent.com/microbiomedata/nmdc-schema/main/nmdc_schema/nmdc_materialized_patterns.yaml"

COMMON_SUFFIXES = [
    '_has_raw_value', '_has_numeric_value', '_has_unit',
    '_term_id', '_term_name', '_canonical_label',
    '_normalized_curie', '_is_obsolete', '_label_match',
    '_has_maximum_numeric_value', '_has_minimum_numeric_value'
]


def fetch_nmdc_schema(schema_url: str = NMDC_SCHEMA_URL) -> dict:
    """Fetch NMDC schema from GitHub."""
    logger.info("Fetching NMDC LinkML schema...")

    response = requests.get(schema_url, timeout=30)
    response.raise_for_status()

    schema = yaml.safe_load(response.text)
    logger.info("✓ Successfully loaded schema")
    return schema


def get_biosample_slots(schema: dict) -> List[str]:
    """Extract Biosample slot names from schema."""
    logger.info("Extracting Biosample slots...")

    biosample_class = schema['classes']['Biosample']
    slots = biosample_class['slots']

    logger.info(f"Found {len(slots)} slots in Biosample class")
    return slots


def get_csv_columns(csv_path: Path) -> List[str]:
    """Extract column headers from CSV file."""
    logger.info(f"Reading CSV columns from {csv_path}...")

    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        headers = next(reader)

    logger.info(f"Found {len(headers)} columns in CSV")
    return headers


def find_slot_matches(slot: str, csv_columns: List[str]) -> List[str]:
    """Find CSV columns that match the slot name exactly or with known flattening suffixes."""
    matches = []
    for col in csv_columns:
        # Exact match
        if col == slot:
            matches.append(col)
        # Match with known suffixes
        else:
            for suffix in COMMON_SUFFIXES:
                if col == slot + suffix:
                    matches.append(col)
                    break

    return matches


def analyze_all_slot_populations(csv_path: Path, slot_to_columns: dict) -> dict:
    """Calculate population rates for all slots in a single CSV pass."""
    if not slot_to_columns:
        return {}

    # Initialize counters
    slot_populated_counts = {slot: 0 for slot in slot_to_columns}
    total_rows = 0

    logger.info("  Reading CSV for population analysis (single pass)...")
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)

        for row in reader:
            total_rows += 1
            if total_rows % 10000 == 0:
                logger.info(f"    Processed {total_rows} rows...")

            # Check each slot's matching columns
            for slot, columns in slot_to_columns.items():
                for col in columns:
                    if col in row and row[col] and row[col].strip():
                        slot_populated_counts[slot] += 1
                        break  # Only count once per slot per row

    # Calculate percentages
    if total_rows == 0:
        return {slot: 0.0 for slot in slot_to_columns}

    return {slot: (count / total_rows * 100) for slot, count in slot_populated_counts.items()}


def analyze_biosample_coverage(csv_path: Path, output_path: Path = None, schema_url: str = NMDC_SCHEMA_URL) -> dict:
    """Main analysis function."""
    logger.info("NMDC Biosample Schema Coverage Analysis")
    logger.info("=" * 50)

    # Get data
    schema = fetch_nmdc_schema(schema_url)
    biosample_slots = get_biosample_slots(schema)
    csv_columns = get_csv_columns(csv_path)

    # Check coverage - precompute slot→columns mapping
    logger.info("Analyzing slot coverage...")
    missing_slots = []
    slot_to_columns = {}

    for slot in sorted(biosample_slots):
        matches = find_slot_matches(slot, csv_columns)
        if matches:
            slot_to_columns[slot] = matches
        else:
            missing_slots.append(slot)

    # Analyze population rates in single pass
    logger.info("Analyzing population rates...")
    slot_populations = analyze_all_slot_populations(csv_path, slot_to_columns)

    # Build represented_slots list
    represented_slots = [(slot, slot_to_columns[slot], slot_populations[slot])
                         for slot in slot_to_columns]

    # Results
    total_slots = len(biosample_slots)
    represented_count = len(represented_slots)
    missing_count = len(missing_slots)

    logger.info(f"\nSUMMARY:")
    logger.info(f"Total Biosample slots: {total_slots}")
    logger.info(f"Slots with CSV matches: {represented_count}")
    logger.info(f"Slots missing from CSV: {missing_count}")
    logger.info(f"Coverage: {represented_count / total_slots * 100:.1f}%")

    if missing_slots:
        logger.info(f"\nMISSING SLOTS ({missing_count}):")
        for slot in missing_slots:
            logger.info(f"  {slot}")

    if represented_slots:
        logger.info(f"\nREPRESENTED SLOTS WITH POPULATION RATES ({represented_count}):")
        # Sort by population rate (descending)
        sorted_slots = sorted(represented_slots, key=lambda x: x[2], reverse=True)

        for slot, matches, pop_rate in sorted_slots:
            match_list = ', '.join(matches[:3])  # Show first 3 matches
            if len(matches) > 3:
                match_list += f" (and {len(matches) - 3} more)"
            logger.info(f"  {slot}: {pop_rate:.1f}% → {match_list}")

    # Show top and bottom populated slots
    if slot_populations:
        logger.info(f"\nTOP 10 MOST POPULATED SLOTS:")
        top_slots = sorted(slot_populations.items(), key=lambda x: x[1], reverse=True)[:10]
        for slot, pop_rate in top_slots:
            logger.info(f"  {slot}: {pop_rate:.1f}%")

        logger.info(f"\nTOP 10 LEAST POPULATED SLOTS (>0%):")
        bottom_slots = [item for item in sorted(slot_populations.items(), key=lambda x: x[1]) if item[1] > 0][:10]
        for slot, pop_rate in bottom_slots:
            logger.info(f"  {slot}: {pop_rate:.1f}%")

    # Build results
    results = {
        'csv_path': str(csv_path),
        'total_slots': total_slots,
        'represented_count': represented_count,
        'missing_count': missing_count,
        'coverage_percent': represented_count / total_slots * 100,
        'missing_slots': missing_slots,
        'represented_slots': {slot: {'matches': matches, 'population_rate': pop_rate}
                             for slot, matches, pop_rate in represented_slots},
        'slot_populations': slot_populations
    }

    # Save results
    if output_path is None:
        output_path = csv_path.parent / 'biosample_coverage_results.json'

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    logger.info(f"\nResults saved to: {output_path}")
    return results


@click.command()
@click.option('--csv-file', '-c', type=click.Path(exists=True, path_type=Path), required=True,
              help='Path to flattened NMDC biosample CSV file')
@click.option('--output-file', '-o', type=click.Path(path_type=Path), default=None,
              help='Path for output JSON results (default: <csv_dir>/biosample_coverage_results.json)')
@click.option('--schema-url', '-s', type=str, default=NMDC_SCHEMA_URL,
              help='URL to NMDC LinkML schema YAML')
def main(csv_file: Path, output_file: Path, schema_url: str):
    """
    Analyze coverage of NMDC Biosample schema slots in flattened CSV export.

    Fetches the NMDC LinkML schema, extracts Biosample class slots, and checks
    which slots appear in the CSV column headers. Reports missing slots and
    population rates for represented slots.
    """
    analyze_biosample_coverage(csv_file, output_file, schema_url)


if __name__ == "__main__":
    main()

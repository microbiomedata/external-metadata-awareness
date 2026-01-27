#!/usr/bin/env python3
"""
Analyze coverage of NMDC Biosample schema slots in flattened CSV export.

This script:
1. Fetches the NMDC LinkML schema from GitHub
2. Extracts Biosample class slots
3. Checks which slots appear as substrings in CSV column headers
4. Reports missing slots and population rates
"""

import csv
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple

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


def analyze_slot_population(csv_path: Path, slot: str, matching_columns: List[str]) -> float:
    """Calculate the percentage of rows where at least one matching column is populated."""
    if not matching_columns:
        return 0.0

    populated_rows = 0
    total_rows = 0

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)

        for row in reader:
            total_rows += 1

            # Check if any of the matching columns has a non-empty value
            has_value = False
            for col in matching_columns:
                if col in row and row[col] and row[col].strip():
                    has_value = True
                    break

            if has_value:
                populated_rows += 1

    return (populated_rows / total_rows * 100) if total_rows > 0 else 0.0


def analyze_biosample_coverage(csv_path: Path, output_path: Path = None) -> dict:
    """Main analysis function."""
    logger.info("NMDC Biosample Schema Coverage Analysis")
    logger.info("=" * 50)

    # Get data
    schema = fetch_nmdc_schema()
    biosample_slots = get_biosample_slots(schema)
    csv_columns = get_csv_columns(csv_path)

    # Check coverage and analyze population
    logger.info("Analyzing slot coverage and population rates...")
    missing_slots = []
    represented_slots = []
    slot_populations = {}

    for i, slot in enumerate(sorted(biosample_slots), 1):
        if i % 50 == 0:
            logger.info(f"  Processed {i}/{len(biosample_slots)} slots...")

        matches = find_slot_matches(slot, csv_columns)
        if matches:
            population_rate = analyze_slot_population(csv_path, slot, matches)
            represented_slots.append((slot, matches, population_rate))
            slot_populations[slot] = population_rate
        else:
            missing_slots.append(slot)

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
    analyze_biosample_coverage(csv_file, output_file)


if __name__ == "__main__":
    main()

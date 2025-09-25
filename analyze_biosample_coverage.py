#!/usr/bin/env python3
"""
Analyze coverage of NMDC Biosample schema slots in flattened CSV export.

This script:
1. Fetches the NMDC LinkML schema from GitHub
2. Extracts Biosample class slots
3. Checks which slots appear as substrings in CSV column headers
4. Reports missing slots
"""

import csv
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import requests
import yaml


def fetch_nmdc_schema() -> dict:
    """Fetch NMDC schema from GitHub."""
    print("Fetching NMDC LinkML schema...")
    
    url = "https://raw.githubusercontent.com/microbiomedata/nmdc-schema/main/nmdc_schema/nmdc_materialized_patterns.yaml"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    
    schema = yaml.safe_load(response.text)
    print("✓ Successfully loaded schema")
    return schema


def get_biosample_slots(schema: dict) -> List[str]:
    """Extract Biosample slot names from schema."""
    print("Extracting Biosample slots...")
    
    biosample_class = schema['classes']['Biosample']
    slots = biosample_class['slots']
    
    print(f"Found {len(slots)} slots in Biosample class")
    return slots


def get_csv_columns(csv_path: Path) -> List[str]:
    """Extract column headers from CSV file."""
    print(f"Reading CSV columns from {csv_path}...")
    
    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        headers = next(reader)
    
    print(f"Found {len(headers)} columns in CSV")
    return headers


def find_slot_matches(slot: str, csv_columns: List[str]) -> List[str]:
    """Find CSV columns that match the slot name exactly or with known flattening suffixes."""
    COMMON_SUFFIXES = [
        '_has_raw_value', '_has_numeric_value', '_has_unit', 
        '_term_id', '_term_name', '_canonical_label', 
        '_normalized_curie', '_is_obsolete', '_label_match',
        '_has_maximum_numeric_value', '_has_minimum_numeric_value'
    ]
    
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


def analyze_biosample_coverage(csv_path: Path) -> None:
    """Main analysis function."""
    print("NMDC Biosample Schema Coverage Analysis")
    print("=" * 50)
    
    # Get data
    schema = fetch_nmdc_schema()
    biosample_slots = get_biosample_slots(schema)
    csv_columns = get_csv_columns(csv_path)
    
    # Check coverage and analyze population
    print("Analyzing slot coverage and population rates...")
    missing_slots = []
    represented_slots = []
    slot_populations = {}
    
    for i, slot in enumerate(sorted(biosample_slots), 1):
        if i % 50 == 0:
            print(f"  Processed {i}/{len(biosample_slots)} slots...")
            
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
    
    print(f"\nSUMMARY:")
    print(f"Total Biosample slots: {total_slots}")
    print(f"Slots with CSV matches: {represented_count}")
    print(f"Slots missing from CSV: {missing_count}")
    print(f"Coverage: {represented_count / total_slots * 100:.1f}%")
    
    if missing_slots:
        print(f"\nMISSING SLOTS ({missing_count}):")
        for slot in missing_slots:
            print(f"  {slot}")
    
    if represented_slots:
        print(f"\nREPRESENTED SLOTS WITH POPULATION RATES ({represented_count}):")
        # Sort by population rate (descending)
        sorted_slots = sorted(represented_slots, key=lambda x: x[2], reverse=True)
        
        for slot, matches, pop_rate in sorted_slots:
            match_list = ', '.join(matches[:3])  # Show first 3 matches
            if len(matches) > 3:
                match_list += f" (and {len(matches) - 3} more)"
            print(f"  {slot}: {pop_rate:.1f}% → {match_list}")
    
    # Show top and bottom populated slots
    if slot_populations:
        print(f"\nTOP 10 MOST POPULATED SLOTS:")
        top_slots = sorted(slot_populations.items(), key=lambda x: x[1], reverse=True)[:10]
        for slot, pop_rate in top_slots:
            print(f"  {slot}: {pop_rate:.1f}%")
        
        print(f"\nTOP 10 LEAST POPULATED SLOTS (>0%):")
        bottom_slots = [item for item in sorted(slot_populations.items(), key=lambda x: x[1]) if item[1] > 0][:10]
        for slot, pop_rate in bottom_slots:
            print(f"  {slot}: {pop_rate:.1f}%")
    
    # Save results
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
    
    results_path = csv_path.parent / 'biosample_coverage_results.json'
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {results_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python analyze_biosample_coverage.py <path_to_csv>")
        sys.exit(1)
    
    csv_path = Path(sys.argv[1])
    if not csv_path.exists():
        print(f"CSV file not found: {csv_path}")
        sys.exit(1)
    
    analyze_biosample_coverage(csv_path)
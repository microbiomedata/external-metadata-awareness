#!/usr/bin/env python3
"""
Prioritize measurement targets by combining discovery results.

Combines fields with authoritative units and fields with numeric content
into a prioritized list for measurement processing.
"""

import json
import click
from typing import Dict, List, Set
from dataclasses import dataclass


@dataclass
class MeasurementField:
    harmonized_name: str
    count: int
    has_authoritative_unit: bool = False
    unit_coverage_percent: float = 0.0
    sample_values: List[str] = None
    units_found: List[str] = None
    priority_score: float = 0.0

    def __post_init__(self):
        if self.sample_values is None:
            self.sample_values = []
        if self.units_found is None:
            self.units_found = []


def load_units_file(filepath: str) -> Dict[str, MeasurementField]:
    """Load fields with authoritative units."""
    fields = {}
    
    with open(filepath, 'r') as f:
        for line in f:
            if line.strip():
                doc = json.loads(line)
                
                # Handle both possible structures
                if 'harmonized_name' in doc:
                    name = doc['harmonized_name']
                    unit = doc['unit']
                else:
                    # Fallback: unit documents without harmonized_name
                    # Skip these for now, they need to be fixed in the aggregation
                    continue
                
                # If field already exists, combine counts
                if name in fields:
                    fields[name].count += doc['count']
                    fields[name].sample_values.extend(doc.get('sample_values', []))
                    fields[name].units_found.extend([unit])
                else:
                    fields[name] = MeasurementField(
                        harmonized_name=name,
                        count=doc['count'],
                        has_authoritative_unit=True,
                        unit_coverage_percent=100.0,  # Has units by definition
                        sample_values=doc.get('sample_values', []),
                        units_found=[unit]
                    )
    
    return fields


def load_numeric_file(filepath: str) -> Dict[str, MeasurementField]:
    """Load fields with numeric content."""
    fields = {}
    
    with open(filepath, 'r') as f:
        for line in f:
            if line.strip():
                doc = json.loads(line)
                name = doc['harmonized_name']
                
                fields[name] = MeasurementField(
                    harmonized_name=name,
                    count=doc['count'],
                    has_authoritative_unit=False,
                    unit_coverage_percent=doc.get('unit_coverage_percent', 0.0),
                    sample_values=doc.get('sample_values', []),
                    units_found=doc.get('units_found', [])
                )
    
    return fields


def calculate_priority_score(field: MeasurementField) -> float:
    """Calculate priority score for measurement field."""
    # Base score from frequency (log scale to avoid huge numbers dominating)
    import math
    frequency_score = math.log10(field.count + 1)
    
    # Bonus for having authoritative units
    unit_bonus = 2.0 if field.has_authoritative_unit else 0.0
    
    # Bonus for high unit coverage in numeric fields
    coverage_bonus = field.unit_coverage_percent / 100.0
    
    # Penalty for very low counts (even though we filter, rank low counts lower)
    count_penalty = 0.0 if field.count >= 1000 else -0.5
    
    return frequency_score + unit_bonus + coverage_bonus + count_penalty


def merge_field_lists(units_fields: Dict[str, MeasurementField], 
                     numeric_fields: Dict[str, MeasurementField]) -> Dict[str, MeasurementField]:
    """Merge unit and numeric field discoveries."""
    merged = {}
    
    # Start with all unit fields (these are high priority)
    for name, field in units_fields.items():
        merged[name] = field
    
    # Add numeric fields, but enhance existing entries if they already exist
    for name, numeric_field in numeric_fields.items():
        if name in merged:
            # Field has both units and numeric content - enhance existing entry
            existing = merged[name]
            # Use the higher count (should be similar but numeric might be more comprehensive)
            existing.count = max(existing.count, numeric_field.count)
            # Keep authoritative unit status
            existing.has_authoritative_unit = True
            # Add any additional sample values
            existing.sample_values.extend(numeric_field.sample_values)
            # Remove duplicates but preserve order
            existing.sample_values = list(dict.fromkeys(existing.sample_values))
        else:
            # New field from numeric discovery
            merged[name] = numeric_field
    
    return merged


@click.command()
@click.option('--units-file', required=True, help='JSON file with fields that have authoritative units')
@click.option('--numeric-file', required=True, help='JSON file with fields that have numeric content')
@click.option('--output-file', required=True, help='Output JSON file with prioritized measurement fields')
@click.option('--min-count', default=100, type=int, help='Minimum occurrence count for inclusion')
@click.option('--max-fields', default=None, type=int, help='Maximum number of fields to include (top N)')
@click.option('--verbose', is_flag=True, help='Verbose output')
def main(units_file: str, numeric_file: str, output_file: str, min_count: int, max_fields: int, verbose: bool):
    """Prioritize measurement targets from discovery checkpoint files."""
    
    if verbose:
        click.echo(f"Loading units file: {units_file}")
    units_fields = load_units_file(units_file)
    
    if verbose:
        click.echo(f"Loading numeric file: {numeric_file}")
    numeric_fields = load_numeric_file(numeric_file)
    
    if verbose:
        click.echo(f"Found {len(units_fields)} fields with units")
        click.echo(f"Found {len(numeric_fields)} fields with numeric content")
    
    # Merge the two discovery results
    merged_fields = merge_field_lists(units_fields, numeric_fields)
    
    if verbose:
        click.echo(f"Merged to {len(merged_fields)} unique fields")
    
    # Filter by minimum count
    filtered_fields = {name: field for name, field in merged_fields.items() 
                      if field.count >= min_count}
    
    if verbose:
        click.echo(f"After min-count filtering ({min_count}): {len(filtered_fields)} fields")
    
    # Calculate priority scores
    for field in filtered_fields.values():
        field.priority_score = calculate_priority_score(field)
    
    # Sort by priority score (descending)
    prioritized_fields = sorted(filtered_fields.values(), 
                               key=lambda f: f.priority_score, reverse=True)
    
    # Apply max fields limit if specified
    if max_fields and len(prioritized_fields) > max_fields:
        prioritized_fields = prioritized_fields[:max_fields]
        if verbose:
            click.echo(f"Limited to top {max_fields} fields")
    
    # Output summary statistics
    units_count = sum(1 for f in prioritized_fields if f.has_authoritative_unit)
    high_coverage_count = sum(1 for f in prioritized_fields if f.unit_coverage_percent > 50)
    
    if verbose:
        click.echo(f"\nFinal prioritized list: {len(prioritized_fields)} fields")
        click.echo(f"  - With authoritative units: {units_count}")
        click.echo(f"  - With >50% unit coverage: {high_coverage_count}")
        click.echo(f"  - Top field: {prioritized_fields[0].harmonized_name} (score: {prioritized_fields[0].priority_score:.2f})")
        if len(prioritized_fields) > 1:
            click.echo(f"  - Lowest field: {prioritized_fields[-1].harmonized_name} (score: {prioritized_fields[-1].priority_score:.2f})")
    
    # Write output file
    output_data = []
    for field in prioritized_fields:
        output_data.append({
            'harmonized_name': field.harmonized_name,
            'count': field.count,
            'has_authoritative_unit': field.has_authoritative_unit,
            'unit_coverage_percent': field.unit_coverage_percent,
            'priority_score': field.priority_score,
            'sample_values': field.sample_values[:10],  # Limit for file size
            'units_found': list(set(field.units_found))  # Deduplicate
        })
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    if verbose:
        click.echo(f"Written prioritized fields to: {output_file}")


if __name__ == '__main__':
    main()
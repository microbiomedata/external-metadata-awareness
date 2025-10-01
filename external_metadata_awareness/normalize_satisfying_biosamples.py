"""
Normalize biosample date and coordinate formats in satisfying biosamples CSV.

This script processes the satisfying biosamples CSV export to normalize:
1. collection_date to ISO 8601 format (YYYY-MM-DD) or NULL
2. lat_lon to decimal degrees format (+/- DD.dddd)

Uses dateparser for robust date parsing and geopy for coordinate conversion.
Optimized to process unique values first, then map back to full dataset.
"""

import re
from pathlib import Path
from typing import Optional

import click
import dateparser
import pandas as pd
from geopy.point import Point


def is_valid_iso_date(date_str: str) -> bool:
    """
    Check if string is already in YYYY-MM-DD format with valid ranges.

    Args:
        date_str: String to check

    Returns:
        True if valid YYYY-MM-DD with plausible year/month/day
    """
    pattern = r'^(\d{4})-(\d{2})-(\d{2})$'
    match = re.match(pattern, date_str)
    if not match:
        return False

    year = int(match.group(1))
    month = int(match.group(2))
    day = int(match.group(3))

    # Validate ranges
    if year < 2000 or year > 2050:
        return False
    if month < 1 or month > 12:
        return False
    if day < 1 or day > 31:
        return False

    return True


def normalize_date(date_str: Optional[str]) -> Optional[str]:
    """
    Normalize date string to YYYY-MM-DD format using dateparser.

    Args:
        date_str: Input date string in various formats

    Returns:
        Date in YYYY-MM-DD format, or None if invalid/missing
    """
    if pd.isna(date_str) or not date_str or str(date_str).strip() == "":
        return None

    date_str = str(date_str).strip()

    # Fast path: already valid ISO date
    if is_valid_iso_date(date_str):
        return date_str

    try:
        # Use dateparser for robust, messy format handling
        parsed = dateparser.parse(date_str)
        if parsed is None:
            return None

        # Validate year range
        if parsed.year < 2000 or parsed.year > 2050:
            return None

        return parsed.strftime('%Y-%m-%d')
    except Exception:
        return None


def normalize_coordinate(coord_str: Optional[str]) -> tuple[Optional[float], Optional[float]]:
    """
    Normalize coordinate string to decimal degrees format using geopy.

    Handles formats like:
    - "40.7128 N 74.0060 W"
    - "40.7128, -74.0060"
    - "40°26'46"N 79°58'56"W"
    - Plain decimal degrees

    Args:
        coord_str: Input coordinate string

    Returns:
        Tuple of (latitude, longitude) as signed decimal degrees to 4 places,
        or (None, None) if invalid
    """
    if pd.isna(coord_str) or not coord_str or str(coord_str).strip() == "":
        return None, None

    coord_str = str(coord_str).strip()

    try:
        # Use geopy.point.Point for flexible coordinate parsing
        point = Point(coord_str)
        lat = round(point.latitude, 4)
        lon = round(point.longitude, 4)

        # Validate ranges
        if -90 <= lat <= 90 and -180 <= lon <= 180:
            return lat, lon
        return None, None
    except Exception:
        return None, None


@click.command()
@click.option(
    '--input-file',
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help='Input CSV file path (e.g., local/satisfying_biosamples.csv)'
)
@click.option(
    '--output-file',
    type=click.Path(path_type=Path),
    required=True,
    help='Output CSV file path (e.g., local/satisfying_biosamples_normalized.csv)'
)
@click.option(
    '--report-failures/--no-report-failures',
    default=False,
    help='Print samples that failed normalization to stderr'
)
@click.option(
    '--progress-interval',
    type=int,
    default=10,
    help='Report progress every N unique values processed (default: 10)'
)
def normalize_biosamples(
    input_file: Path,
    output_file: Path,
    report_failures: bool,
    progress_interval: int
) -> None:
    """
    Normalize biosample dates and coordinates in CSV export.

    Reads the satisfying biosamples CSV, normalizes date and coordinate formats,
    and writes the result to a new CSV file.

    Optimization: Processes unique values first, then maps back to full dataset.
    """
    click.echo(f"Reading input file: {input_file}")

    # Read CSV
    df = pd.read_csv(input_file)
    original_count = len(df)
    click.echo(f"Loaded {original_count:,} biosamples")

    # Track normalization statistics
    date_normalized = 0
    date_failed = 0
    coord_normalized = 0
    coord_failed = 0
    failures = []

    # =========================================================================
    # Normalize dates using unique value mapping
    # =========================================================================
    click.echo("\nNormalizing collection_date to YYYY-MM-DD format...")
    if 'collection_date' in df.columns:
        # Get unique values and sort alphabetically
        unique_dates = sorted(df['collection_date'].unique(), key=lambda x: str(x))
        total_unique = len(unique_dates)
        click.echo(f"  Found {total_unique:,} unique date values")

        # Process each unique value
        date_map = {}
        for idx, date_val in enumerate(unique_dates, start=1):
            if idx % progress_interval == 0:
                click.echo(f"  Processing date {idx}/{total_unique}: '{date_val}'")

            normalized = normalize_date(date_val)
            date_map[date_val] = normalized

        # Map back to dataframe
        click.echo(f"  Mapping normalized dates back to {original_count:,} rows...")
        df['collection_date'] = df['collection_date'].map(date_map)

        # Count successes/failures
        date_normalized = df['collection_date'].notna().sum()
        date_failed = df['collection_date'].isna().sum()

        if report_failures:
            for orig_val, norm_val in date_map.items():
                if norm_val is None and pd.notna(orig_val) and str(orig_val).strip():
                    failures.append(f"Date failed: '{orig_val}'")

    # =========================================================================
    # Normalize coordinates using unique value mapping
    # =========================================================================
    click.echo("\nNormalizing lat_lon to separate latitude and longitude columns (+/- DD.dddd)...")
    if 'lat_lon' in df.columns:
        # Get unique values and sort alphabetically
        unique_coords = sorted(df['lat_lon'].unique(), key=lambda x: str(x))
        total_unique = len(unique_coords)
        click.echo(f"  Found {total_unique:,} unique coordinate values")

        # Process each unique value
        coord_map = {}
        for idx, coord_val in enumerate(unique_coords, start=1):
            if idx % progress_interval == 0:
                click.echo(f"  Processing coordinate {idx}/{total_unique}: '{coord_val}'")

            lat, lon = normalize_coordinate(coord_val)
            coord_map[coord_val] = (lat, lon)

        # Map back to dataframe - create separate columns
        click.echo(f"  Mapping normalized coordinates back to {original_count:,} rows...")
        df['latitude'] = df['lat_lon'].map(lambda x: coord_map.get(x, (None, None))[0])
        df['longitude'] = df['lat_lon'].map(lambda x: coord_map.get(x, (None, None))[1])

        # Count successes/failures
        coord_normalized = df['latitude'].notna().sum()
        coord_failed = df['latitude'].isna().sum()

        if report_failures:
            for orig_val, (lat, lon) in coord_map.items():
                if lat is None and pd.notna(orig_val) and str(orig_val).strip():
                    failures.append(f"Coord failed: '{orig_val}'")

        # Drop original lat_lon column
        df = df.drop(columns=['lat_lon'])

    # Write output
    click.echo(f"\nWriting normalized data to: {output_file}")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_file, index=False)

    # Report statistics
    click.echo("\n" + "=" * 60)
    click.echo("Normalization Summary")
    click.echo("=" * 60)
    click.echo(f"Total biosamples:        {original_count:,}")
    click.echo(f"\nDates:")
    click.echo(f"  Successfully normalized: {date_normalized:,}")
    click.echo(f"  Failed to normalize:     {date_failed:,}")
    click.echo(f"\nCoordinates:")
    click.echo(f"  Successfully normalized: {coord_normalized:,}")
    click.echo(f"  Failed to normalize:     {coord_failed:,}")
    click.echo("=" * 60)

    if report_failures and failures:
        click.echo("\nFailed normalizations:", err=True)
        for failure in failures[:100]:  # Limit to first 100
            click.echo(f"  {failure}", err=True)
        if len(failures) > 100:
            click.echo(f"  ... and {len(failures) - 100} more", err=True)


if __name__ == '__main__':
    normalize_biosamples()

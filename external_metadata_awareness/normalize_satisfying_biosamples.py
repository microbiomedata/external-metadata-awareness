"""
Normalize biosample date and coordinate formats in satisfying biosamples CSV.

This script processes the satisfying biosamples CSV export to normalize:
1. collection_date to ISO 8601 format (YYYY-MM-DD) or NULL
2. lat_lon to decimal degrees format (+/- DD.dddd)

Uses dateparser for robust date parsing and geopy for coordinate conversion.
Optimized to process unique values first, then map back to full dataset.
Preserves original values in output alongside normalized values.

IMPORTANT LIMITATIONS:
- Timezone information is discarded during date normalization
  (e.g., '2017-03-23T23:30Z' → '2017-03-23')
- Time-of-day information is discarded (dates only, no timestamps)
- See issue #217 for future timestamp preservation work
"""

import re
from datetime import datetime
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
    today = datetime.now()
    if year < 2000 or year > today.year:
        return False
    if month < 1 or month > 12:
        return False
    if day < 1 or day > 31:
        return False

    return True


def normalize_date(date_str: Optional[str], imputation_log: list) -> Optional[str]:
    """
    Normalize date string to YYYY-MM-DD format using dateparser.

    Args:
        date_str: Input date string in various formats
        imputation_log: List to append imputation messages to

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

        # Validate year range (must be between 2000 and today)
        today = datetime.now()
        if parsed.year < 2000 or parsed.year > today.year:
            return None

        # Reject future dates
        if parsed.date() > today.date():
            return None

        # Check if day or month was missing and imputed
        # dateparser sets day=1 for year-month dates, month=1 and day=1 for year-only
        original_lower = date_str.lower()

        # Detect year-only format (e.g., "2017")
        if re.match(r'^\d{4}$', date_str):
            imputation_log.append(f"Imputed month=01, day=01 for year-only date: '{date_str}' → '{parsed.strftime('%Y-%m-%d')}'")
        # Detect year-month format (e.g., "2017-02", "2017/02", "Feb 2017")
        elif re.match(r'^\d{4}[-/]\d{1,2}$', date_str) or (len(date_str.split()) == 2 and parsed.day == 1):
            imputation_log.append(f"Imputed day=01 for year-month date: '{date_str}' → '{parsed.strftime('%Y-%m-%d')}'")

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
    default=50,
    help='Report progress every N unique values processed (default: 50)'
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
    Preserves original values alongside normalized values in output.
    """
    click.echo(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Reading input file: {input_file}")

    # Read CSV
    df = pd.read_csv(input_file)
    original_count = len(df)
    click.echo(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Loaded {original_count:,} biosamples")

    # Track normalization statistics
    date_normalized = 0
    date_failed = 0
    coord_normalized = 0
    coord_failed = 0
    failures = []
    imputation_log = []

    # =========================================================================
    # Normalize dates using unique value mapping
    # =========================================================================
    click.echo(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Normalizing collection_date to YYYY-MM-DD format...")
    if 'collection_date' in df.columns:
        # Get unique values and sort alphabetically
        unique_dates = sorted(df['collection_date'].unique(), key=lambda x: str(x))
        total_unique = len(unique_dates)
        click.echo(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]   Found {total_unique:,} unique date values")

        # Process each unique value
        date_map = {}
        for idx, date_val in enumerate(unique_dates, start=1):
            if idx == 1 or idx % progress_interval == 1:
                click.echo(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]   Processing date {idx}/{total_unique}: '{date_val}'")

            normalized = normalize_date(date_val, imputation_log)
            date_map[date_val] = normalized

        # Map back to dataframe - rename original to _raw, normalized has no suffix
        click.echo(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]   Mapping normalized dates back to {original_count:,} rows...")
        df['collection_date_raw'] = df['collection_date']
        df['collection_date'] = df['collection_date_raw'].map(date_map)

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
    click.echo(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Normalizing lat_lon to separate latitude/longitude columns (+/- DD.dddd)...")
    if 'lat_lon' in df.columns:
        # Get unique values and sort alphabetically
        unique_coords = sorted(df['lat_lon'].unique(), key=lambda x: str(x))
        total_unique = len(unique_coords)
        click.echo(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]   Found {total_unique:,} unique coordinate values")

        # Process each unique value
        coord_map = {}
        for idx, coord_val in enumerate(unique_coords, start=1):
            if idx == 1 or idx % progress_interval == 1:
                click.echo(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]   Processing coordinate {idx}/{total_unique}: '{coord_val}'")

            lat, lon = normalize_coordinate(coord_val)
            coord_map[coord_val] = (lat, lon)

        # Map back to dataframe - rename original to _raw, normalized has no suffix
        click.echo(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]   Mapping normalized coordinates back to {original_count:,} rows...")
        df['lat_lon_raw'] = df['lat_lon']
        df['latitude'] = df['lat_lon_raw'].map(lambda x: coord_map.get(x, (None, None))[0])
        df['longitude'] = df['lat_lon_raw'].map(lambda x: coord_map.get(x, (None, None))[1])

        # Drop the original lat_lon column (we have lat_lon_raw now)
        df = df.drop(columns=['lat_lon'])

        # Count successes/failures
        coord_normalized = df['latitude'].notna().sum()
        coord_failed = df['latitude'].isna().sum()

        if report_failures:
            for orig_val, (lat, lon) in coord_map.items():
                if lat is None and pd.notna(orig_val) and str(orig_val).strip():
                    failures.append(f"Coord failed: '{orig_val}'")

    # Filter out rows missing required normalized data
    click.echo(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Filtering rows with incomplete normalized data...")
    rows_before_filter = len(df)

    # Must have all three: collection_date >= 2017-01-01, latitude, longitude
    df = df[
        df['collection_date'].notna() &
        (df['collection_date'] >= '2017-01-01') &
        df['latitude'].notna() &
        df['longitude'].notna()
    ]

    rows_after_filter = len(df)
    rows_removed = rows_before_filter - rows_after_filter

    click.echo(f"  Removed {rows_removed:,} rows missing required data")
    click.echo(f"  Retained {rows_after_filter:,} rows with complete normalization")

    # Write output
    click.echo(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Writing normalized data to: {output_file}")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_file, index=False)

    # Report statistics
    click.echo("\n" + "=" * 60)
    click.echo("Normalization Summary")
    click.echo("=" * 60)
    click.echo(f"Input biosamples:                    {original_count:,}")
    click.echo(f"\nNormalization results:")
    click.echo(f"  Dates successfully normalized:     {date_normalized:,}")
    click.echo(f"  Dates failed to normalize:         {date_failed:,}")
    click.echo(f"  Coordinates successfully normalized: {coord_normalized:,}")
    click.echo(f"  Coordinates failed to normalize:   {coord_failed:,}")
    click.echo(f"\nFiltering (collection_date >= 2017-01-01 AND lat AND lon):")
    click.echo(f"  Rows removed:                      {rows_removed:,}")
    click.echo(f"  Rows retained in output:           {rows_after_filter:,}")
    click.echo("=" * 60)

    # Report date imputations prominently
    if imputation_log:
        click.echo("\n" + "=" * 60)
        click.echo("DATE IMPUTATION REPORT")
        click.echo("=" * 60)
        click.echo(f"Total imputations: {len(imputation_log)}")
        click.echo("\nSample imputations (first 50):")
        for imputation in imputation_log[:50]:
            click.echo(f"  {imputation}")
        if len(imputation_log) > 50:
            click.echo(f"\n  ... and {len(imputation_log) - 50} more imputations")
        click.echo("=" * 60)

    if report_failures and failures:
        click.echo("\nFailed normalizations:", err=True)
        for failure in failures[:100]:  # Limit to first 100
            click.echo(f"  {failure}", err=True)
        if len(failures) > 100:
            click.echo(f"  ... and {len(failures) - 100} more", err=True)


if __name__ == '__main__':
    normalize_biosamples()

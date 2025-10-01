"""
Normalize biosample date and coordinate formats in satisfying biosamples CSV.

This script processes the satisfying biosamples CSV export to normalize:
1. collection_date to ISO 8601 format (YYYY-MM-DD) or NULL
2. lat_lon to decimal degrees format (+/- DD.dddd)

Uses dateparser for robust date parsing and geopy for coordinate conversion.
"""

from pathlib import Path
from typing import Optional

import click
import dateparser
import pandas as pd
from geopy.point import Point


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

    try:
        # Use dateparser for robust, messy format handling
        parsed = dateparser.parse(str(date_str))
        if parsed is None:
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
def normalize_biosamples(
    input_file: Path,
    output_file: Path,
    report_failures: bool
) -> None:
    """
    Normalize biosample dates and coordinates in CSV export.

    Reads the satisfying biosamples CSV, normalizes date and coordinate formats,
    and writes the result to a new CSV file.
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

    # Normalize dates
    click.echo("Normalizing collection_date to YYYY-MM-DD format...")
    if 'collection_date' in df.columns:
        for idx, row in df.iterrows():
            original_date = row['collection_date']
            normalized = normalize_date(original_date)

            if normalized is not None:
                df.at[idx, 'collection_date'] = normalized
                date_normalized += 1
            else:
                df.at[idx, 'collection_date'] = None
                if pd.notna(original_date) and str(original_date).strip():
                    date_failed += 1
                    if report_failures:
                        failures.append(f"Date failed: {row['accession']} - '{original_date}'")

    # Normalize coordinates - split into separate latitude and longitude columns
    click.echo("Normalizing lat_lon to separate latitude and longitude columns (+/- DD.dddd)...")
    if 'lat_lon' in df.columns:
        # Create new columns
        df['latitude'] = None
        df['longitude'] = None

        for idx, row in df.iterrows():
            original_coord = row['lat_lon']
            lat, lon = normalize_coordinate(original_coord)

            if lat is not None and lon is not None:
                df.at[idx, 'latitude'] = lat
                df.at[idx, 'longitude'] = lon
                coord_normalized += 1
            else:
                df.at[idx, 'latitude'] = None
                df.at[idx, 'longitude'] = None
                if pd.notna(original_coord) and str(original_coord).strip():
                    coord_failed += 1
                    if report_failures:
                        failures.append(f"Coord failed: {row['accession']} - '{original_coord}'")

        # Drop the original lat_lon column
        df = df.drop(columns=['lat_lon'])

    # Write output
    click.echo(f"Writing normalized data to: {output_file}")
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

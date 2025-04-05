import pandas as pd
import click


@click.command()
@click.option('--nmdc', 'nmdc_path', required=True, type=click.Path(exists=True), help='Path to nmdc-schema.tsv')
@click.option('--output', 'output_path', default='nmdc_slot_range_summary.tsv', show_default=True,
              type=click.Path(), help='Path to save the output summary file')
def summarize_slot_range_pairs(nmdc_path, output_path):
    """
    Generate a summary of unique (slot, range) pairs in NMDC schema,
    showing whether the range is a class, and which classes use that pair.
    """
    # Load NMDC schema
    nmdc_df = pd.read_csv(nmdc_path, sep='\t')

    # Filter to rows with slot and range
    filtered = nmdc_df[["slot", "range", "class"]].dropna()

    # Get set of NMDC-defined classes
    known_classes = set(nmdc_df["class"].dropna().unique())

    # Group by slot + range, aggregate list of classes
    grouped = (
        filtered.groupby(["slot", "range"])["class"]
        .apply(lambda classes: sorted(set(classes)))
        .reset_index()
        .rename(columns={"class": "domain"})
    )

    # Add column indicating whether the range is also a class
    grouped["range_is_nmdc_class"] = grouped["range"].apply(lambda r: r in known_classes)

    # Convert domain list to string for export
    grouped["domain"] = grouped["domain"].apply(lambda lst: ", ".join(lst))

    # Save result
    grouped.to_csv(output_path, sep="\t", index=False)
    click.echo(f"✅ Slot-range summary saved to: {output_path}")


if __name__ == '__main__':
    summarize_slot_range_pairs()

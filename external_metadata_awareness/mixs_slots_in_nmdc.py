import pandas as pd
import click


@click.command()
@click.option('--mixs', 'mixs_path', required=True, type=click.Path(exists=True), help='Path to mixs-schema.tsv')
@click.option('--nmdc', 'nmdc_path', required=True, type=click.Path(exists=True), help='Path to nmdc-schema.tsv')
@click.option('--output', 'output_path', default='mixs_slot_usage_summary.tsv', show_default=True,
              type=click.Path(), help='Path to save the output summary file')
def generate_slot_summary(mixs_path, nmdc_path, output_path):
    """Generate a table of MIxS slots and their usage in NMDC, with flags for MixsCompliantData exclusivity."""
    # Load the TSV files
    mixs_df = pd.read_csv(mixs_path, sep='\t')
    nmdc_df = pd.read_csv(nmdc_path, sep='\t')

    # Get unique slots
    mixs_slots = set(mixs_df["slot"].dropna().unique())
    nmdc_slots = set(nmdc_df["slot"].dropna().unique())

    # Build base comparison DataFrame
    comparison_df = pd.DataFrame({
        "slot": sorted(mixs_slots),
        "used_in_nmdc": [slot in nmdc_slots for slot in sorted(mixs_slots)]
    })

    # Identify exclusive MixsCompliantData slots
    mixs_compliant_slots = mixs_df[mixs_df["class"] == "MixsCompliantData"]["slot"].dropna().unique()
    slot_class_counts = mixs_df.groupby("slot")["class"].nunique()
    exclusive_slots = [slot for slot in mixs_compliant_slots if slot_class_counts.get(slot, 0) == 1]

    # Add exclusivity column
    comparison_df["exclusive_to_mixs_compliant_data"] = comparison_df["slot"].isin(exclusive_slots)

    # Save result
    comparison_df.to_csv(output_path, sep='\t', index=False)
    click.echo(f"✅ Summary saved to: {output_path}")


if __name__ == '__main__':
    generate_slot_summary()

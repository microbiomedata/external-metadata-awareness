import click
import pandas as pd

# Define the evidence ranking; lower numbers indicate stronger evidence.
EVIDENCE_RANKING = {
    'rdfs:label': 0,
    'oio:hasExactSynonym': 1,
    'oio:hasDbXref': 2,
    'oio:hasRelatedSynonym': 3,
    'skos:relatedMatch': 4,
    'skos:relatedMatch-INVERSE': 5,
    'oio:hasBroadSynonym': 6,
    'oio:hasNarrowSynonym': 7,
    'rdf:ID': 8
}


@click.command()
@click.option('--input', '-i', 'input_file', required=True,
              help="Path to the input TSV file")
@click.option('--output', '-o', 'output_file', required=True,
              help="Path for the output filtered TSV file")
def main(input_file, output_file):
    """Processes the SSSOM lexical matching file to keep only the best evidence rows."""

    # Load the TSV file, ignoring lines that start with "#"
    df = pd.read_csv(input_file, sep="\t", comment='#')

    # Report the number of rows before filtering.
    start_rows = len(df)
    click.echo(f"Starting rows: {start_rows}")

    # Helper function to compute evidence score for a row.
    def get_evidence_score(row):
        subj_val = row.get('subject_match_field')
        obj_val = row.get('object_match_field')
        score_subj = EVIDENCE_RANKING.get(subj_val, 999) if pd.notnull(subj_val) else 999
        score_obj = EVIDENCE_RANKING.get(obj_val, 999) if pd.notnull(obj_val) else 999
        return min(score_subj, score_obj)

    # Calculate evidence score for each row.
    df['evidence_score'] = df.apply(get_evidence_score, axis=1)

    # Group by subject and object.
    group_cols = ['subject_id', 'object_id']
    group_min = df.groupby(group_cols)['evidence_score'].min().reset_index()
    group_min = group_min.rename(columns={'evidence_score': 'min_evidence_score'})

    # Merge the minimum score into the main DataFrame.
    df = pd.merge(df, group_min, on=group_cols, how='left')

    # Keep only rows that have the best evidence score.
    filtered_df = df[df['evidence_score'] == df['min_evidence_score']].copy()

    # Remove duplicate rows.
    filtered_df = filtered_df.drop_duplicates()

    # Remove rows where subject_id equals object_id.
    filtered_df = filtered_df[filtered_df['subject_id'] != filtered_df['object_id']]

    # Drop helper columns.
    filtered_df = filtered_df.drop(columns=['evidence_score', 'min_evidence_score'])

    # Sort the results case-insensitively.
    filtered_df = filtered_df.sort_values(
        by=['subject_label', 'object_label', 'subject_match_field', 'object_match_field'],
        key=lambda col: col.str.lower()
    )

    # Report the number of rows after filtering.
    end_rows = len(filtered_df)
    click.echo(f"Ending rows: {end_rows}")

    # Save the filtered, sorted DataFrame to the output TSV file.
    filtered_df.to_csv(output_file, sep="\t", index=False)
    click.echo(f"Filtered file saved to: {output_file}")


if __name__ == '__main__':
    main()

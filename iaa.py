import pandas as pd
import itertools
import click
from typing import List, Tuple


def safe_int_convert(x):
    try:
        return int(x)
    except (ValueError, pd.errors.IntCastingNaNError):
        return 0


def calculate_iaa(row: pd.Series) -> float:
    values: List[int] = [0 if v not in [-1, 0, 1] else v for v in row.map(safe_int_convert)]
    pairs: List[Tuple[int, int]] = list(itertools.combinations(values, 2))
    agreements: int = sum(1 for a, b in pairs if a == b)
    return agreements / len(pairs)


@click.command()
@click.option('--input-file', '-i', type=click.Path(exists=True), required=True, help='Path to input CSV file.')
@click.option('--output-file', '-o', type=click.Path(), required=True,
              help='Path where the output CSV file will be saved.')
@click.option('--vote-columns', '-v', multiple=True,
              default=['CJM_Vote', 'MAM vote', 'MLS_vote', 'NMW_vote', 'SM_vote'],
              help='Column names for votes.')
@click.option('--debug-toolbar/--no-debug-toolbar', default=False, help='Show or hide the Dash debug toolbar.')
def main(input_file: str, output_file: str, vote_columns: List[str], debug_toolbar: bool) -> None:
    # Step 1: Process the data and create `for_plotting` DataFrame
    df: pd.DataFrame = pd.read_csv(input_file)
    safe_int_vote_columns = [f"{col}_safe_int" for col in vote_columns]
    for col in vote_columns:
        df[f"{col}_safe_int"] = df[col].map(safe_int_convert)

    df['IAA_score'] = df[list(safe_int_vote_columns)].apply(calculate_iaa, axis=1)
    df['vote_sum'] = df[safe_int_vote_columns].sum(axis=1)

    for_plotting = df[~((df['IAA_score'] == 1) & (df['vote_sum'] == 0))]

    # Group data by vote_sum and IAA_score, and calculate count at each coordinate
    grouped = for_plotting.groupby(['vote_sum', 'IAA_score']).size().reset_index(name='count')

    # Step 2: Save the `for_plotting` DataFrame to a CSV file
    df.to_csv(f"{output_file}", index=False)
    print(f"Updated CSV file with IAA scores has been created: {output_file}")


if __name__ == '__main__':
    main()
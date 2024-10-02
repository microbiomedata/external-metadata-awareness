import pandas as pd
import itertools
import click
from typing import List, Tuple
from dash import Dash, dcc, html, Input, Output
from dash import dash_table
import plotly.express as px


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
    #
    # # Step 3: Create and launch the Dash dashboard with dynamic layout
    # app = Dash(__name__)
    #
    # app.layout = html.Div(
    #     style={"display": "flex", "flexDirection": "column", "height": "100vh"},  # Flex container for full height
    #     children=[
    #         dcc.Graph(id='scatter-plot', config={'displayModeBar': True}, style={"flex": "1", "width": "100%"}),
    #         # Plot takes up space
    #         dash_table.DataTable(
    #             id='data-table',
    #             columns=[{"name": i, "id": i} for i in for_plotting.columns],
    #             data=for_plotting.to_dict('records'),
    #             style_table={
    #                 'overflowY': 'auto',  # Allow vertical scrolling for the table
    #                 'overflowX': 'auto',  # Allow horizontal scrolling
    #                 'maxWidth': '100%',  # Ensure table takes full width
    #                 'flex': '1',  # Table takes remaining vertical space
    #                 'display': 'block',  # Ensure scrollbars are visible
    #             },
    #             sort_action='native',  # Enables sorting
    #             fixed_columns={'headers': True, 'data': 2},  # Freeze the first two columns
    #             style_cell={
    #                 'minWidth': '150px',  # Set a minimum width for columns
    #                 'width': '150px',  # Set a default width for columns
    #                 'maxWidth': '200px',  # Ensure columns don't become too wide
    #                 'whiteSpace': 'normal'  # Allow text to wrap within the cells
    #             },
    #         ),
    #     ]
    # )
    #
    # @app.callback(
    #     Output('scatter-plot', 'figure'),
    #     Input('scatter-plot', 'selectedData')
    # )
    # def update_plot(selectedData):
    #     # Plot vote_sum on x-axis and IAA_score on y-axis with larger and color-coded dots
    #     fig = px.scatter(grouped, x='vote_sum', y='IAA_score', size='count', color='count',
    #                      hover_data=['count'], size_max=30, color_continuous_scale='Viridis')
    #     return fig
    #
    # @app.callback(
    #     Output('data-table', 'data'),
    #     Input('scatter-plot', 'selectedData')
    # )
    # def filter_table_on_selection(selectedData):
    #     if selectedData is None or not selectedData['points']:
    #         return for_plotting.to_dict('records')  # Show all rows if no points are selected
    #
    #     # Extract selected points and filter the DataFrame based on those points
    #     selected_points = [(point['x'], point['y']) for point in selectedData['points']]
    #     filtered_data = for_plotting[
    #         for_plotting.apply(lambda row: (row['vote_sum'], row['IAA_score']) in selected_points, axis=1)
    #     ]
    #     return filtered_data.to_dict('records')
    #
    # # Run the Dash app, pass `debug_toolbar` to control the toolbar visibility
    # app.run_server(debug=debug_toolbar)


if __name__ == '__main__':
    main()

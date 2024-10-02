import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np  # Needed for logarithmic transformation
from streamlit_plotly_events import plotly_events
from st_aggrid import AgGrid, GridOptionsBuilder

# Load the CSV file
df = pd.read_csv('soil-ebs-with-iaa.csv')

# Remove rows where the 'unique_id' column is empty or missing
df = df[df['unique_id'].notna()]

# Group by 'vote_sum' and 'IAA_score' to calculate how many rows share the same coordinates
df['count'] = df.groupby(['vote_sum', 'IAA_score'])['unique_id'].transform('count')

# Apply logarithmic scaling to counts
df['log_count'] = df['count'].apply(lambda x: np.log1p(x))  # log1p to avoid log(0)

# Set up the page layout
st.set_page_config(layout="wide")

# Create a Plotly scatter plot for IAA_score vs votesum
# Size the dots based on the log-scaled count of rows with the same coordinates
fig = px.scatter(
    df,
    x='vote_sum',
    y='IAA_score',
    size='log_count',  # Size based on log-scaled count
    title='IAA Score vs Vote Sum (Logarithmic Scaling)',
    hover_data=df.columns
)

# Enable lasso/box selection tool
fig.update_layout(dragmode='lasso', height=400)  # Set plot height

# Display the plot and capture selected points
selected_points = plotly_events(fig, click_event=False, hover_event=False, select_event=True)

# Add a button to reset the selection
reset = st.button('Reset Selection')

# Filter the table based on selected points, or reset if the button is clicked
if reset or not selected_points:
    filtered_df = df  # Show all rows when reset is clicked or no points are selected
else:
    selected_indices = [point['pointIndex'] for point in selected_points]
    filtered_df = df.iloc[selected_indices]

# Create Ag-Grid options to enable horizontal scrolling and freeze first two columns
gb = GridOptionsBuilder.from_dataframe(filtered_df)
gb.configure_default_column(resizable=True)
gb.configure_column('unique_id', pinned='left', width=200)  # Freeze unique_id column and set width
gb.configure_column('label', pinned='left', width=200)  # Freeze label column and set width
gb.configure_grid_options(domLayout='normal')  # Enable horizontal scrolling

# Display the table with AgGrid
grid_options = gb.build()
AgGrid(filtered_df, gridOptions=grid_options, height=300, fit_columns_on_grid_load=False)  # Disable auto column fit

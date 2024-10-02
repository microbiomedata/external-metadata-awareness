import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np  # Needed for logarithmic transformation
from streamlit_plotly_events import plotly_events
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# Set up the page layout
st.set_page_config(layout="wide")

# Prompt the user to upload a CSV file
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

# Check if a file was uploaded
if uploaded_file is not None:
    # Load the uploaded CSV file
    df = pd.read_csv(uploaded_file)

    # Remove rows where the 'unique_id' column is empty or missing
    df = df[df['unique_id'].notna()]

    # Add new columns: streamlit_keep (default false) and streamlit_notes (default empty string)
    df['streamlit_keep'] = False  # Default to False
    df['streamlit_notes'] = ""  # Default to an empty string

    # Group by 'vote_sum' and 'IAA_score' to calculate how many rows share the same coordinates
    df['count'] = df.groupby(['vote_sum', 'IAA_score'])['unique_id'].transform('count')

    # Apply logarithmic scaling to counts
    df['log_count'] = df['count'].apply(lambda x: np.log1p(x))  # log1p to avoid log(0)

    # Create a Plotly scatter plot for IAA_score vs votesum
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

    # Place the reset and download buttons on the same horizontal line
    col1, col2 = st.columns([1, 2])

    with col1:
        reset = st.button('Reset Selection')

    # Filter the table based on selected points, or reset if the button is clicked
    if reset or not selected_points:
        filtered_df = df  # Show all rows when reset is clicked or no points are selected
    else:
        selected_indices = [point['pointIndex'] for point in selected_points]
        filtered_df = df.iloc[selected_indices]

    # Create Ag-Grid options: only 'streamlit_keep' and 'streamlit_notes' are editable
    gb = GridOptionsBuilder.from_dataframe(filtered_df)
    gb.configure_default_column(resizable=True, editable=False)  # Make all columns non-editable by default
    gb.configure_column('streamlit_keep', editable=True)  # Only streamlit_keep is editable
    gb.configure_column('streamlit_notes', editable=True)  # Only streamlit_notes is editable
    gb.configure_column('unique_id', pinned='left', width=200)  # Freeze unique_id
    gb.configure_column('label', pinned='left', width=200)  # Freeze label
    gb.configure_grid_options(domLayout='normal')  # Enable horizontal scrolling

    # Display the table with AgGrid
    grid_options = gb.build()
    grid_response = AgGrid(
        filtered_df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.VALUE_CHANGED,
        height=300,
        fit_columns_on_grid_load=False
    )

    # Capture the edited data from the table
    edited_df = pd.DataFrame(grid_response['data'])

    with col2:
        # Add a download button for the edited data
        csv = edited_df.to_csv(index=False)  # Convert the edited data to CSV
        st.download_button(
            label="Download edited data as CSV",
            data=csv,
            file_name='edited_data.csv',
            mime='text/csv',
        )

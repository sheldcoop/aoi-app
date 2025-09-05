# src/data_handler.py

import pandas as pd
import streamlit as st

def calculate_plot_coords(df, panel_rows, panel_cols, gap_size):
    """
    Calculates the global plot coordinates (PLOT_X, PLOT_Y) based on quadrant and unit indices.
    This is the key transformation step to fix the KeyError.
    """
    # Define offsets for each quadrant
    q2_x_offset = panel_cols + gap_size
    q3_y_offset = panel_rows + gap_size
    q4_x_offset = panel_cols + gap_size
    q4_y_offset = panel_rows + gap_size

    # Create PLOT_X and PLOT_Y columns
    df['PLOT_X'] = df['UNIT_INDEX_X'] + 0.5  # Default for Q1 and Q3
    df['PLOT_Y'] = df['UNIT_INDEX_Y'] + 0.5  # Default for Q1 and Q2

    # Apply offsets based on quadrant
    df.loc[df['QUADRANT'] == 'Q2', 'PLOT_X'] += q2_x_offset
    df.loc[df['QUADRANT'] == 'Q3', 'PLOT_Y'] += q3_y_offset
    df.loc[df['QUADRANT'] == 'Q4', 'PLOT_X'] += q4_x_offset
    df.loc[df['QUADRANT'] == 'Q4', 'PLOT_Y'] += q4_y_offset
    
    return df

# Use caching to improve performance on re-runs
@st.cache_data
def load_data(uploaded_file, panel_rows, panel_cols, gap_size):
    """
    Loads data from an uploaded Excel file, validates it, and calculates plot coordinates.
    """
    if uploaded_file is None:
        return pd.DataFrame()

    try:
        df = pd.read_excel(uploaded_file)
        
        # --- Data Validation ---
        required_columns = ['QUADRANT', 'UNIT_INDEX_X', 'UNIT_INDEX_Y', 'DEFECT_TYPE']
        if not all(col in df.columns for col in required_columns):
            st.error(f"Error: The uploaded Excel file is missing one or more required columns. Please ensure it contains: {', '.join(required_columns)}")
            return pd.DataFrame()

        # --- Data Transformation ---
        df = calculate_plot_coords(df, panel_rows, panel_cols, gap_size)

        return df
        
    except Exception as e:
        st.error(f"An error occurred while reading the Excel file: {e}")
        return pd.DataFrame()

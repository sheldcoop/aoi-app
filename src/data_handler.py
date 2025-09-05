# src/data_handler.py

import pandas as pd
import numpy as np
import streamlit as st

def derive_quadrants(df):
    """
    Derives the QUADRANT column from X_COORDINATES and Y_COORDINATES if it doesn't exist.
    It finds the center of the defect cloud and assigns quadrants based on that center.
    """
    if 'X_COORDINATES' not in df.columns or 'Y_COORDINATES' not in df.columns:
        st.error("Cannot derive quadrants because 'X_COORDINATES' or 'Y_COORDINATES' are missing.")
        return df

    # Find the midpoint of the entire dataset
    x_midpoint = (df['X_COORDINATES'].min() + df['X_COORDINATES'].max()) / 2
    y_midpoint = (df['Y_COORDINATES'].min() + df['Y_COORDINATES'].max()) / 2

    # Define conditions for each quadrant based on the midpoint
    conditions = [
        (df['X_COORDINATES'] <= x_midpoint) & (df['Y_COORDINATES'] <= y_midpoint),  # Q1 (Bottom-Left)
        (df['X_COORDINATES'] > x_midpoint)  & (df['Y_COORDINATES'] <= y_midpoint),  # Q2 (Bottom-Right)
        (df['X_COORDINATES'] <= x_midpoint) & (df['Y_COORDINATES'] > y_midpoint),   # Q3 (Top-Left)
        (df['X_COORDINATES'] > x_midpoint)  & (df['Y_COORDINATES'] > y_midpoint)    # Q4 (Top-Right)
    ]
    
    # Define the corresponding quadrant labels
    quadrant_labels = ['Q1', 'Q2', 'Q3', 'Q4']
    
    # Use numpy.select to efficiently assign the quadrant labels
    df['QUADRANT'] = np.select(conditions, quadrant_labels, default='Unknown')
    
    st.success("Successfully derived defect quadrants from X/Y coordinates.")
    return df

def calculate_plot_coords(df, panel_rows, panel_cols, gap_size):
    """
    Calculates the global plot coordinates (PLOT_X, PLOT_Y) based on quadrant and unit indices.
    """
    # Define offsets for each quadrant
    q2_x_offset = panel_cols + gap_size
    q3_y_offset = panel_rows + gap_size
    q4_x_offset = panel_cols + gap_size
    q4_y_offset = panel_rows + gap_size

    # Add 0.5 to center the defect marker within its unit cell
    df['PLOT_X'] = df['UNIT_INDEX_X'] + 0.5
    df['PLOT_Y'] = df['UNIT_INDEX_Y'] + 0.5

    # Apply offsets based on the (now guaranteed) QUADRANT column
    df.loc[df['QUADRANT'] == 'Q2', 'PLOT_X'] += q2_x_offset
    df.loc[df['QUADRANT'] == 'Q3', 'PLOT_Y'] += q3_y_offset
    df.loc[df['QUADRANT'] == 'Q4', 'PLOT_X'] += q4_x_offset
    df.loc[df['QUADRANT'] == 'Q4', 'PLOT_Y'] += q4_y_offset
    
    return df

# Use caching to improve performance on re-runs
@st.cache_data
def load_data(uploaded_file, panel_rows, panel_cols, gap_size):
    """
    Loads data, derives quadrants if necessary, and calculates plot coordinates.
    """
    if uploaded_file is None:
        return pd.DataFrame()

    try:
        df = pd.read_excel(uploaded_file)
        
        # --- Data Validation ---
        # We now check for the columns needed for derivation.
        base_required_columns = ['UNIT_INDEX_X', 'UNIT_INDEX_Y', 'DEFECT_TYPE']
        if not all(col in df.columns for col in base_required_columns):
            st.error(f"Error: Excel file is missing required columns. Please ensure it has: {', '.join(base_required_columns)}")
            return pd.DataFrame()

        # --- Data Derivation Step ---
        # If the QUADRANT column is not in the uploaded file, create it.
        if 'QUADRANT' not in df.columns:
            df = derive_quadrants(df)
            if 'QUADRANT' not in df.columns: # Check if derivation failed
                return pd.DataFrame()

        # --- Data Transformation Step ---
        # Now that QUADRANT is guaranteed to exist, calculate plot coordinates.
        df = calculate_plot_coords(df, panel_rows, panel_cols, gap_size)

        return df
        
    except Exception as e:
        st.error(f"An error occurred while processing the Excel file: {e}")
        return pd.DataFrame()

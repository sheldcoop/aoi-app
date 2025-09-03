# src/data_handler.py
# This module contains all functions related to loading and processing data.

import streamlit as st
import pandas as pd
import numpy as np

# ==============================================================================
# --- DATA LOADING & PREPARATION ---
# ==============================================================================

@st.cache_data
def load_data(uploaded_file, panel_rows, panel_cols, gap_size):
    """
    Loads, prepares, and caches the defect data from a user-uploaded file.
    If no file is uploaded, it falls back to generating sample data with probabilities.
    """
    if uploaded_file is not None:
        # --- Production Path: Load from uploaded Excel file ---
        st.sidebar.success("Excel file uploaded successfully!")
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        
        # --- Data Cleaning and Validation ---
        required_columns = ['DEFECT_TYPE', 'UNIT_INDEX_X', 'UNIT_INDEX_Y']
        if not all(col in df.columns for col in required_columns):
            st.error(f"The uploaded file is missing one of the required columns: {required_columns}")
            return pd.DataFrame() # Return empty dataframe to prevent crashes
            
        df = df[required_columns]
        df.dropna(subset=required_columns, inplace=True)

        # Ensure data types are correct
        df['UNIT_INDEX_X'] = df['UNIT_INDEX_X'].astype(int)
        df['UNIT_INDEX_Y'] = df['UNIT_INDEX_Y'].astype(int)
        
        # Clean up defect type strings
        df['DEFECT_TYPE'] = df['DEFECT_TYPE'].str.strip()
        
    else:
        # --- Fallback Path: Generate sample data (non-uniform probabilities) ---
        st.sidebar.info("No file uploaded. Displaying sample probabilistic data.")
        total_rows, total_cols = 2 * panel_rows, 2 * panel_cols
        number_of_defects = 211

        # Define probability distributions (random, not uniform)
        row_probs = np.random.rand(total_rows)      # random weights for each row
        row_probs = row_probs / row_probs.sum()     # normalize so they sum to 1
        
        col_probs = np.random.rand(total_cols)      # random weights for each col
        col_probs = col_probs / col_probs.sum()

        defect_data = {
            'UNIT_INDEX_X': np.random.choice(total_rows, size=number_of_defects, p=row_probs),
            'UNIT_INDEX_Y': np.random.choice(total_cols, size=number_of_defects, p=col_probs),
            'DEFECT_TYPE': np.random.choice([
                'Nick', 'Short', 'Missing Feature', 'Cut', 'Fine Short', 
                'Pad Violation', 'Island', 'Cut/Short', 'Nick/Protrusion'
            ], size=number_of_defects)
        }
        df = pd.DataFrame(defect_data)

    # --- Common Processing for both loaded and sample data ---
    
    # Assign Quadrant
    conditions = [
        (df['UNIT_INDEX_X'] < panel_rows) & (df['UNIT_INDEX_Y'] < panel_cols),
        (df['UNIT_INDEX_X'] < panel_rows) & (df['UNIT_INDEX_Y'] >= panel_cols),
        (df['UNIT_INDEX_X'] >= panel_rows) & (df['UNIT_INDEX_Y'] < panel_cols),
        (df['UNIT_INDEX_X'] >= panel_rows) & (df['UNIT_INDEX_Y'] >= panel_cols)
    ]
    choices = ['Q1', 'Q2', 'Q3', 'Q4']
    df['QUADRANT'] = np.select(conditions, choices, default='Other')
    
    # Coordinate Transformation
    plot_x_base = df['UNIT_INDEX_Y'] % panel_cols
    plot_y_base = df['UNIT_INDEX_X'] % panel_rows
    x_offset = np.where(df['UNIT_INDEX_Y'] >= panel_cols, panel_cols + gap_size, 0)
    y_offset = np.where(df['UNIT_INDEX_X'] >= panel_rows, panel_rows + gap_size, 0)
    df['plot_x'] = plot_x_base + x_offset + np.random.rand(len(df)) * 0.8 + 0.1
    df['plot_y'] = plot_y_base + y_offset + np.random.rand(len(df)) * 0.8 + 0.1
    
    return df

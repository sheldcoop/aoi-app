# src/data_handler.py
# This module contains all functions related to loading and processing data.

import streamlit as st
import pandas as pd
import numpy as np

# ==============================================================================
# --- DATA LOADING & PREPARATION ---
# ==============================================================================

@st.cache_data
def load_data(uploaded_files, panel_rows, panel_cols, gap_size):
    """
    Loads and prepares defect data from one or more user-uploaded files.
    If no files are uploaded, it falls back to generating sample data.
    """
    if uploaded_files:
        # --- Production Path: Load from uploaded Excel file(s) ---
        all_dfs = []
        for uploaded_file in uploaded_files:
            try:
                df = pd.read_excel(uploaded_file, engine='openpyxl')

                # --- Data Cleaning and Validation ---
                required_columns = ['DEFECT_TYPE', 'UNIT_INDEX_X', 'UNIT_INDEX_Y']
                if not all(col in df.columns for col in required_columns):
                    st.error(f"File '{uploaded_file.name}' is missing required columns. Skipping.")
                    continue

                df = df[required_columns]
                df.dropna(subset=required_columns, inplace=True)
                df['UNIT_INDEX_X'] = df['UNIT_INDEX_X'].astype(int)
                df['UNIT_INDEX_Y'] = df['UNIT_INDEX_Y'].astype(int)
                df['DEFECT_TYPE'] = df['DEFECT_TYPE'].str.strip()
                all_dfs.append(df)
            except Exception as e:
                st.error(f"Error processing file '{uploaded_file.name}': {e}")
        
        if not all_dfs:
            st.warning("No valid data could be loaded from the uploaded file(s).")
            return pd.DataFrame()

        st.sidebar.success(f"{len(all_dfs)} file(s) loaded successfully!")
        df = pd.concat(all_dfs, ignore_index=True)

    else:
        # --- Fallback Path: Generate sample data ---
        st.sidebar.info("No file uploaded. Displaying sample data.")
        total_rows, total_cols = 2 * panel_rows, 2 * panel_cols
        number_of_defects = 150
        defect_data = {
            'UNIT_INDEX_X': np.random.randint(0, total_rows, size=number_of_defects),
            'UNIT_INDEX_Y': np.random.randint(0, total_cols, size=number_of_defects),
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
    
    return df


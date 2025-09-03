# src/data_handler.py
# This module contains all functions related to loading and processing data.

import streamlit as st
import pandas as pd
import numpy as np

# ==============================================================================
# --- DATA LOADING & PREPARATION ---
# ==============================================================================

def load_data(uploaded_file, panel_rows, panel_cols, gap_size):
    """
    Loads, prepares, and caches the defect data from a user-uploaded file.
    If no file is uploaded, it falls back to generating fresh random data
    on every reload (no caching).
    """
    if uploaded_file is not None:
        # --- Production Path: Load from uploaded Excel file ---
        @st.cache_data
        def process_uploaded_file(uploaded_file, panel_rows, panel_cols, gap_size):
            st.sidebar.success("Excel file uploaded successfully!")
            df = pd.read_excel(uploaded_file, engine='openpyxl')
            
            # --- Data Cleaning and Validation ---
            required_columns = ['DEFECT_TYPE', 'UNIT_INDEX_X', 'UNIT_INDEX_Y']
            if not all(col in df.columns for col in required_columns):
                st.error(f"The uploaded file is missing one of the required columns: {required_columns}")
                return pd.DataFrame()
                
            df = df[required_columns]
            df.dropna(subset=required_columns, inplace=True)
            df['UNIT_INDEX_X'] = df['UNIT_INDEX_X'].astype(int)
            df['UNIT_INDEX_Y'] = df['UNIT_INDEX_Y'].astype(int)
            df['DEFECT_TYPE'] = df['DEFECT_TYPE'].str.strip()
            return df

        df = process_uploaded_file(uploaded_file, panel_rows, panel_cols, gap_size)

    else:
        # --- Fallback Path: Generate sample data (random clusters, no caching) ---
        st.sidebar.info("No file uploaded. Displaying fresh random clustered data.")
        total_rows, total_cols = 2 * panel_rows, 2 * panel_cols
        number_of_defects = 255

        # Choose random cluster centers
        num_clusters = 6
        cluster_centers_x = np.random.randint(0, total_rows, size=num_clusters)
        cluster_centers_y = np.random.randint(0, total_cols, size=num_clusters)

        defects_x, defects_y = [], []
        for i in range(number_of_defects):
            cluster_id = np.random.randint(0, num_clusters)
            x = int(np.random.normal(cluster_centers_x[cluster_id], scale=2))
            y = int(np.random.normal(cluster_centers_y[cluster_id], scale=2))
            x = np.clip(x, 0, total_rows - 1)
            y = np.clip(y, 0, total_cols - 1)
            defects_x.append(x)
            defects_y.append(y)

        defect_data = {
            'UNIT_INDEX_X': defects_x,
            'UNIT_INDEX_Y': defects_y,
            'DEFECT_TYPE': np.random.choice([
                'Nick', 'Short', 'Missing Feature', 'Cut', 'Fine Short', 
                'Pad Violation', 'Island', 'Cut/Short', 'Nick/Protrusion'
            ], size=number_of_defects)
        }
        df = pd.DataFrame(defect_data)

    # --- Common Processing for both loaded and sample data ---
    conditions = [
        (df['UNIT_INDEX_X'] < panel_rows) & (df['UNIT_INDEX_Y'] < panel_cols),
        (df['UNIT_INDEX_X'] < panel_rows) & (df['UNIT_INDEX_Y'] >= panel_cols),
        (df['UNIT_INDEX_X'] >= panel_rows) & (df['UNIT_INDEX_Y'] < panel_cols),
        (df['UNIT_INDEX_X'] >= panel_rows) & (df['UNIT_INDEX_Y'] >= panel_cols)
    ]
    choices = ['Q1', 'Q2', 'Q3', 'Q4']
    df['QUADRANT'] = np.select(conditions, choices, default='Other')
    
    plot_x_base = df['UNIT_INDEX_Y'] % panel_cols
    plot_y_base = df['UNIT_INDEX_X'] % panel_rows
    x_offset = np.where(df['UNIT_INDEX_Y'] >= panel_cols, panel_cols + gap_size, 0)
    y_offset = np.where(df['UNIT_INDEX_X'] >= panel_rows, panel_rows + gap_size, 0)
    df['plot_x'] = plot_x_base + x_offset + np.random.rand(len(df)) * 0.8 + 0.1
    df['plot_y'] = plot_y_base + y_offset + np.random.rand(len(df)) * 0.8 + 0.1
    
    return df

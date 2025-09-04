# src/data_handler.py
# This module contains all functions related to loading and processing data.

import streamlit as st
import pandas as pd
import numpy as np
import re

# ==============================================================================
# --- IMAGE DATA HANDLING ---
# ==============================================================================

def create_image_lookup_from_uploads(uploaded_images):
    """
    Scans the uploaded image files, parses filenames to extract DEFECT_ID,
    and creates a lookup dictionary mapping the ID to the image data.
    """
    image_lookup = {}
    if not uploaded_images:
        return image_lookup

    # Regex to extract DEFECT_ID from filenames like 'defect_101.jpg'
    pattern = re.compile(r"defect_(\d+).*\.(jpg|jpeg|png)", re.IGNORECASE)

    for image_file in uploaded_images:
        match = pattern.match(image_file.name)
        if match:
            defect_id = int(match.group(1))
            image_lookup[defect_id] = image_file

    return image_lookup

# ==============================================================================
# --- DATA LOADING & PREPARATION ---
# ==============================================================================

@st.cache_data
def load_data(uploaded_file, panel_rows, panel_cols, gap_size):
    """
    Loads, prepares, and caches data from a user-uploaded file.
    If no file is uploaded, it falls back to sample data.
    This function is cached for performance.
    """
    if uploaded_file is not None:
        st.sidebar.success("Excel file uploaded successfully!")
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        
        required_columns = ['DEFECT_ID', 'DEFECT_TYPE', 'UNIT_INDEX_X', 'UNIT_INDEX_Y']
        if not all(col in df.columns for col in required_columns):
            st.error(f"Uploaded file is missing required columns. Ensure it has: {required_columns}")
            return pd.DataFrame()
            
        df = df[required_columns]
        df.dropna(subset=required_columns, inplace=True)

        for col in ['DEFECT_ID', 'UNIT_INDEX_X', 'UNIT_INDEX_Y']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df.dropna(subset=['DEFECT_ID', 'UNIT_INDEX_X', 'UNIT_INDEX_Y'], inplace=True)
        df['DEFECT_ID'] = df['DEFECT_ID'].astype(int)

        df['DEFECT_TYPE'] = df['DEFECT_TYPE'].str.strip()
        
    else:
        st.sidebar.info("No file uploaded. Displaying sample data.")
        total_rows, total_cols = 2 * panel_rows, 2 * panel_cols
        number_of_defects = 1500
        defect_data = {
            'DEFECT_ID': range(number_of_defects),
            'UNIT_INDEX_X': np.random.randint(0, total_rows, size=number_of_defects),
            'UNIT_INDEX_Y': np.random.randint(0, total_cols, size=number_of_defects),
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


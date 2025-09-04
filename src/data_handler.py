# src/data_handler.py
# This module contains all functions related to loading and processing data.

import streamlit as st
import pandas as pd
import numpy as np
import os
import re
from collections import defaultdict

# ==============================================================================
# --- IMAGE DATA HANDLING ---
# ==============================================================================

@st.cache_data
def create_image_lookup(image_dir="images"):
    """
    Scans the image directory, parses filenames to extract coordinates,
    and creates a lookup dictionary mapping coordinates to image paths.
    """
    image_lookup = defaultdict(list)
    if not os.path.exists(image_dir):
        return {}

    # Regex to extract coordinates from filenames like 'defect_X_Y_mZ.jpg'
    pattern = re.compile(r"defect_(\d+)_(\d+)_m\d+\.jpg")

    for filename in os.listdir(image_dir):
        match = pattern.match(filename)
        if match:
            x_coord = int(match.group(1))
            y_coord = int(match.group(2))
            image_lookup[(x_coord, y_coord)].append(os.path.join(image_dir, filename))

    # Return a regular dict with the first image found for each coordinate
    return {key: value[0] for key, value in image_lookup.items()}

# ==============================================================================
# --- DATA LOADING & PREPARATION ---
# ==============================================================================

@st.cache_data
def load_data(uploaded_file, panel_rows, panel_cols, gap_size):
    """
    Loads, prepares, and caches the defect data from a user-uploaded file.
    If no file is uploaded, it falls back to generating sample data.
    Also links defect data to available images.
    """
    # --- Create the image lookup dictionary ---
    image_lookup = create_image_lookup()

    if uploaded_file is not None:
        # --- Production Path: Load from uploaded Excel file ---
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
        
    else:
        # --- Fallback Path: Generate sample data ---
        st.sidebar.info("No file uploaded. Displaying sample data.")
        total_rows, total_cols = 2 * panel_rows, 2 * panel_cols
        number_of_defects = 1500
        defect_data = {
            'UNIT_INDEX_X': np.random.randint(0, total_rows, size=number_of_defects),
            'UNIT_INDEX_Y': np.random.randint(0, total_cols, size=number_of_defects),
            'DEFECT_TYPE': np.random.choice([
                'Nick', 'Short', 'Missing Feature', 'Cut', 'Fine Short', 
                'Pad Violation', 'Island', 'Cut/Short', 'Nick/Protrusion'
            ], size=number_of_defects),
            'image_path': [None] * number_of_defects  # No images for sample data
        }
        df = pd.DataFrame(defect_data)

    # --- Link Images to Defect Data ---
    if 'image_path' not in df.columns:
        df['image_path'] = df.apply(
            lambda row: image_lookup.get((row['UNIT_INDEX_X'], row['UNIT_INDEX_Y'])),
            axis=1
        )

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


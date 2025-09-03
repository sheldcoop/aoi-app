# src/data_handler.py
# This module contains all functions related to loading and processing data.

import streamlit as st
import pandas as pd
import numpy as np

# ==============================================================================
# --- DATA LOADING & PREPARATION ---
# ==============================================================================

@st.cache_data
def process_uploaded_file(uploaded_file, panel_rows, panel_cols, gap_size):
    """
    Loads, cleans, and processes the defect data from an uploaded Excel file.
    This is cached for performance.
    """
    st.sidebar.success("Excel file uploaded successfully!")
    df = pd.read_excel(uploaded_file, engine='openpyxl')
    
    # --- Data Cleaning and Validation ---
    required_columns = ['DEFECT_TYPE', 'UNIT_INDEX_X', 'UNIT_INDEX_Y']
    if not all(col in df.columns for col in required_columns):
        st.error(f"The uploaded file is missing one of the required columns: {required_columns}")
        return pd.DataFrame()  # prevent crashes

    # Select only needed columns
    df = df[required_columns].dropna(subset=required_columns)

    # Ensure correct dtypes
    df['UNIT_INDEX_X'] = df['UNIT_INDEX_X'].astype(int)
    df['UNIT_INDEX_Y'] = df['UNIT_INDEX_Y'].astype(int)

    # Clean defect type strings
    df['DEFECT_TYPE'] = df['DEFECT_TYPE'].str.strip()

    # Common processing
    df = add_quadrant_and_plot_coords(df, panel_rows, panel_cols, gap_size)
    return df


def generate_sample_data(panel_rows, panel_cols, gap_size):
    """
    Generates fresh random sample defect data every reload (not cached).
    Uses random probability distributions for row/col selection.
    """
    st.sidebar.info("No file uploaded. Displaying sample data.")
    total_rows, total_cols = 2 * panel_rows, 2 * panel_cols
    number_of_defects = 211

    # --- Random probability distributions (different every reload) ---
    row_probs = np.random.rand(total_rows)
    row_probs = row_probs / row_probs.sum()
    col_probs = np.random.rand(total_cols)
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

    # Common processing
    df = add_quadrant_and_plot_coords(df, panel_rows, panel_cols, gap_size)
    return df


def add_quadrant_and_plot_coords(df, panel_rows, panel_cols, gap_size):
    """
    Adds quadrant assignment and plotting coordinates.
    Shared by uploaded + sample data.
    """
    # --- Quadrant assignment ---
    conditions = [
        (df['UNIT_INDEX_X'] < panel_rows) & (df['UNIT_INDEX_Y'] < panel_cols),
        (df['UNIT_INDEX_X'] < panel_rows) & (df['UNIT_INDEX_Y'] >= panel_cols),
        (df['UNIT_INDEX_X'] >= panel_rows) & (df['UNIT_INDEX_Y'] < panel_cols),
        (df['UNIT_INDEX_X'] >= panel_rows) & (df['UNIT_INDEX_Y'] >= panel_cols)
    ]
    choices = ['Q1', 'Q2', 'Q3', 'Q4']
    df['QUADRANT'] = np.select(conditions, choices, default='Other')

    # --- Plot coordinates with offsets and jitter ---
    plot_x_base = df['UNIT_INDEX_Y'] % panel_cols
    plot_y_base = df['UNIT_INDEX_X'] % panel_rows
    x_offset = np.where(df['UNIT_INDEX_Y'] >= panel_cols, panel_cols + gap_size, 0)
    y_offset = np.where(df['UNIT_INDEX_X'] >= panel_rows, panel_rows + gap_size, 0)

    df['plot_x'] = plot_x_base + x_offset + np.random.rand(len(df)) * 0.8 + 0.1
    df['plot_y'] = plot_y_base + y_offset + np.random.rand(len(df)) * 0.8 + 0.1

    return df


def load_data(uploaded_file, panel_rows, panel_cols, gap_size):
    """
    Main entry point for loading data.
    - If file uploaded → cached processing.
    - If no file → fresh random data each reload.
    """
    if uploaded_file is not None:
        return process_uploaded_file(uploaded_file, panel_rows, panel_cols, gap_size)
    else:
        return generate_sample_data(panel_rows, panel_cols, gap_size)

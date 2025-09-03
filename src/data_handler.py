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
    If no file is uploaded, it falls back to generating sample data.
    """
    if uploaded_file is not None:
        # --- Production Path: Load from uploaded Excel file ---
        st.sidebar.success("Excel file uploaded successfully!")
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        
        # --- Data Cleaning and Validation ---
        required_columns = ['DEFECT_TYPE', 'UNIT_INDEX_X', 'UNIT_INDEX_Y']
        # Check if all required columns are present
        if not all(col in df.columns for col in required_columns):
            st.error(f"The uploaded file is missing one of the required columns: {required_columns}")
            return pd.DataFrame() # Return empty dataframe to prevent crashes
            
        # Select only the columns we need
        df = df[required_columns]
        
        # Remove rows with missing values in our key columns
        df.dropna(subset=required_columns, inplace=True)

        # Ensure data types are correct
        df['UNIT_INDEX_X'] = df['UNIT_INDEX_X'].astype(int)
        df['UNIT_INDEX_Y'] = df['UNIT_INDEX_Y'].astype(int)
        
        # Clean up defect type strings
        df['DEFECT_TYPE'] = df['DEFECT_TYPE'].str.strip()
        
    else:
        # --- Fallback Path: Generate sample data with weighted quadrants ---
        st.sidebar.info("No file uploaded. Displaying sample data.")
        total_rows, total_cols = 2 * panel_rows, 2 * panel_cols
        number_of_defects = 500
        
        # --- NEW CODE: Define Quadrant Probabilities ---
        # Sum of probabilities must be 1.0
        # In this example, Q1 gets 40%, Q2 gets 30%, Q3 gets 20%, Q4 gets 10%
        quadrant_probabilities = [0.4, 0.3, 0.2, 0.1]
        
        # Use np.random.choice to select a quadrant for each defect based on probabilities
        quadrant_choices = np.random.choice(
            ['Q1', 'Q2', 'Q3', 'Q4'],
            size=number_of_defects,
            p=quadrant_probabilities
        )

        # --- NEW CODE: Generate coordinates based on the assigned quadrant ---
        defect_data = {
            'UNIT_INDEX_X': [],
            'UNIT_INDEX_Y': [],
            'DEFECT_TYPE': np.random.choice([
                'Nick', 'Short', 'Missing Feature', 'Cut', 'Fine Short', 
                'Pad Violation', 'Island', 'Cut/Short', 'Nick/Protrusion'
            ], size=number_of_defects)
        }

        for q in quadrant_choices:
            if q == 'Q1':
                defect_data['UNIT_INDEX_X'].append(np.random.randint(0, panel_rows))
                defect_data['UNIT_INDEX_Y'].append(np.random.randint(0, panel_cols))
            elif q == 'Q2':
                defect_data['UNIT_INDEX_X'].append(np.random.randint(0, panel_rows))
                defect_data['UNIT_INDEX_Y'].append(np.random.randint(panel_cols, total_cols))
            elif q == 'Q3':
                defect_data['UNIT_INDEX_X'].append(np.random.randint(panel_rows, total_rows))
                defect_data['UNIT_INDEX_Y'].append(np.random.randint(0, panel_cols))
            elif q == 'Q4':
                defect_data['UNIT_INDEX_X'].append(np.random.randint(panel_rows, total_rows))
                defect_data['UNIT_INDEX_Y'].append(np.random.randint(panel_cols, total_cols))

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

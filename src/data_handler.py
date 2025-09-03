# src/data_handler.py

import streamlit as st
import pandas as pd
import numpy as np

# ==============================================================================
# --- DATA LOADING & PREPARATION ---
# ==============================================================================

@st.cache_data
def load_data(uploaded_file, panel_rows, panel_cols, gap_size, quadrant_probabilities):
    """
    Loads, prepares, and caches the defect data.
    Now accepts quadrant_probabilities as an input to break the cache.
    """
    if uploaded_file is not None:
        st.sidebar.success("Excel file uploaded successfully!")
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        
        required_columns = ['DEFECT_TYPE', 'UNIT_INDEX_X', 'UNIT_INDEX_Y']
        if not all(col in df.columns for col in required_columns):
            st.error(f"The uploaded file is missing a required column: {required_columns}")
            return pd.DataFrame()
            
        df = df[required_columns]
        df.dropna(subset=required_columns, inplace=True)
        df['UNIT_INDEX_X'] = df['UNIT_INDEX_X'].astype(int)
        df['UNIT_INDEX_Y'] = df['UNIT_INDEX_Y'].astype(int)
        df['DEFECT_TYPE'] = df['DEFECT_TYPE'].str.strip()
        
    else:
        st.sidebar.info("No file uploaded. Displaying sample data.")
        total_rows, total_cols = 2 * panel_rows, 2 * panel_cols
        number_of_defects = 500
        
        st.sidebar.write("Random Quadrant Probabilities:", np.round(quadrant_probabilities, 2))
        
        quadrant_choices = np.random.choice(
            ['Q1', 'Q2', 'Q3', 'Q4'],
            size=number_of_defects,
            p=quadrant_probabilities
        )

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
        df['QUADRANT'] = quadrant_choices
        
    # --- Common Processing for both loaded and sample data ---
    plot_x_base = df['UNIT_INDEX_Y'] % panel_cols
    plot_y_base = df['UNIT_INDEX_X'] % panel_rows
    x_offset = np.where(df['UNIT_INDEX_Y'] >= panel_cols, panel_cols + gap_size, 0)
    y_offset = np.where(df['UNIT_INDEX_X'] >= panel_rows, panel_rows + gap_size, 0)
    df['plot_x'] = plot_x_base + x_offset + np.random.rand(len(df)) * 0.8 + 0.1
    df['plot_y'] = plot_y_base + y_offset + np.random.rand(len(df)) * 0.8 + 0.1
    
    return df

# ==============================================================================
# --- STREAMLIT APP LAYOUT ---
# ==============================================================================

def main():
    st.set_page_config(layout="wide")
    st.title("Defect Analysis App")
    

    st.sidebar.header("Input Parameters")
    
    uploaded_file = st.sidebar.file_uploader("Upload an Excel file", type=["xlsx"])
    panel_rows = st.sidebar.number_input("Panel Rows", min_value=1, value=10, step=1)
    panel_cols = st.sidebar.number_input("Panel Columns", min_value=1, value=10, step=1)
    gap_size = st.sidebar.number_input("Gap Size", min_value=0, value=2, step=1)
    
    # --- Generate probabilities here to bypass the cache ---
    random_weights = np.random.rand(4)
    quadrant_probabilities = random_weights / random_weights.sum()

    # --- Load and display data, passing the probabilities ---
    df_defects = load_data(uploaded_file, panel_rows, panel_cols, gap_size, quadrant_probabilities)
    
    if not df_defects.empty:
        st.subheader("Raw Data Preview")
        st.dataframe(df_defects.head())

if __name__ == "__main__":
    main()

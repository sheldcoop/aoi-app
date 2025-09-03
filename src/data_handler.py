# app.py
# This is the main script to run the Streamlit app.

import streamlit as st
# Import the functions from your data handler module
from src.data_handler import generate_sample_data, load_uploaded_file, process_data

# ==============================================================================
# --- STREAMLIT APP LAYOUT ---
# ==============================================================================

def main():
    st.set_page_config(layout="wide")
    st.title("Defect Analysis App")

    # --- Sidebar for user inputs ---
    st.sidebar.header("Input Parameters")
    
    uploaded_file = st.sidebar.file_uploader("Upload an Excel file", type=["xlsx"])
    panel_rows = st.sidebar.number_input("Panel Rows", min_value=1, value=10, step=1)
    panel_cols = st.sidebar.number_input("Panel Columns", min_value=1, value=10, step=1)
    gap_size = st.sidebar.number_input("Gap Size", min_value=0, value=2, step=1)
    
    # --- Logic to load data from the correct source ---
    if uploaded_file is not None:
        # If a file is uploaded, use the cached function to load it
        df_raw = load_uploaded_file(uploaded_file)
    else:
        # If no file is present, use the non-cached function to get new random data
        df_raw = generate_sample_data(panel_rows, panel_cols)
        
    # --- Common processing step for whichever data source was used ---
    df_defects = process_data(df_raw, panel_rows, panel_cols, gap_size)
    
    # --- Display the results ---
    if not df_defects.empty:
        st.subheader("Processed Data Preview")
        st.dataframe(df_defects.head())
        
        # You can add your plots and other analyses here, for example:
        # st.subheader("Defect Scatter Plot")
        # st.scatter_chart(df_defects, x='plot_x', y='plot_y')

if __name__ == "__main__":
    main()

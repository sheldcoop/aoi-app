# app.py
# Main application file for the Defect Analysis Streamlit Dashboard.
# This script serves as the main entry point and the "Defect Map" page.

import streamlit as st
import pandas as pd
import numpy as np

# Import our modularized functions
from src.config import BACKGROUND_COLOR, TEXT_COLOR
from src.data_handler import load_data
from src.reporting import generate_excel_report
from src.views import render_defect_view

# ==============================================================================
# --- App Configuration and State Management ---
# ==============================================================================

st.set_page_config(layout="wide", page_title="Defect Map Analysis")

# Initialize session state variables
if 'analysis_run' not in st.session_state:
    st.session_state.analysis_run = False
if 'processed_df' not in st.session_state:
    st.session_state.processed_df = pd.DataFrame()
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = None

# --- Custom CSS ---
st.markdown(f"""
    <style>
        .reportview-container {{ background-color: {BACKGROUND_COLOR}; }}
        .sidebar .sidebar-content {{ background-color: #2E2E2E; }}
        h1, h2, h3, .stRadio, .stSelectbox, .stNumberInput {{ color: {TEXT_COLOR}; }}
    </style>
""", unsafe_allow_html=True)

st.title("Defect Map View")

# ==============================================================================
# --- Sidebar Control Panel ---
# ==============================================================================

with st.sidebar:
    st.header("Control Panel")
    st.divider()

    st.subheader("Data Source")
    uploaded_files = st.file_uploader(
        "Upload Your Defect Data (Excel)",
        type=["xlsx", "xls"],
        accept_multiple_files=True,
        key="file_uploader"
    )
    
    st.divider()

    if st.button("Run Analysis", use_container_width=True):
        st.session_state.analysis_run = True
        st.session_state.uploaded_files = uploaded_files
        # Clear previous data when a new analysis is run
        if 'processed_df' in st.session_state:
            del st.session_state['processed_df']
            load_data.clear() # Clear the cache as well

    st.subheader("Configuration")
    panel_rows = st.number_input("Panel Rows", min_value=2, max_value=50, value=7)
    panel_cols = st.number_input("Panel Columns", min_value=2, max_value=50, value=7)

    st.divider()

    st.subheader("Analysis Controls")
    quadrant_selection = st.selectbox("Select Quadrant", ["All", "Q1", "Q2", "Q3", "Q4"])

    # Add controls for cross-page filtering
    if 'selected_defect' in st.session_state:
        st.divider()
        st.subheader("Cross-Filter")
        st.info(f"Defect type '{st.session_state.selected_defect}' selected from Pareto chart.")

        st.session_state.filter_by_defect = st.checkbox("Apply Pareto Selection", key="filter_by_defect_box")

        if st.button("Clear Selection"):
            del st.session_state.selected_defect
            st.rerun()

# ==============================================================================
# --- Main Page Logic ---
# ==============================================================================

if st.session_state.get('analysis_run', False):
    # Use files from session state to maintain consistency across pages
    files_to_process = st.session_state.get('uploaded_files', [])

    # Load data if not already in session state
    if 'processed_df' not in st.session_state or st.session_state.processed_df.empty:
        full_df = load_data(files_to_process, panel_rows, panel_cols)
        if not full_df.empty:
            full_df['jitter_x'] = np.random.rand(len(full_df)) * 0.8 + 0.1
            full_df['jitter_y'] = np.random.rand(len(full_df)) * 0.8 + 0.1
            st.session_state.processed_df = full_df.copy()
        else:
            st.session_state.processed_df = pd.DataFrame()

    processed_df = st.session_state.get('processed_df', pd.DataFrame())

    if processed_df.empty:
        st.warning("No data to display. Please upload valid Excel file(s) and click 'Run Analysis' in the sidebar.")
        st.stop()

    # Add Download Report Button to Sidebar (only if data is loaded)
    with st.sidebar:
        st.divider()
        st.subheader("Reporting")
        excel_report_bytes = generate_excel_report(processed_df, panel_rows, panel_cols)
        st.download_button(
            label="Download Full Report",
            data=excel_report_bytes,
            file_name="full_defect_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # Filter data based on quadrant selection
    display_df = processed_df[
        processed_df['QUADRANT'] == quadrant_selection
    ] if quadrant_selection != "All" else processed_df.copy()

    # Apply cross-filter if selected
    if st.session_state.get('selected_defect') and st.session_state.get('filter_by_defect', False):
        selected_defect = st.session_state.selected_defect
        display_df = display_df[display_df['DEFECT_TYPE'] == selected_defect]
        st.write(f"### Showing filtered results for: {selected_defect}")

    # Render the main defect view
    render_defect_view(display_df, quadrant_selection, panel_rows, panel_cols)

else:
    st.info("Welcome! Please upload your Excel file(s) and click 'Run Analysis' in the sidebar to begin.")

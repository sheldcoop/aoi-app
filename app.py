# app.py

"""
Main application file for the Defect Analysis Streamlit Dashboard.
This script acts as the main entry point and orchestrates the UI and logic.
"""

import streamlit as st
import pandas as pd
import numpy as np

# Import our modularized functions
from src.config import BACKGROUND_COLOR, TEXT_COLOR
from src.data_handler import load_data
from src.reporting import generate_excel_report
from src.views import render_defect_view, render_pareto_view, render_summary_view

# ==============================================================================
# --- STREAMLIT APP MAIN LOGIC ---
# ==============================================================================

def main():
    """
    Main function to run the Streamlit application.
    """
    # --- App Configuration ---
    st.set_page_config(layout="wide", page_title="Panel Defect Analysis")
    
    # --- STATE MANAGEMENT INITIALIZATION ---
    if 'analysis_run' not in st.session_state:
        st.session_state.analysis_run = False
    # State to store processed data for stable jitter
    if 'processed_df' not in st.session_state:
        st.session_state.processed_df = pd.DataFrame()

    def reset_analysis_state():
        st.session_state.analysis_run = False
        st.session_state.processed_df = pd.DataFrame() # Also reset our new state
        load_data.clear()

    # --- Apply Custom CSS for a Professional UI ---
    st.markdown(f"""
        <style>
            /* Main app background */
            .reportview-container {{
                background-color: {BACKGROUND_COLOR};
            }}
            /* Sidebar styling */
            .sidebar .sidebar-content {{
                background-color: #2E2E2E; /* Darker grey for control panel feel */
                border-right: 2px solid #4A4A4A;
            }}
            /* Center the main title */
            h1 {{
                text-align: center;
                padding-bottom: 20px;
            }}
            /* General text color */
            body, h2, h3, .stRadio, .stSelectbox, .stNumberInput {{
                color: {TEXT_COLOR};
            }}
            /* Style the KPI metric labels and values */
            .st-emotion-cache-1g8w9s4 p {{ /* Metric Label */
                color: {TEXT_COLOR};
                font-size: 16px;
            }}
             .st-emotion-cache-fplge9 div {{ /* Metric Value */
                font-size: 28px;
            }}
        </style>
    """, unsafe_allow_html=True)
    
    st.title("Panel Defect Analysis Tool")

    # --- Sidebar Control Panel ---
    with st.sidebar:
        st.header("Control Panel")
        st.divider()
        
        st.subheader("Data Source")
        uploaded_files = st.file_uploader(
            "Upload Your Defect Data (Excel)",
            type=["xlsx", "xls"],
            accept_multiple_files=True,
            on_change=reset_analysis_state
        )
        
        st.divider()

        if st.button("Run Analysis", use_container_width=True):
            st.session_state.analysis_run = True
        
        st.subheader("Configuration")
        panel_rows = st.number_input("Panel Rows", min_value=2, max_value=50, value=7)
        panel_cols = st.number_input("Panel Columns", min_value=2, max_value=50, value=7)
        gap_size = 1 

        st.divider()

        st.subheader("Analysis Controls")
        view_mode = st.radio("Select View", ["Defect View", "Pareto View", "Summary View"])
        quadrant_selection = st.selectbox("Select Quadrant", ["All", "Q1", "Q2", "Q3", "Q4"])

    # --- Main Application Logic ---
    if st.session_state.analysis_run:
        full_df = load_data(uploaded_files, panel_rows, panel_cols)

        if full_df.empty:
            st.warning("No data to display. Please upload valid Excel file(s) and click 'Run Analysis'.")
            st.stop()
        
        # Calculate jitter ONCE and store it in session state for stability
        if st.session_state.processed_df.empty or 'jitter_x' not in st.session_state.processed_df.columns:
            full_df['jitter_x'] = np.random.rand(len(full_df)) * 0.8 + 0.1
            full_df['jitter_y'] = np.random.rand(len(full_df)) * 0.8 + 0.1
            st.session_state.processed_df = full_df.copy()

        # Use the processed dataframe from session state from now on
        display_df = st.session_state.processed_df[
            st.session_state.processed_df['QUADRANT'] == quadrant_selection
        ] if quadrant_selection != "All" else st.session_state.processed_df.copy()

        # --- Add Download Report Button to Sidebar ---
        with st.sidebar:
            st.divider()
            st.subheader("Reporting")
            excel_report_bytes = generate_excel_report(full_df, panel_rows, panel_cols)
            st.download_button(
                label="Download Full Report",
                data=excel_report_bytes,
                file_name="full_defect_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        # --- Main content area ---
        if view_mode == "Defect View":
            render_defect_view(display_df, quadrant_selection, panel_rows, panel_cols, gap_size)
        elif view_mode == "Pareto View":
            render_pareto_view(display_df, quadrant_selection)
        elif view_mode == "Summary View":
            render_summary_view(display_df, full_df, quadrant_selection, panel_rows, panel_cols)
    else:
        st.info("Upload your Excel file(s) and click 'Run Analysis' to begin.")

if __name__ == '__main__':
    main()

# pages/1_Pareto_Analysis.py

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Adjust path to import from src
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import BACKGROUND_COLOR, PLOT_AREA_COLOR, TEXT_COLOR
from src.data_handler import load_data
from src.plotting import create_pareto_trace
from streamlit_plotly_events import streamlit_plotly_events

st.set_page_config(layout="wide", page_title="Pareto Analysis")

st.title("Pareto Analysis")

# --- Sidebar Control Panel ---
# This is repeated across pages to ensure consistent controls
with st.sidebar:
    st.header("Control Panel")
    st.divider()

    st.subheader("Data Source")
    uploaded_files = st.file_uploader(
        "Upload Your Defect Data (Excel)",
        type=["xlsx", "xls"],
        accept_multiple_files=True,
        key="file_uploader" # Use a unique key
    )

    st.divider()

    if st.button("Run Analysis", use_container_width=True):
        if 'analysis_run' not in st.session_state or not st.session_state.analysis_run:
            st.session_state.analysis_run = True
            # Clear previous data when a new analysis is run
            if 'processed_df' in st.session_state:
                del st.session_state.processed_df

    st.subheader("Configuration")
    panel_rows = st.number_input("Panel Rows", min_value=2, max_value=50, value=7)
    panel_cols = st.number_input("Panel Columns", min_value=2, max_value=50, value=7)

    st.divider()

    st.subheader("Analysis Controls")
    quadrant_selection = st.selectbox("Select Quadrant", ["All", "Q1", "Q2", "Q3", "Q4"])

# --- Main Application Logic ---
if st.session_state.get('analysis_run', False):
    # Load data if not already in session state
    if 'processed_df' not in st.session_state:
        full_df = load_data(uploaded_files, panel_rows, panel_cols)
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

    # Filter data based on quadrant selection
    display_df = processed_df[
        processed_df['QUADRANT'] == quadrant_selection
    ] if quadrant_selection != "All" else processed_df.copy()

    # --- Render Pareto Chart ---
    st.header(f"Pareto Analysis for Quadrant: {quadrant_selection}")

    fig = go.Figure()
    pareto_traces = create_pareto_trace(display_df)
    for trace in pareto_traces:
        fig.add_trace(trace)

    fig.update_layout(
        title=dict(text=f"Pareto Analysis - Quadrant: {quadrant_selection} ({len(display_df)} Defects)", font=dict(color=TEXT_COLOR), x=0.5),
        xaxis=dict(title="Defect Type", title_font=dict(color=TEXT_COLOR), tickfont=dict(color=TEXT_COLOR)),
        yaxis=dict(
            title="Count",
            title_font=dict(color=TEXT_COLOR),
            tickfont=dict(color=TEXT_COLOR)
        ),
        yaxis2=dict(
            title="Cumulative Percentage",
            title_font=dict(color="crimson"),
            tickfont=dict(color="crimson"),
            overlaying='y',
            side='right',
            range=[0, 105],
            showgrid=False,
            tickformat='.0f'
        ),
        plot_bgcolor=PLOT_AREA_COLOR,
        paper_bgcolor=BACKGROUND_COLOR,
        showlegend=True,
        height=600,
        legend=dict(x=0.01, y=0.99, xanchor='left', yanchor='top', font=dict(color=TEXT_COLOR))
    )
    # Use streamlit_plotly_events to capture clicks
    selected_points = streamlit_plotly_events(
        fig,
        click_event=True,
        key="pareto_click"
    )

    # If a bar is clicked, store the defect type in session state
    if selected_points and 'x' in selected_points[0]:
        selected_defect = selected_points[0]['x']
        st.session_state.selected_defect = selected_defect
        st.success(f"Selected '{selected_defect}'. Go to the Defect Map page to see the filtered view.")

else:
    st.info("Upload your Excel file(s) and click 'Run Analysis' in the sidebar to begin.")

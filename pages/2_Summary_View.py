# pages/2_Summary_View.py

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
from src.plotting import create_grouped_pareto_trace

st.set_page_config(layout="wide", page_title="Summary View")

st.title("Statistical Summary")

# --- Sidebar Control Panel ---
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
        if 'analysis_run' not in st.session_state or not st.session_state.analysis_run:
            st.session_state.analysis_run = True
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

    # --- Render Summary View ---
    st.header(f"Statistical Summary for Quadrant: {quadrant_selection}")

    if display_df.empty:
        st.info("No defects to summarize in the selected quadrant.")
        st.stop()

    if quadrant_selection != "All":
        total_defects = len(display_df)
        total_cells = panel_rows * panel_cols
        defective_cells = len(display_df[['UNIT_INDEX_X', 'UNIT_INDEX_Y']].drop_duplicates())
        defect_density = total_defects / total_cells if total_cells > 0 else 0
        yield_estimate = (total_cells - defective_cells) / total_cells if total_cells > 0 else 0

        st.markdown("### Key Performance Indicators (KPIs)")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Defect Count", f"{total_defects:,}")
        col2.metric("Defect Density", f"{defect_density:.2f} defects/cell")
        col3.metric("Yield Estimate", f"{yield_estimate:.2%}")

        st.divider()
        st.markdown("### Top Defect Types")
        top_offenders = display_df['DEFECT_TYPE'].value_counts().reset_index()
        top_offenders.columns = ['Defect Type', 'Count']
        top_offenders['Percentage'] = (top_offenders['Count'] / total_defects) * 100
        st.dataframe(top_offenders.style.format({'Percentage': '{:.2f}%'}).background_gradient(cmap='Reds', subset=['Count']), use_container_width=True)

    else: # "All" is selected, show the Quarterly Breakdown
        st.markdown("### Quarterly KPI Breakdown")

        kpi_data = []
        quadrants = ['Q1', 'Q2', 'Q3', 'Q4']
        for quad in quadrants:
            quad_df = processed_df[processed_df['QUADRANT'] == quad]
            total_defects = len(quad_df)
            density = total_defects / (panel_rows * panel_cols) if (panel_rows * panel_cols) > 0 else 0
            kpi_data.append({"Quadrant": quad, "Total Defects": total_defects, "Defect Density": f"{density:.2f}"})

        kpi_df = pd.DataFrame(kpi_data)
        st.dataframe(kpi_df, use_container_width=True)

        st.divider()
        st.markdown("### Defect Distribution by Quadrant")
        fig = go.Figure()
        grouped_traces = create_grouped_pareto_trace(processed_df)
        for trace in grouped_traces: fig.add_trace(trace)

        fig.update_layout(
            barmode='group',
            xaxis=dict(title="Defect Type", title_font=dict(color=TEXT_COLOR), tickfont=dict(color=TEXT_COLOR)),
            yaxis=dict(title="Count", title_font=dict(color=TEXT_COLOR), tickfont=dict(color=TEXT_COLOR)),
            plot_bgcolor=PLOT_AREA_COLOR,
            paper_bgcolor=BACKGROUND_COLOR,
            legend=dict(font=dict(color=TEXT_COLOR)),
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Upload your Excel file(s) and click 'Run Analysis' in the sidebar to begin.")

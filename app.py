# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events

# Import modularized functions
from src.config import BACKGROUND_COLOR, TEXT_COLOR
from src.data_handler import load_and_process_data
from src.plotting import create_dynamic_grid, create_defect_traces, create_true_pareto_chart
from src.reporting import generate_excel_report

# ==============================================================================
# --- STREAMLIT APP MAIN LOGIC ---
# ==============================================================================

def main():
    """ Main function to run the Streamlit application. """
    st.set_page_config(layout="wide", page_title="Panel Defect Analysis")

    # --- STATE MANAGEMENT INITIALIZATION ---
    if 'processed_df' not in st.session_state:
        st.session_state.processed_df = pd.DataFrame()
    if 'visible_defects' not in st.session_state:
        st.session_state.visible_defects = []
    if 'pareto_filter' not in st.session_state:
        st.session_state.pareto_filter = None

    def reset_app_state():
        # Clear cached data
        load_and_process_data.clear()
        # Reset all session state variables
        st.session_state.processed_df = pd.DataFrame()
        st.session_state.visible_defects = []
        st.session_state.pareto_filter = None

    # --- UI STYLING ---
    st.markdown(f"<style> .reportview-container {{ background-color: {BACKGROUND_COLOR}; }} </style>", unsafe_allow_html=True)
    st.title("Panel Defect Analysis Tool")

    # --- SIDEBAR CONTROL PANEL ---
    with st.sidebar:
        st.header("Control Panel")
        
        uploaded_files = st.file_uploader(
            "Upload Defect Data (Excel)",
            type=["xlsx", "xls"],
            accept_multiple_files=True,
            on_change=reset_app_state
        )

        if not uploaded_files:
            st.info("Please upload data file(s) to begin analysis.")
            st.stop()
        
        st.divider()
        st.subheader("Panel Configuration")
        panel_rows = st.number_input("Panel Rows", min_value=2, max_value=50, value=7)
        panel_cols = st.number_input("Panel Columns", min_value=2, max_value=50, value=7)
        
        st.divider()
        st.subheader("Analysis Controls")
        quadrant_selection = st.selectbox("Filter by Quadrant", ["All", "Q1", "Q2", "Q3", "Q4"])

        # Process data only once after upload and config is set
        full_df = load_and_process_data(uploaded_files, panel_rows, panel_cols, gap_size=1)
        if full_df.empty:
            st.warning("No data found in the uploaded files.")
            st.stop()
        
        st.session_state.processed_df = full_df

        # --- DYNAMIC & INTERACTIVE LEGEND IN SIDEBAR ---
        st.divider()
        st.subheader("Toggle Defect Visibility")
        defect_types = sorted(st.session_state.processed_df['DEFECT_TYPE'].unique())
        
        # Initialize visible defects on first run
        if not st.session_state.visible_defects:
            st.session_state.visible_defects = defect_types

        visible = []
        for defect in defect_types:
            if st.checkbox(defect, value=(defect in st.session_state.visible_defects), key=f"check_{defect}"):
                visible.append(defect)
        st.session_state.visible_defects = visible

        # --- PARETO FILTER CONTROLS ---
        if st.session_state.pareto_filter:
            st.warning(f"Map filtered by: **{st.session_state.pareto_filter}**")
            if st.button("Clear Pareto Filter", use_container_width=True):
                st.session_state.pareto_filter = None
                st.rerun() # Immediately rerun to update the view
        
        st.divider()
        st.subheader("Reporting")
        excel_report_bytes = generate_excel_report(st.session_state.processed_df, panel_rows, panel_cols)
        st.download_button(
            label="Download Full Report",
            data=excel_report_bytes,
            file_name="full_defect_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    # --- DATA FILTERING LOGIC ---
    # Start with the full, processed dataset
    working_df = st.session_state.processed_df.copy()

    # 1. Apply Quadrant Filter
    if quadrant_selection != "All":
        working_df = working_df[working_df['QUADRANT'] == quadrant_selection]

    # This df is used for KPIs and Pareto (unaffected by other filters)
    kpi_pareto_df = working_df.copy()

    # 2. Apply Pareto Click Filter (if any)
    if st.session_state.pareto_filter:
        working_df = working_df[working_df['DEFECT_TYPE'] == st.session_state.pareto_filter]

    # 3. Apply Visibility Toggles
    working_df = working_df[working_df['DEFECT_TYPE'].isin(st.session_state.visible_defects)]
    
    # Final dataframe for the map
    display_df = working_df

    # --- MAIN CONTENT AREA ---
    # --- PERSISTENT KPIs ---
    total_defects = len(kpi_pareto_df)
    yield_estimate = 1 - (len(kpi_pareto_df[['UNIT_INDEX_X', 'UNIT_INDEX_Y']].drop_duplicates()) / ((panel_rows * panel_cols * 4))) if total_defects > 0 else 1
    
    st.markdown("### Key Performance Indicators")
    kpi1, kpi2 = st.columns(2)
    kpi1.metric("Total Defects in View", f"{total_defects:,}")
    kpi2.metric("Estimated Yield", f"{yield_estimate:.2%}")
    st.divider()

    # --- UNIFIED DASHBOARD LAYOUT ---
    col1, col2 = st.columns([2, 1]) # 2/3 width for map, 1/3 for pareto

    with col1:
        st.subheader("Defect Map")
        fig_map = go.Figure()

        # Calculate plot coordinates dynamically based on panel config
        display_df['plot_x'] = (display_df['UNIT_INDEX_Y'] % panel_cols) + display_df['jitter_x']
        display_df['plot_y'] = (display_df['UNIT_INDEX_X'] % panel_rows) + display_df['jitter_y']
        
        # Offset for quadrants
        x_offset = np.where(display_df['UNIT_INDEX_Y'] >= panel_cols, panel_cols, 0)
        y_offset = np.where(display_df['UNIT_INDEX_X'] >= panel_rows, panel_rows, 0)
        display_df['plot_x'] += x_offset
        display_df['plot_y'] += y_offset

        defect_traces = create_defect_traces(display_df, st.session_state.visible_defects)
        for trace in defect_traces:
            fig_map.add_trace(trace)

        fig_map.update_layout(
            title=f"Displaying {len(display_df)} of {total_defects} Defects",
            xaxis=dict(range=[-1, 2 * panel_cols + 1], showgrid=False, zeroline=False),
            yaxis=dict(range=[-1, 2 * panel_rows + 1], scaleanchor="x", scaleratio=1, showgrid=False, zeroline=False),
            plot_bgcolor=PLOT_AREA_COLOR,
            paper_bgcolor=BACKGROUND_COLOR,
            shapes=create_dynamic_grid(panel_rows, panel_cols),
            height=700,
            showlegend=False, # Legend is now in the sidebar
            margin=dict(l=10, r=10, t=40, b=10)
        )
        st.plotly_chart(fig_map, use_container_width=True)

    with col2:
        st.subheader("Analysis")
        pareto_fig = create_true_pareto_chart(kpi_pareto_df)
        
        # Use streamlit-plotly-events to capture clicks
        selected_points = plotly_events(pareto_fig, click_event=True, key="pareto_click")

        if selected_points:
            # The click event returns a list of dicts, we need the first one
            clicked_defect_type = selected_points[0].get('customdata')
            if clicked_defect_type:
                st.session_state.pareto_filter = clicked_defect_type
                st.rerun()

        # Display Summary Table
        st.markdown("##### Defect Counts")
        summary_df = kpi_pareto_df['DEFECT_TYPE'].value_counts().reset_index()
        summary_df.columns = ['Defect Type', 'Count']
        st.dataframe(summary_df, use_container_width=True, height=250)


if __name__ == '__main__':
    main()

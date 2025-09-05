# app.py

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Import our modularized functions
from src.config import BACKGROUND_COLOR, PLOT_AREA_COLOR, GRID_COLOR, TEXT_COLOR
from src.data_handler import load_data # CHANGE 5: Add @st.cache_data to this function in its file!
from src.plotting import (
    create_dynamic_grid, create_single_panel_grid, create_defect_traces,
    create_pareto_trace, create_grouped_pareto_trace
)
from src.reporting import generate_excel_report

# ==============================================================================
# --- STREAMLIT APP MAIN LOGIC ---
# ==============================================================================

def main():
    """
    Main function to run the Streamlit application.
    """
    st.set_page_config(layout="wide", page_title="Panel Defect Analysis")
    
    # --- STATE MANAGEMENT INITIALIZATION ---
    if 'analysis_run' not in st.session_state:
        st.session_state.analysis_run = False
    # CHANGE 3: Add state for stable jitter
    if 'processed_df' not in st.session_state:
        st.session_state.processed_df = pd.DataFrame()

    def reset_analysis_state():
        st.session_state.analysis_run = False
        st.session_state.processed_df = pd.DataFrame()
        load_data.clear()

    # (Your CSS remains the same, so it's omitted for brevity)
    st.markdown(...) 
    
    st.title("Panel Defect Analysis Tool")

    # (Your Sidebar remains the same, so it's omitted for brevity)
    with st.sidebar:
        ...

    # --- Main Application Logic ---
    if st.session_state.analysis_run:
        full_df = load_data(uploaded_files, panel_rows, panel_cols, gap_size)

        if full_df.empty:
            st.warning("No data to display. Please upload valid Excel file(s) and click 'Run Analysis'.")
            st.stop()
            
        # CHANGE 3: Calculate jitter ONCE and store in session state
        if st.session_state.processed_df.empty or not st.session_state.processed_df.equals(full_df):
            full_df['jitter_x'] = np.random.rand(len(full_df)) * 0.8 + 0.1
            full_df['jitter_y'] = np.random.rand(len(full_df)) * 0.8 + 0.1
            st.session_state.processed_df = full_df.copy()

        display_df = st.session_state.processed_df[
            st.session_state.processed_df['QUADRANT'] == quadrant_selection
        ] if quadrant_selection != "All" else st.session_state.processed_df.copy()

        # (Your Download Button logic remains the same)
        with st.sidebar:
            ...

        # --- Main content area ---
        if view_mode == "Defect View":
            
            # CHANGE 7: Define a base layout to keep code DRY
            base_layout = dict(
                plot_bgcolor=BACKGROUND_COLOR, 
                paper_bgcolor=BACKGROUND_COLOR,
                height=900, # CHANGE 9: Standardize height
                title_font=dict(color=TEXT_COLOR),
                title_x=0.5, # CHANGE 4: Center the title
                margin=dict(l=40, r=40, t=80, b=40), # CHANGE 6: Add more breathing room
                # CHANGE 2: Move legend to the right
                legend=dict(
                    orientation="v", 
                    yanchor="top", 
                    y=1, 
                    xanchor="left", 
                    x=1.02,
                    title_font=dict(color=TEXT_COLOR), 
                    font=dict(color=TEXT_COLOR)
                )
            )

            fig = go.Figure()

            if quadrant_selection == "All":
                FIGURE_WIDTH, FIGURE_HEIGHT = 900, 900
                MARGIN = dict(l=20, r=20, t=50, b=20)
                layout_data = create_dynamic_grid(panel_rows, panel_cols, gap_size, FIGURE_WIDTH, FIGURE_HEIGHT, MARGIN)
                cell_size = layout_data['cell_size']
                
                # Use jitter from session state
                display_df['plot_x'] = ((display_df['UNIT_INDEX_Y'] % panel_cols) + display_df['jitter_x']) * cell_size
                display_df['plot_y'] = ((display_df['UNIT_INDEX_X'] % panel_rows) + display_df['jitter_y']) * cell_size
                
                panel_width_units = panel_cols * cell_size
                panel_height_units = panel_rows * cell_size
                x_offset = np.where(display_df['UNIT_INDEX_Y'] >= panel_cols, panel_width_units + layout_data['gap_size_units'], 0)
                y_offset = np.where(display_df['UNIT_INDEX_X'] >= panel_rows, panel_height_units + layout_data['gap_size_units'], 0)
                display_df['plot_x'] += x_offset
                display_df['plot_y'] += y_offset

                defect_traces = create_defect_traces(display_df)
                for trace in defect_traces: fig.add_trace(trace)
                
                fig.update_layout(base_layout)
                fig.update_layout(
                    title_text=f"Panel Defect Map - Quadrant: {quadrant_selection} ({len(display_df)} Defects)",
                    xaxis=dict(range=layout_data['x_axis_range'], tickvals=layout_data['x_tick_pos'], ticktext=list(range(2*panel_cols)), showgrid=False, zeroline=False),
                    yaxis=dict(range=layout_data['y_axis_range'], tickvals=layout_data['y_tick_pos'], ticktext=list(range(2*panel_rows)), scaleanchor="x", scaleratio=1, showgrid=False, zeroline=False),
                    shapes=layout_data['shapes']
                )

            else: # Single Quadrant View
                plot_shapes = create_single_panel_grid(panel_rows, panel_cols)

                # Use jitter from session state
                display_df['plot_x'] = (display_df['UNIT_INDEX_Y'] % panel_cols) + display_df['jitter_x']
                display_df['plot_y'] = (display_df['UNIT_INDEX_X'] % panel_rows) + display_df['jitter_y']

                defect_traces = create_defect_traces(display_df)
                for trace in defect_traces: fig.add_trace(trace)

                fig.update_layout(base_layout)
                fig.update_layout(
                    title_text=f"Panel Defect Map - Quadrant: {quadrant_selection} ({len(display_df)} Defects)",
                    xaxis=dict(range=[-1, panel_cols + 1], showgrid=True, zeroline=False, showticklabels=True),
                    yaxis=dict(range=[-1, panel_rows + 1], showgrid=True, zeroline=False, showticklabels=True, scaleanchor="x", scaleratio=1),
                    shapes=plot_shapes
                )

            # CHANGE 1: Center the plot using columns
            _, chart_col, _ = st.columns([1, 4, 1]) # Use a ratio to control centering width
            with chart_col:
                st.plotly_chart(fig, use_container_width=True)

        elif view_mode == "Pareto View":
            # CHANGE 8: Use columns for a better Pareto layout
            chart_col, summary_col = st.columns([2, 1])

            with chart_col:
                fig = go.Figure()
                pareto_trace = create_pareto_trace(display_df) # CHANGE 10: Sort data inside this function
                fig.add_trace(pareto_trace)
                
                fig.update_layout(
                    title=dict(text=f"Pareto Analysis - Quadrant: {quadrant_selection}", font=dict(color=TEXT_COLOR), x=0.5),
                    xaxis=dict(title="Defect Type", title_font=dict(color=TEXT_COLOR), tickfont=dict(color=TEXT_COLOR)),
                    yaxis=dict(title="Count", title_font=dict(color=TEXT_COLOR), tickfont=dict(color=TEXT_COLOR)),
                    plot_bgcolor=PLOT_AREA_COLOR, 
                    paper_bgcolor=BACKGROUND_COLOR,
                    showlegend=False,
                    height=700
                )
                st.plotly_chart(fig, use_container_width=True)

            with summary_col:
                st.markdown("### Defect Summary")
                st.markdown(f"**Total Defects in View:** {len(display_df)}")
                summary_table = display_df['DEFECT_TYPE'].value_counts().reset_index()
                summary_table.columns = ['Defect Type', 'Count']
                st.dataframe(summary_table, use_container_width=True, height=600)
                
        # (Your Summary View logic remains the same)
        elif view_mode == "Summary View":
            ...

    else:
        # CHANGE 10: Better initial welcome message
        _, col, _ = st.columns(3)
        with col:
            st.image("https://www.streamlit.io/images/brand/streamlit-logo-secondary-colormark-darktext.svg", width=300)
            st.info("### Welcome to the Panel Defect Analysis Tool!")
            st.write("Please upload your Excel file(s) and click **'Run Analysis'** in the sidebar to begin.")

if __name__ == '__main__':
    main()

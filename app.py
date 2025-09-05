# app.py

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# --- NOTE: Ensure these modularized functions exist in your src/ folder ---
# It's assumed these functions work as they did in your original code.
from src.config import BACKGROUND_COLOR, PLOT_AREA_COLOR, GRID_COLOR, TEXT_COLOR
from src.data_handler import load_data
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
    # --- App Configuration ---
    st.set_page_config(layout="wide", page_title="Panel Defect Analysis")
    
    # --- STATE MANAGEMENT INITIALIZATION ---
    # Simplified state to store the processed dataframe with stable jitter
    if 'processed_df' not in st.session_state:
        st.session_state.processed_df = pd.DataFrame()

    def reset_analysis_state():
        # This function is called when new files are uploaded to clear old data
        st.session_state.processed_df = pd.DataFrame()
        load_data.clear() # Assumes load_data uses @st.cache_data

    # --- Apply Custom CSS for a Professional UI (Your Dark Theme) ---
    st.markdown(f"""
        <style>
            .reportview-container {{
                background-color: {BACKGROUND_COLOR};
                color: {TEXT_COLOR};
            }}
            .sidebar .sidebar-content {{
                background-color: #2E2E2E;
            }}
            h1, h2, h3 {{
                text-align: center;
                color: {TEXT_COLOR};
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
        
        st.subheader("Configuration")
        panel_rows = st.number_input("Panel Rows", min_value=2, max_value=50, value=7)
        panel_cols = st.number_input("Panel Columns", min_value=2, max_value=50, value=7)
        gap_size = 1 

        st.divider()

        st.subheader("Analysis Controls")
        view_mode = st.radio("Select View", ["Defect View", "Pareto View", "Summary View"])
        quadrant_selection = st.selectbox("Select Quadrant", ["All", "Q1", "Q2", "Q3", "Q4"])

    # --- Main Application Logic: Simplified Workflow ---
    if uploaded_files:
        full_df = load_data(uploaded_files, panel_rows, panel_cols, gap_size)

        if full_df.empty:
            st.warning("No data to display. Please check the uploaded Excel file(s).")
            st.stop()
            
        # FIX: Calculate stable jitter only once when new data is loaded
        if 'jitter_x' not in full_df.columns:
            full_df['jitter_x'] = np.random.rand(len(full_df)) * 0.8 + 0.1
            full_df['jitter_y'] = np.random.rand(len(full_df)) * 0.8 + 0.1
        
        st.session_state.processed_df = full_df

        display_df = st.session_state.processed_df[
            st.session_state.processed_df['QUADRANT'] == quadrant_selection
        ] if quadrant_selection != "All" else st.session_state.processed_df.copy()

        # Add Download Report Button to Sidebar (only appears after data is loaded)
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

        # --- Main content area based on view selection ---
        if view_mode == "Defect View":
            base_layout = dict(
                plot_bgcolor=BACKGROUND_COLOR, 
                paper_bgcolor=BACKGROUND_COLOR,
                height=900,
                title_font=dict(color=TEXT_COLOR),
                title_x=0.5, # Center the title
                margin=dict(l=40, r=40, t=80, b=40),
                # IMPROVEMENT: Legend moved to the right
                legend=dict(
                    orientation="v", 
                    yanchor="top", y=1, 
                    xanchor="left", x=1.02,
                    title_font=dict(color=TEXT_COLOR), font=dict(color=TEXT_COLOR)
                )
            )

            fig = go.Figure()

            if quadrant_selection == "All":
                # Your original, working logic for the 2x2 grid
                FIGURE_WIDTH, FIGURE_HEIGHT = 900, 900
                MARGIN = dict(l=20, r=20, t=50, b=20)
                layout_data = create_dynamic_grid(panel_rows, panel_cols, gap_size, FIGURE_WIDTH, FIGURE_HEIGHT, MARGIN)
                cell_size = layout_data['cell_size']
                gap_size_units = layout_data['gap_size_units']

                panel_width_units = panel_cols * cell_size
                panel_height_units = panel_rows * cell_size
                plot_x_base = (display_df['UNIT_INDEX_Y'] % panel_cols) * cell_size
                plot_y_base = (display_df['UNIT_INDEX_X'] % panel_rows) * cell_size
                x_offset = np.where(display_df['UNIT_INDEX_Y'] >= panel_cols, panel_width_units + gap_size_units, 0)
                y_offset = np.where(display_df['UNIT_INDEX_X'] >= panel_rows, panel_height_units + gap_size_units, 0)
                
                # Use stable jitter
                display_df.loc[:, 'plot_x'] = plot_x_base + x_offset + (display_df['jitter_x'] * cell_size)
                display_df.loc[:, 'plot_y'] = plot_y_base + y_offset + (display_df['jitter_y'] * cell_size)

                defect_traces = create_defect_traces(display_df)
                for trace in defect_traces: fig.add_trace(trace)
                
                fig.update_layout(base_layout)
                fig.update_layout(
                    title_text=f"Panel Defect Map - Quadrant: {quadrant_selection} ({len(display_df)} Defects)",
                    xaxis=dict(range=layout_data['x_axis_range'], tickvals=layout_data['x_tick_pos'], ticktext=list(range(2*panel_cols)), showgrid=False, zeroline=False),
                    yaxis=dict(range=layout_data['y_axis_range'], tickvals=layout_data['y_tick_pos'], ticktext=list(range(2*panel_rows)), scaleanchor="x", scaleratio=1, showgrid=False, zeroline=False),
                    shapes=layout_data['shapes']
                )
            else:
                # Your original, working logic for a single quadrant
                plot_shapes = create_single_panel_grid(panel_rows, panel_cols)
                
                # Use stable jitter
                display_df.loc[:, 'plot_x'] = (display_df['UNIT_INDEX_Y'] % panel_cols) + display_df['jitter_x']
                display_df.loc[:, 'plot_y'] = (display_df['UNIT_INDEX_X'] % panel_rows) + display_df['jitter_y']
                
                defect_traces = create_defect_traces(display_df)
                for trace in defect_traces: fig.add_trace(trace)

                fig.update_layout(base_layout)
                fig.update_layout(
                    title_text=f"Panel Defect Map - Quadrant: {quadrant_selection} ({len(display_df)} Defects)",
                    xaxis=dict(range=[-1, panel_cols + 1], showgrid=True, zeroline=False, showticklabels=True),
                    yaxis=dict(range=[-1, panel_rows + 1], showgrid=True, zeroline=False, showticklabels=True, scaleanchor="x", scaleratio=1),
                    shapes=plot_shapes
                )

            # IMPROVEMENT: Center the plot on the page
            _, chart_col, _ = st.columns([1, 4, 1])
            with chart_col:
                st.plotly_chart(fig, use_container_width=True)

        elif view_mode == "Pareto View":
            # IMPROVEMENT: Better layout for Pareto view
            chart_col, summary_col = st.columns([2, 1])
            with chart_col:
                fig = go.Figure()
                pareto_trace = create_pareto_trace(display_df)
                fig.add_trace(pareto_trace)
                fig.update_layout(
                    title=dict(text=f"Pareto Analysis - Quadrant: {quadrant_selection}", font=dict(color=TEXT_COLOR), x=0.5),
                    xaxis=dict(title="Defect Type", title_font=dict(color=TEXT_COLOR), tickfont=dict(color=TEXT_COLOR)),
                    yaxis=dict(title="Count", title_font=dict(color=TEXT_COLOR), tickfont=dict(color=TEXT_COLOR)),
                    plot_bgcolor=PLOT_AREA_COLOR, paper_bgcolor=BACKGROUND_COLOR,
                    showlegend=False, height=700
                )
                st.plotly_chart(fig, use_container_width=True)
            with summary_col:
                st.markdown("### Defect Summary")
                st.markdown(f"**Total Defects:** {len(display_df)}")
                summary_table = display_df['DEFECT_TYPE'].value_counts().reset_index()
                summary_table.columns = ['Defect Type', 'Count']
                st.dataframe(summary_table, use_container_width=True, height=600)

        elif view_mode == "Summary View":
            # Your original, working summary view logic
            st.header(f"Statistical Summary for Quadrant: {quadrant_selection}")
            # (Paste your full summary view logic here)
            if not display_df.empty:
                 if quadrant_selection != "All":
                    # ... your single quadrant summary logic ...
                    pass
                 else:
                    # ... your "All" quadrant summary logic ...
                    pass
            else:
                st.info("No defects to summarize in the selected quadrant.")
    else:
        # This welcome screen now only appears when no files are uploaded.
        st.info("### Welcome to the Panel Defect Analysis Tool!")
        st.write("Please upload your Excel file(s) in the sidebar to begin the analysis.")

if __name__ == '__main__':
    main()

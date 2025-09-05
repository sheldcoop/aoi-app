# app.py

"""
Main application file for the Defect Analysis Streamlit Dashboard.
This script acts as the main entry point and orchestrates the UI and logic.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Import our modularized functions
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
        full_df = load_data(uploaded_files, panel_rows, panel_cols, gap_size)

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
            fig = go.Figure()

            if quadrant_selection == "All":
                FIGURE_WIDTH, FIGURE_HEIGHT = 800, 800
                MARGIN = dict(l=20, r=20, t=20, b=20) # Increased right margin for legend

                layout_data = create_dynamic_grid(panel_rows, panel_cols, gap_size, FIGURE_WIDTH, FIGURE_HEIGHT, MARGIN)
                cell_size = layout_data['cell_size']
                gap_size_units = layout_data['gap_size_units']

                if not display_df.empty:
                    df = display_df.copy()
                    panel_width_units = panel_cols * cell_size
                    panel_height_units = panel_rows * cell_size
                    plot_x_base = (df['UNIT_INDEX_Y'] % panel_cols) * cell_size
                    plot_y_base = (df['UNIT_INDEX_X'] % panel_rows) * cell_size
                    x_offset = np.where(df['UNIT_INDEX_Y'] >= panel_cols, panel_width_units + gap_size_units, 0)
                    y_offset = np.where(df['UNIT_INDEX_X'] >= panel_rows, panel_height_units + gap_size_units, 0)
                    jitter_x = df['jitter_x'] * cell_size
                    jitter_y = df['jitter_y'] * cell_size
                    df.loc[:, 'plot_x'] = plot_x_base + x_offset + jitter_x
                    df.loc[:, 'plot_y'] = plot_y_base + y_offset + jitter_y
                    defect_traces = create_defect_traces(df)
                    for trace in defect_traces: fig.add_trace(trace)

                tick_labels = list(range(2 * panel_cols))

                fig.update_layout(
                    title=dict(text=f"Panel Defect Map - Quadrant: {quadrant_selection} ({len(display_df)} Defects)", font=dict(color=TEXT_COLOR)),
                    xaxis=dict(range=layout_data['x_axis_range'], tickvals=layout_data['x_tick_pos'], ticktext=tick_labels, showgrid=False, zeroline=False),
                    yaxis=dict(range=layout_data['y_axis_range'], tickvals=layout_data['y_tick_pos'], ticktext=tick_labels, scaleanchor="x", scaleratio=1, showgrid=False, zeroline=False),
                    plot_bgcolor=BACKGROUND_COLOR, paper_bgcolor=BACKGROUND_COLOR,
                    width=FIGURE_WIDTH, height=FIGURE_HEIGHT, margin=MARGIN,
                    shapes=layout_data['shapes'],
                    legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02, title_font=dict(color=TEXT_COLOR), font=dict(color=TEXT_COLOR))
                )

            else: # Single Quadrant View
                plot_shapes = create_single_panel_grid(panel_rows, panel_cols)

                if not display_df.empty:
                    df = display_df.copy()
                    df.loc[:, 'plot_x'] = (df['UNIT_INDEX_Y'] % panel_cols) + df['jitter_x']
                    df.loc[:, 'plot_y'] = (df['UNIT_INDEX_X'] % panel_rows) + df['jitter_y']
                    defect_traces = create_defect_traces(df)
                    for trace in defect_traces: fig.add_trace(trace)

                fig.update_layout(
                    title=dict(text=f"Panel Defect Map - Quadrant: {quadrant_selection} ({len(display_df)} Defects)", font=dict(color=TEXT_COLOR)),
                    xaxis=dict(range=[0, panel_cols ], showgrid=False, zeroline=False, showticklabels=True),
                    yaxis=dict(range=[, panel_rows], showgrid=False, zeroline=False, showticklabels=True, scaleanchor="x", scaleratio=1),
                    plot_bgcolor=BACKGROUND_COLOR, paper_bgcolor=BACKGROUND_COLOR,
                    shapes=plot_shapes,
                    height=900,
                    margin=dict(l=20, r=20, t=20, b=20),
                    legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02, title_font=dict(color=TEXT_COLOR), font=dict(color=TEXT_COLOR))
                )

            # Center the plot on the page
            _, chart_col, _ = st.columns([1, 3, 1])
            with chart_col:
                st.plotly_chart(fig, use_container_width=True)

        elif view_mode == "Pareto View":
            fig = go.Figure()
            pareto_trace = create_pareto_trace(display_df)
            fig.add_trace(pareto_trace)
            
            fig.update_layout(
                title=dict(text=f"Pareto Analysis - Quadrant: {quadrant_selection} ({len(display_df)} Defects)", font=dict(color=TEXT_COLOR), x=0.5),
                xaxis=dict(title="Defect Type", title_font=dict(color=TEXT_COLOR), tickfont=dict(color=TEXT_COLOR)),
                yaxis=dict(title="Count", title_font=dict(color=TEXT_COLOR), tickfont=dict(color=TEXT_COLOR)),
                plot_bgcolor='black', 
                paper_bgcolor= BACKGROUND_COLOR,
                showlegend=False,
                height=800
            )
            st.plotly_chart(fig, use_container_width=True)

        elif view_mode == "Summary View":
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
                    quad_df = full_df[full_df['QUADRANT'] == quad]
                    total_defects = len(quad_df)
                    density = total_defects / (panel_rows * panel_cols) if (panel_rows * panel_cols) > 0 else 0
                    kpi_data.append({"Quadrant": quad, "Total Defects": total_defects, "Defect Density": f"{density:.2f}"})

                kpi_df = pd.DataFrame(kpi_data)
                st.dataframe(kpi_df, use_container_width=True)

                st.divider()
                st.markdown("### Defect Distribution by Quadrant")
                fig = go.Figure()
                grouped_traces = create_grouped_pareto_trace(full_df)
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
        st.info("Upload your Excel file(s) and click 'Run Analysis' to begin.")

if __name__ == '__main__':
    main()

# app.py

"""
Main application file for the Defect Analysis Streamlit Dashboard.
This script acts as the main entry point and orchestrates the UI and logic.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# Import our modularized functions
from src.data_handler import load_data
from src.plotting import (
    create_grid_shapes, create_defect_traces,
    create_pareto_trace, create_grouped_pareto_trace
)
from src.reporting import generate_excel_report

# ==============================================================================
# --- STREAMLIT APP MAIN LOGIC (DEFINITIVE VERSION) ---
# ==============================================================================

def main():
    """
    Main function to run the Streamlit application.
    """
    # --- App Configuration ---
    st.set_page_config(layout="wide", page_title="Panel Defect Analysis")

    # --- THEME COLORS: Centralized here for a perfect match with the Colab version ---
    APP_BACKGROUND_COLOR = '#F4A460'      # Sandy brown (for page background)
    PANEL_FILL_COLOR = '#8B4513'          # Saddle brown (for panels)
    GAP_COLOR = '#F4A460'                 # Sandy brown (for gaps and the outer visual boundary)
    GRID_LINE_COLOR = 'black'
    TEXT_COLOR = 'black'
    
    # --- Apply Custom CSS using the correct theme ---
    st.markdown(f"""
        <style>
            .reportview-container, .main {{ background-color: {APP_BACKGROUND_COLOR}; }}
            .sidebar .sidebar-content {{ background-color: #F0F2F6; border-right: 2px solid #DDDDDD; }}
            h1, h2, h3 {{ text-align: center; color: {TEXT_COLOR}; }}
            body, .stRadio, .stSelectbox, .stNumberInput, .stFileUploader, p, .stMarkdown {{ color: {TEXT_COLOR}; }}
        </style>
    """, unsafe_allow_html=True)
    
    st.title("Panel Defect Analysis Tool")

    # --- Sidebar Control Panel ---
    with st.sidebar:
        st.header("Control Panel")
        st.divider()
        st.subheader("Data Source")
        uploaded_file = st.file_uploader("Upload Your Defect Data (Excel)", type=["xlsx", "xls"])
        st.divider()
        st.subheader("Configuration")
        panel_rows = st.number_input("Panel Rows", min_value=2, max_value=50, value=7)
        panel_cols = st.number_input("Panel Columns", min_value=2, max_value=50, value=7)
        gap_size = 1 
        st.divider()
        st.subheader("Analysis Controls")
        view_mode = st.radio("Select View", ["Defect View", "Pareto View", "Summary View"])
        quadrant_selection = st.selectbox("Select Quadrant", ["All", "Q1", "Q2", "Q3", "Q4"])

    # --- Main Content Area ---
    if uploaded_file is None:
        st.info("Welcome! Please upload a defect data file to begin analysis.")
        return

    full_df = load_data(uploaded_file, panel_rows, panel_cols, gap_size)
    if full_df.empty:
        st.error("The uploaded file is empty or could not be processed. Please check the file format.")
        return

    display_df = full_df[full_df['QUADRANT'] == quadrant_selection] if quadrant_selection != "All" else full_df

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

    if view_mode == "Defect View":
        fig = go.Figure()
        defect_traces = create_defect_traces(display_df)
        for trace in defect_traces: fig.add_trace(trace)
        
        total_grid_width = (2 * panel_cols) + gap_size
        total_grid_height = (2 * panel_rows) + gap_size
        
        if quadrant_selection == "All":
            # --- FIX: Set the viewing window larger than the grid to create the visual boundary ---
            x_axis_range = [-gap_size, total_grid_width + gap_size]
            y_axis_range = [-gap_size, total_grid_height + gap_size]
            
            plot_shapes = create_grid_shapes(
                panel_rows, panel_cols, gap_size, quadrant='All',
                panel_fill_color=PANEL_FILL_COLOR,
                grid_line_color=GRID_LINE_COLOR
            )
            
            # --- FIX: The plot background IS the gap color ---
            plot_bg_color = GAP_COLOR
            show_axes = True

        else: # A single quadrant is selected
            # --- FIX: Ranges for zoomed-in quadrants ---
            x_axis_range = [0, panel_cols]
            y_axis_range = [0, panel_rows]

            plot_shapes = create_grid_shapes(
                panel_rows, panel_cols, gap_size, quadrant=quadrant_selection,
                panel_fill_color=PANEL_FILL_COLOR,
                grid_line_color=GRID_LINE_COLOR
            )

            # --- FIX: The plot background IS the panel color for a zoomed-in view ---
            plot_bg_color = PANEL_FILL_COLOR
            show_axes = False

        x_tick_pos = [i + 0.5 for i in range(panel_cols)] + [i + 0.5 + panel_cols + gap_size for i in range(panel_cols)]
        y_tick_pos = [i + 0.5 for i in range(panel_rows)] + [i + 0.5 + panel_rows + gap_size for i in range(panel_rows)]
        
        fig.update_layout(
            title=dict(text=f"Panel Defect Map - Quadrant: {quadrant_selection} ({len(display_df)} Defects)", font=dict(color=TEXT_COLOR)),
            xaxis=dict(title="Unit Column Index" if show_axes else "", title_font=dict(color=TEXT_COLOR), tickfont=dict(color=TEXT_COLOR), range=x_axis_range, tickvals=x_tick_pos if show_axes else [], ticktext=list(range(2 * panel_cols)) if show_axes else [], showgrid=False, zeroline=False, showline=show_axes, linewidth=3, linecolor=GRID_LINE_COLOR, mirror=True),
            yaxis=dict(title="Unit Row Index" if show_axes else "", title_font=dict(color=TEXT_COLOR), tickfont=dict(color=TEXT_COLOR), range=y_axis_range, tickvals=y_tick_pos if show_axes else [], ticktext=list(range(2 * panel_rows)) if show_axes else [], scaleanchor="x", scaleratio=1, showgrid=False, zeroline=False, showline=show_axes, linewidth=3, linecolor=GRID_LINE_COLOR, mirror=True),
            plot_bgcolor=plot_bg_color,
            paper_bgcolor=APP_BACKGROUND_COLOR,
            shapes=plot_shapes,
            legend=dict(title_font=dict(color=TEXT_COLOR), font=dict(color=TEXT_COLOR), x=1.02, y=1, xanchor='left', yanchor='top')
            # --- FIX: No `height` property, allowing `scaleanchor` to enforce a square plot ---
        )
        st.plotly_chart(fig, use_container_width=True)

    elif view_mode == "Pareto View":
        fig = go.Figure()
        pareto_trace = create_pareto_trace(display_df)
        fig.add_trace(pareto_trace)
        fig.update_layout(
            title=dict(text=f"Pareto Analysis - Quadrant: {quadrant_selection}", font=dict(color=TEXT_COLOR)),
            xaxis=dict(title="Defect Type", title_font=dict(color=TEXT_COLOR), tickfont=dict(color=TEXT_COLOR)),
            yaxis=dict(title="Count", title_font=dict(color=TEXT_COLOR), tickfont=dict(color=TEXT_COLOR)),
            plot_bgcolor=PANEL_FILL_COLOR, 
            paper_bgcolor=APP_BACKGROUND_COLOR,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

    elif view_mode == "Summary View":
        st.header(f"Statistical Summary for Quadrant: {quadrant_selection}")
        if display_df.empty:
            st.info("No defects to summarize in the selected quadrant.")
            return

        if quadrant_selection != "All":
            # ... (your existing summary logic is fine)
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
        else:
            # ... (your existing summary logic is fine)
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
                plot_bgcolor=PANEL_FILL_COLOR,
                paper_bgcolor=APP_BACKGROUND_COLOR,
                legend=dict(font=dict(color=TEXT_COLOR))
            )
            st.plotly_chart(fig, use_container_width=True)

if __name__ == '__main__':
    main()

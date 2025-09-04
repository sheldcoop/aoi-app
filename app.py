# app.py

"""
Main application file for the Defect Analysis Streamlit Dashboard.
This script acts as the main entry point and orchestrates the UI and logic.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# Import our modularized functions
from src.config import BACKGROUND_COLOR, PLOT_AREA_COLOR, GRID_COLOR, TEXT_COLOR
from src.data_handler import load_data
from src.plotting import (
    create_grid_shapes, create_defect_traces, 
    create_pareto_trace, create_grouped_pareto_trace, get_base_layout
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
    st.sidebar.header("Control Panel")
    st.sidebar.divider()

    st.sidebar.subheader("Data Source")
    uploaded_file = st.sidebar.file_uploader("Upload Your Defect Data (Excel)", type=["xlsx", "xls"])

    st.sidebar.divider()

    st.sidebar.subheader("Configuration")
    panel_rows = st.sidebar.number_input("Panel Rows", min_value=2, max_value=50, value=7)
    panel_cols = st.sidebar.number_input("Panel Columns", min_value=2, max_value=50, value=7)
    gap_size = 1
    cell_size = st.sidebar.slider("Cell Size (Zoom)", min_value=20, max_value=100, value=40, help="Adjust the visual size of the grid cells on the defect map.")

    # --- Load data early to populate filters ---
    full_df = load_data(uploaded_file, panel_rows, panel_cols, gap_size)
    if full_df.empty:
        st.warning("No data to display. Please upload a valid Excel file.")
        return

    # --- Sidebar controls that depend on the data ---
    st.sidebar.divider()
    st.sidebar.subheader("Analysis Controls")

    defect_types = sorted(full_df['DEFECT_TYPE'].unique())
    selected_defects = st.sidebar.multiselect(
        "Filter by Defect Type",
        options=defect_types,
        default=[]
    )

    view_mode = st.sidebar.radio("Select View", ["Defect View", "Pareto View", "Summary View"])
    quadrant_selection = st.sidebar.selectbox("Select Quadrant", ["All", "Q1", "Q2", "Q3", "Q4"])

    # --- Filter data based on sidebar controls ---
    display_df = full_df.copy()
    if quadrant_selection != "All":
        display_df = display_df[display_df['QUADRANT'] == quadrant_selection]

    if selected_defects: # If the user has selected any defect types
        display_df = display_df[display_df['DEFECT_TYPE'].isin(selected_defects)]

    # --- Add Download Report Button to Sidebar ---
    st.sidebar.divider()
    st.sidebar.subheader("Reporting")

    excel_report_bytes = generate_excel_report(full_df, panel_rows, panel_cols)

    st.sidebar.download_button(
        label="Download Full Report",
        data=excel_report_bytes,
        file_name="full_defect_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # --- Main content area ---
    if view_mode == "Defect View":
        fig = go.Figure()
        defect_traces = create_defect_traces(display_df)
        for trace in defect_traces: fig.add_trace(trace)
        
        total_rows, total_cols = 2 * panel_rows, 2 * panel_cols
        total_width, total_height = 2 * panel_cols + gap_size, 2 * panel_rows + gap_size
        x_range_full, y_range_full = [-1, total_width + 1], [-1, total_height + 1]
        q1_x, q1_y = [0, panel_cols], [0, panel_rows]
        q2_x, q2_y = [panel_cols + gap_size, total_width], [0, panel_rows]
        q3_x, q3_y = [0, panel_cols], [panel_rows + gap_size, total_height]
        q4_x, q4_y = [panel_cols + gap_size, total_width], [panel_rows + gap_size, total_height]
        
        if quadrant_selection == "All":
            x_axis_range, y_axis_range = x_range_full, y_range_full
            plot_shapes = create_grid_shapes(panel_rows, panel_cols, gap_size, quadrant='All')
            show_axes = True
            plot_bg_color = PLOT_AREA_COLOR
        else:
            plot_shapes = create_grid_shapes(panel_rows, panel_cols, gap_size, quadrant=quadrant_selection)
            show_axes = False
            plot_bg_color = BACKGROUND_COLOR
            if quadrant_selection == "Q1": x_axis_range, y_axis_range = q1_x, q1_y
            elif quadrant_selection == "Q2": x_axis_range, y_axis_range = q2_x, q2_y
            elif quadrant_selection == "Q3": x_axis_range, y_axis_range = q3_x, q3_y
            else: x_axis_range, y_axis_range = q4_x, q4_y

        x_tick_pos = [i + 0.5 for i in range(panel_cols)] + [i + 0.5 + panel_cols + gap_size for i in range(panel_cols)]
        y_tick_pos = [i + 0.5 for i in range(panel_rows)] + [i + 0.5 + panel_rows + gap_size for i in range(panel_rows)]
        
        # --- Calculate dynamic height for the plot ---
        # The total height of the grid in plot coordinates is (2 * panel_rows + gap_size)
        # We multiply this by the user-defined cell_size to get the desired pixel height.
        dynamic_plot_height = (2 * panel_rows + gap_size) * cell_size

        layout = get_base_layout(
            title_text=f"Panel Defect Map - Quadrant: {quadrant_selection} ({len(display_df)} Defects)",
            text_color=TEXT_COLOR,
            plot_bgcolor=plot_bg_color,
            paper_bgcolor=BACKGROUND_COLOR
        )
        layout.update(
            xaxis=dict(title="Unit Column Index" if show_axes else "", range=x_axis_range, tickvals=x_tick_pos if show_axes else [], ticktext=list(range(total_cols)) if show_axes else [], showgrid=False, zeroline=False, showline=show_axes, linewidth=3, linecolor=GRID_COLOR, mirror=True),
            yaxis=dict(title="Unit Row Index" if show_axes else "", range=y_axis_range, tickvals=y_tick_pos if show_axes else [], ticktext=list(range(total_rows)) if show_axes else [], scaleanchor="x", scaleratio=1, showgrid=False, zeroline=False, showline=show_axes, linewidth=3, linecolor=GRID_COLOR, mirror=True),
            shapes=plot_shapes,
            legend=dict(x=1.02, y=1, xanchor='left', yanchor='top'),
            height=dynamic_plot_height
        )
        fig.update_layout(layout)
        st.plotly_chart(fig, use_container_width=True)

    elif view_mode == "Pareto View":
        fig = go.Figure()
        pareto_trace = create_pareto_trace(display_df)
        fig.add_trace(pareto_trace)
        
        layout = get_base_layout(
            title_text=f"Pareto Analysis - Quadrant: {quadrant_selection} ({len(display_df)} Defects)",
            text_color=TEXT_COLOR,
            plot_bgcolor=PLOT_AREA_COLOR,
            paper_bgcolor=BACKGROUND_COLOR
        )
        layout.update(
            xaxis=dict(title="Defect Type"),
            yaxis=dict(title="Count"),
            showlegend=False,
            height=800
        )
        fig.update_layout(layout)
        st.plotly_chart(fig, use_container_width=True)

    elif view_mode == "Summary View":
        st.header(f"Statistical Summary for Quadrant: {quadrant_selection}")

        if display_df.empty:
            st.info("No defects to summarize in the selected quadrant.")
            return

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
            st.dataframe(top_offenders.style.format({'Percentage': '{:.2f}%'}), use_container_width=True)
        
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
            
            layout = get_base_layout(
                title_text="Defect Distribution by Quadrant",
                text_color=TEXT_COLOR,
                plot_bgcolor=PLOT_AREA_COLOR,
                paper_bgcolor=BACKGROUND_COLOR
            )
            layout.update(
                barmode='group',
                xaxis=dict(title="Defect Type"),
                yaxis=dict(title="Count"),
                height=600
            )
            fig.update_layout(layout)
            st.plotly_chart(fig, use_container_width=True)

if __name__ == '__main__':
    main()


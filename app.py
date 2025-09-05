# app.py

"""
Main application file for the Defect Analysis Streamlit Dashboard.
This script acts as the main entry point and orchestrates the UI and logic.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# Import our modularized functions
# Note: We will override the imported colors inside main() to match the Colab version.
from src.config import BACKGROUND_COLOR, PLOT_AREA_COLOR, GRID_COLOR, TEXT_COLOR
from src.data_handler import load_data
from src.plotting import (
    create_grid_shapes, create_defect_traces,
    create_pareto_trace, create_grouped_pareto_trace
)
from src.reporting import generate_excel_report

# ==============================================================================
# --- STREAMLIT APP MAIN LOGIC (FINAL CORRECTED VERSION) ---
# ==============================================================================

def main():
    """
    Main function to run the Streamlit application.
    """
    # --- App Configuration ---
    st.set_page_config(layout="wide", page_title="Panel Defect Analysis")

    # --- NEW: Hardcode correct colors to match Colab version ---
    # This ensures the plot looks right without needing to change src/config.py
    CORRECT_BACKGROUND_COLOR = '#F4A460'
    CORRECT_PLOT_AREA_COLOR = '#8B4513'
    CORRECT_GRID_COLOR = 'black'
    CORRECT_TEXT_COLOR = 'black'
    
    # --- Apply Custom CSS for a Professional UI ---
    st.markdown(f"""
        <style>
            /* Main app background */
            .reportview-container, .main {{
                background-color: {CORRECT_BACKGROUND_COLOR};
            }}
            /* Sidebar styling */
            .sidebar .sidebar-content {{
                background-color: #F0F2F6; /* A light grey for the sidebar */
                border-right: 2px solid #DDDDDD;
            }}
            h1, h2, h3 {{ text-align: center; padding-bottom: 20px; color: {CORRECT_TEXT_COLOR}; }}
            body, .stRadio, .stSelectbox, .stNumberInput, .stFileUploader, .stDownloadButton {{ color: {CORRECT_TEXT_COLOR}; }}
            p, .stMarkdown {{ color: {CORRECT_TEXT_COLOR}; }}
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
        st.info("Welcome! Please upload a defect data file using the control panel on the left to begin analysis.")
        return

    full_df = load_data(uploaded_file, panel_rows, panel_cols, gap_size)
    if full_df.empty:
        st.error("The uploaded file could not be processed or is empty. Please check the file format and content.")
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
        
        total_panel_width = (2 * panel_cols) + gap_size
        total_panel_height = (2 * panel_rows) + gap_size
        x_range_full, y_range_full = [-gap_size, total_panel_width], [-gap_size, total_panel_height]
        
        q1_x, q1_y = [0, panel_cols], [0, panel_rows]
        q2_x, q2_y = [panel_cols + gap_size, total_panel_width], [0, panel_rows]
        q3_x, q3_y = [0, panel_cols], [panel_rows + gap_size, total_panel_height]
        q4_x, q4_y = [panel_cols + gap_size, total_panel_width], [panel_rows + gap_size, total_panel_height]
        
        if quadrant_selection == "All":
            x_axis_range, y_axis_range = x_range_full, y_range_full
            plot_shapes = create_grid_shapes(panel_rows, panel_cols, gap_size, quadrant='All')
            
            boundary_shape = go.layout.Shape(
                type="rect", x0=-gap_size, y0=-gap_size, x1=total_panel_width, y1=total_panel_height,
                fillcolor=CORRECT_PLOT_AREA_COLOR, line_width=0, layer='below'
            )
            plot_shapes.insert(0, boundary_shape)
            
            show_axes = True
            plot_bg_color = CORRECT_BACKGROUND_COLOR
        else:
            plot_shapes = create_grid_shapes(panel_rows, panel_cols, gap_size, quadrant=quadrant_selection)
            show_axes = False
            plot_bg_color = CORRECT_BACKGROUND_COLOR
            if quadrant_selection == "Q1": x_axis_range, y_axis_range = q1_x, q1_y
            elif quadrant_selection == "Q2": x_axis_range, y_axis_range = q2_x, q2_y
            elif quadrant_selection == "Q3": x_axis_range, y_axis_range = q3_x, q3_y
            else: x_axis_range, y_axis_range = q4_x, q4_y

        total_cols = 2 * panel_cols
        total_rows = 2 * panel_rows
        x_tick_pos = [i + 0.5 for i in range(panel_cols)] + [i + 0.5 + panel_cols + gap_size for i in range(panel_cols)]
        y_tick_pos = [i + 0.5 for i in range(panel_rows)] + [i + 0.5 + panel_rows + gap_size for i in range(panel_rows)]
        
        fig.update_layout(
            title=dict(text=f"Panel Defect Map - Quadrant: {quadrant_selection} ({len(display_df)} Defects)", font=dict(color=CORRECT_TEXT_COLOR)),
            xaxis=dict(title="Unit Column Index" if show_axes else "", title_font=dict(color=CORRECT_TEXT_COLOR), tickfont=dict(color=CORRECT_TEXT_COLOR), range=x_axis_range, tickvals=x_tick_pos if show_axes else [], ticktext=list(range(total_cols)) if show_axes else [], showgrid=False, zeroline=False, showline=show_axes, linewidth=3, linecolor=CORRECT_GRID_COLOR, mirror=True),
            yaxis=dict(title="Unit Row Index" if show_axes else "", title_font=dict(color=CORRECT_TEXT_COLOR), tickfont=dict(color=CORRECT_TEXT_COLOR), range=y_axis_range, tickvals=y_tick_pos if show_axes else [], ticktext=list(range(total_rows)) if show_axes else [], scaleanchor="x", scaleratio=1, showgrid=False, zeroline=False, showline=show_axes, linewidth=3, linecolor=CORRECT_GRID_COLOR, mirror=True),
            plot_bgcolor=plot_bg_color, 
            paper_bgcolor=CORRECT_BACKGROUND_COLOR,
            shapes=plot_shapes,
            legend=dict(title_font=dict(color=CORRECT_TEXT_COLOR), font=dict(color=CORRECT_TEXT_COLOR), x=1.02, y=1, xanchor='left', yanchor='top')
            # --- FIX: The `height=800` line has been removed to ensure a square aspect ratio ---
        )
        st.plotly_chart(fig, use_container_width=True)

    elif view_mode == "Pareto View":
        fig = go.Figure()
        pareto_trace = create_pareto_trace(display_df)
        fig.add_trace(pareto_trace)
        fig.update_layout(
            title=dict(text=f"Pareto Analysis - Quadrant: {quadrant_selection} ({len(display_df)} Defects)", font=dict(color=CORRECT_TEXT_COLOR)),
            xaxis=dict(title="Defect Type", title_font=dict(color=CORRECT_TEXT_COLOR), tickfont=dict(color=CORRECT_TEXT_COLOR)),
            yaxis=dict(title="Count", title_font=dict(color=CORRECT_TEXT_COLOR), tickfont=dict(color=CORRECT_TEXT_COLOR)),
            plot_bgcolor=CORRECT_PLOT_AREA_COLOR, 
            paper_bgcolor=CORRECT_BACKGROUND_COLOR,
            showlegend=False
        )
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
            st.dataframe(top_offenders.style.format({'Percentage': '{:.2f}%'}).background_gradient(cmap='Reds', subset=['Count']), use_container_width=True)
        else:
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
                xaxis=dict(title="Defect Type", title_font=dict(color=CORRECT_TEXT_COLOR), tickfont=dict(color=CORRECT_TEXT_COLOR)),
                yaxis=dict(title="Count", title_font=dict(color=CORRECT_TEXT_COLOR), tickfont=dict(color=CORRECT_TEXT_COLOR)),
                plot_bgcolor=CORRECT_PLOT_AREA_COLOR, 
                paper_bgcolor=CORRECT_BACKGROUND_COLOR,
                legend=dict(font=dict(color=CORRECT_TEXT_COLOR))
            )
            st.plotly_chart(fig, use_container_width=True)


if __name__ == '__main__':
    main()

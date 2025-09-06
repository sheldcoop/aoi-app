# src/views.py
# This module contains functions for rendering the different views in the Streamlit app.

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from src.config import BACKGROUND_COLOR, PLOT_AREA_COLOR, TEXT_COLOR
from src.plotting import (
    create_dynamic_grid, create_single_panel_grid, create_defect_traces,
    create_pareto_trace, create_grouped_pareto_trace
)

def _calculate_defect_coordinates(df, panel_rows, panel_cols, cell_size, gap_size_units):
    """Helper function to calculate plot coordinates for defects."""
    panel_width_units = panel_cols * cell_size
    panel_height_units = panel_rows * cell_size

    plot_x_base = (df['UNIT_INDEX_Y'] % panel_cols) * cell_size
    plot_y_base = (df['UNIT_INDEX_X'] % panel_rows) * cell_size

    x_offset = np.where(df['UNIT_INDEX_Y'] >= panel_cols, panel_width_units + gap_size_units, 0)
    y_offset = np.where(df['UNIT_INDEX_X'] >= panel_rows, panel_height_units + gap_size_units, 0)

    jitter_x = df['jitter_x'] * cell_size
    jitter_y = df['jitter_y'] * cell_size

    df['plot_x'] = plot_x_base + x_offset + jitter_x
    df['plot_y'] = plot_y_base + y_offset + jitter_y

    return df

def render_defect_view(display_df, quadrant_selection, panel_rows, panel_cols, gap_size):
    """Renders the defect view."""
    fig = go.Figure()

    if quadrant_selection == "All":
        FIGURE_WIDTH, FIGURE_HEIGHT = 800, 800
        MARGIN = dict(l=20, r=20, t=20, b=20)

        layout_data = create_dynamic_grid(panel_rows, panel_cols, gap_size, FIGURE_WIDTH, FIGURE_HEIGHT, MARGIN)

        if not display_df.empty:
            df = display_df.copy()
            df = _calculate_defect_coordinates(df, panel_rows, panel_cols, layout_data['cell_size'], layout_data['gap_size_units'])
            defect_traces = create_defect_traces(df)
            for trace in defect_traces: fig.add_trace(trace)

        tick_labels = list(range(2 * panel_cols))

        fig.update_layout(
            title=dict(text=f"Panel Defect Map - Quadrant: {quadrant_selection} ({len(display_df)} Defects)", font=dict(color=TEXT_COLOR)),
            xaxis=dict(range=layout_data['x_axis_range'], tickvals=layout_data['x_tick_pos'], ticktext=tick_labels, showgrid=False, zeroline=False),
            yaxis=dict(range=layout_data['y_axis_range'], tickvals=layout_data['y_tick_pos'], ticktext=tick_labels, scaleanchor="x", scaleratio=1, showgrid=False, zeroline=False),
            plot_bgcolor='#E58A60', paper_bgcolor=BACKGROUND_COLOR,
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
            xaxis=dict(range=[0, panel_cols-1 ], showgrid=False, zeroline=False, showticklabels=True),
            yaxis=dict(range=[0, panel_rows-1], showgrid=False, zeroline=False, showticklabels=True, scaleanchor="x", scaleratio=1),
            plot_bgcolor=BACKGROUND_COLOR, paper_bgcolor=BACKGROUND_COLOR,
            shapes=plot_shapes,
            height=800,
            margin=dict(l=20, r=20, t=20, b=20),
            legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02, title_font=dict(color=TEXT_COLOR), font=dict(color=TEXT_COLOR))
        )

    # Center the plot on the page
    _, chart_col, _ = st.columns([1, 3, 1])
    with chart_col:
        st.plotly_chart(fig, use_container_width=True)


def render_pareto_view(display_df, quadrant_selection):
    """Renders the pareto view."""
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
    st.plotly_chart(fig, use_container_width=True)


def render_summary_view(display_df, full_df, quadrant_selection, panel_rows, panel_cols):
    """Renders the summary view."""
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

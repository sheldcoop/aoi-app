# src/views.py
# This module contains the function for rendering the main Defect Map view.

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from src.config import BACKGROUND_COLOR, PLOT_AREA_COLOR, TEXT_COLOR
from src.plotting import (
    create_dynamic_grid, create_single_panel_grid, create_defect_traces
)

def _calculate_defect_coordinates(df, panel_rows, panel_cols, layout_data):
    """Helper function to calculate plot coordinates for defects in the relative grid."""
    cell_size = layout_data['cell_size']
    gap_size_units = layout_data['gap_size_units']
    panel_width_units = layout_data['panel_width_units']
    panel_height_units = layout_data['panel_height_units']

    # Base position within a quadrant (0 to panel_width/height)
    plot_x_base = (df['UNIT_INDEX_Y'] % panel_cols) * cell_size
    plot_y_base = (df['UNIT_INDEX_X'] % panel_rows) * cell_size

    # Offset for each quadrant
    # Q1: Top-Left -> x=0, y=panel_height+gap
    # Q2: Top-Right -> x=panel_width+gap, y=panel_height+gap
    # Q3: Bottom-Left -> x=0, y=0
    # Q4: Bottom-Right -> x=panel_width+gap, y=0
    x_offset = np.where(df['QUADRANT'].isin(['Q2', 'Q4']), panel_width_units + gap_size_units, 0)
    y_offset = np.where(df['QUADRANT'].isin(['Q1', 'Q2']), panel_height_units + gap_size_units, 0)

    # Add jitter within the cell
    jitter_x = df['jitter_x'] * cell_size
    jitter_y = df['jitter_y'] * cell_size

    df['plot_x'] = plot_x_base + x_offset + jitter_x
    df['plot_y'] = plot_y_base + y_offset + jitter_y

    return df

def render_defect_view(display_df, quadrant_selection, panel_rows, panel_cols):
    """Renders the defect view."""
    fig = go.Figure()

    if quadrant_selection == "All":
        # The new grid function does not need pixel dimensions
        layout_data = create_dynamic_grid(panel_rows, panel_cols, gap_size_relative=0.1)

        if not display_df.empty:
            df = display_df.copy()
            df = _calculate_defect_coordinates(df, panel_rows, panel_cols, layout_data)
            defect_traces = create_defect_traces(df)
            for trace in defect_traces: fig.add_trace(trace)

        tick_labels_x = list(range(2 * panel_cols))
        tick_labels_y = list(range(2 * panel_rows))

        fig.update_layout(
            title=dict(text=f"Panel Defect Map - Quadrant: {quadrant_selection} ({len(display_df)} Defects)", font=dict(color=TEXT_COLOR)),
            xaxis=dict(
                range=layout_data['x_axis_range'],
                tickvals=layout_data['x_tick_pos'],
                ticktext=tick_labels_x,
                showgrid=False,
                zeroline=False
            ),
            yaxis=dict(
                range=layout_data['y_axis_range'],
                tickvals=layout_data['y_tick_pos'],
                ticktext=tick_labels_y,
                scaleanchor="x",
                scaleratio=1,
                showgrid=False,
                zeroline=False
            ),
            plot_bgcolor='#E58A60',
            paper_bgcolor=BACKGROUND_COLOR,
            shapes=layout_data['shapes'],
            legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02, title_font=dict(color=TEXT_COLOR), font=dict(color=TEXT_COLOR)),
            margin=dict(l=40, r=40, t=40, b=40) # Add a margin for aesthetics
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

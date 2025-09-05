# src/plotting.py
# This module contains all functions that create visualizations.

import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Import the style configurations
from src.config import PANEL_COLOR, GRID_COLOR, defect_style_map

# ==============================================================================
# --- VISUALIZATION FUNCTIONS ---
# ==============================================================================

def create_dynamic_grid(panel_rows, panel_cols, gap_cells, figure_width, figure_height, margin):
    """
    Generates shapes for a dynamic grid based on figure size, including panels and a boundary.
    This function replicates the logic from the user's provided script to create a
    dynamically sized grid layout.
    """
    # --- Configuration ---
    NUM_PANELS_X = 2
    NUM_PANELS_Y = 2

    # --- Step 1: Dynamically Calculate CELL_SIZE ---
    plottable_width_px = figure_width - margin['l'] - margin['r']
    plottable_height_px = figure_height - margin['t'] - margin['b']
    total_cell_units_x = (NUM_PANELS_X * panel_cols) + (NUM_PANELS_X + 1) * gap_cells
    total_cell_units_y = (NUM_PANELS_Y * panel_rows) + (NUM_PANELS_Y + 1) * gap_cells
    cell_size_for_width = plottable_width_px / total_cell_units_x
    cell_size_for_height = plottable_height_px / total_cell_units_y
    cell_size = min(cell_size_for_width, cell_size_for_height)

    # --- Step 2: Calculate Scaled Dimensions ---
    panel_width_units = panel_cols * cell_size
    panel_height_units = panel_rows * cell_size
    gap_size_units = gap_cells * cell_size
    shapes = []

    # --- Step 3: Draw the Four Central Panels and Their Grids ---
    panel_origins = [
        (0, 0), # Q1
        (panel_width_units + gap_size_units, 0), # Q2
        (0, panel_height_units + gap_size_units), # Q3
        (panel_width_units + gap_size_units, panel_height_units + gap_size_units) # Q4
    ]

    for x_start, y_start in panel_origins:
        # Panel background and main border
        shapes.append(go.layout.Shape(
            type="rect",
            x0=x_start, y0=y_start,
            x1=x_start + panel_width_units, y1=y_start + panel_height_units,
            line=dict(color=GRID_COLOR, width=3),
            fillcolor=PANEL_COLOR,
            layer='below'
        ))
        # Inner grid lines (vertical)
        for i in range(1, panel_cols):
            shapes.append(go.layout.Shape(
                type="line",
                x0=x_start + (i * cell_size), y0=y_start,
                x1=x_start + (i * cell_size), y1=y_start + panel_height_units,
                line=dict(color=GRID_COLOR, width=0.5),
                layer='below'
            ))
        # Inner grid lines (horizontal)
        for i in range(1, panel_rows):
            shapes.append(go.layout.Shape(
                type="line",
                x0=x_start, y0=y_start + (i * cell_size),
                x1=x_start + panel_width_units, y1=y_start + (i * cell_size),
                line=dict(color=GRID_COLOR, width=0.5),
                layer='below'
            ))

    # --- Step 4: Draw the Solid Outer Boundary Frame ---
    total_panel_width = (NUM_PANELS_X * panel_width_units) + (NUM_PANELS_X - 1) * gap_size_units
    total_panel_height = (NUM_PANELS_Y * panel_height_units) + (NUM_PANELS_Y - 1) * gap_size_units

    shapes.insert(0, go.layout.Shape(
        type="rect",
        x0=-gap_size_units,
        y0=-gap_size_units,
        x1=total_panel_width + gap_size_units,
        y1=total_panel_height + gap_size_units,
        fillcolor=PANEL_COLOR,
        line_width=0,
        layer='below'
    ))

    # --- Step 5: Prepare return dictionary ---
    # The tick positions need to be calculated for the main app to use.
    x_tick_pos = (
        [i * cell_size + (cell_size / 2) for i in range(panel_cols)] +
        [i * cell_size + (cell_size / 2) + panel_width_units + gap_size_units for i in range(panel_cols)]
    )
    y_tick_pos = (
        [i * cell_size + (cell_size / 2) for i in range(panel_rows)] +
        [i * cell_size + (cell_size / 2) + panel_height_units + gap_size_units for i in range(panel_rows)]
    )

    layout_data = {
        "shapes": shapes,
        "cell_size": cell_size,
        "x_axis_range": [-gap_size_units, total_panel_width + gap_size_units],
        "y_axis_range": [-gap_size_units, total_panel_height + gap_size_units],
        "x_tick_pos": x_tick_pos,
        "y_tick_pos": y_tick_pos,
        "total_width": total_panel_width,
        "total_height": total_panel_height,
        "gap_size_units": gap_size_units
    }

    return layout_data


def create_single_panel_grid(panel_rows, panel_cols):
    """
    Generates the shapes for a single panel grid, used for the zoomed-in quadrant view.
    """
    shapes = []
    # Panel background and main border
    shapes.append(go.layout.Shape(
        type="rect",
        x0=0, y0=0,
        x1=panel_cols, y1=panel_rows,
        line=dict(color=GRID_COLOR, width=3),
        fillcolor=PANEL_COLOR,
        layer='below'
    ))
    # Inner grid lines (vertical)
    for i in range(1, panel_cols):
        shapes.append(go.layout.Shape(
            type="line", x0=i, y0=0, x1=i, y1=panel_rows,
            line=dict(color=GRID_COLOR, width=0.5, dash='dot'),
            opacity=0.5, layer='below'
        ))
    # Inner grid lines (horizontal)
    for i in range(1, panel_rows):
        shapes.append(go.layout.Shape(
            type="line", x0=0, y0=i, x1=panel_cols, y1=i,
            line=dict(color=GRID_COLOR, width=0.5, dash='dot'),
            opacity=0.5, layer='below'
        ))
    return shapes


def create_defect_traces(df):
    """Creates a scatter trace for each defect type."""
    traces = []
    for dtype, color in defect_style_map.items():
        dff = df[df['DEFECT_TYPE'] == dtype]
        if not dff.empty:
            traces.append(go.Scatter(
                x=dff['plot_x'], y=dff['plot_y'], mode='markers',
                marker=dict(color=color, size=8, line=dict(width=1, color='black')),
                name=dtype,
                customdata=dff[['UNIT_INDEX_X', 'UNIT_INDEX_Y', 'DEFECT_TYPE']],
                hovertemplate="<b>Type: %{customdata[2]}</b><br>Location (X, Y): (%{customdata[0]}, %{customdata[1]})<extra></extra>"
            ))
    return traces

def create_defect_view_figure(display_df, panel_rows, panel_cols, gap_size, quadrant_selection, lot_number, TEXT_COLOR, BACKGROUND_COLOR):
    """
    Creates the main Defect View figure, handling both 'All' and single quadrant views.
    """
    fig = go.Figure()

    if quadrant_selection == "All":
        FIGURE_WIDTH, FIGURE_HEIGHT = 800, 800
        MARGIN = dict(l=20, r=20, t=20, b=20)

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
            plot_bgcolor='#E58A60', paper_bgcolor=BACKGROUND_COLOR,
            width=FIGURE_WIDTH, height=FIGURE_HEIGHT, margin=MARGIN,
            shapes=layout_data['shapes'],
            legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02, title_font=dict(color=TEXT_COLOR), font=dict(color=TEXT_COLOR))
        )

        if lot_number:
            fig.add_annotation(
                x=layout_data['total_width'],
                y=layout_data['total_height'] + layout_data['gap_size_units'],
                text=f"<b>Lot: {lot_number}</b>",
                showarrow=False,
                xanchor="right",
                yanchor="top",
                font=dict(family="Arial, sans-serif", size=16, color=TEXT_COLOR),
                align="right"
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

    return fig

def create_pareto_trace(df):
    """Creates the Pareto bar chart trace for a single dataset."""
    if df.empty:
        return go.Bar(name='Pareto')
    pareto_data = df['DEFECT_TYPE'].value_counts().reset_index()
    pareto_data.columns = ['Defect Type', 'Count']
    return go.Bar(
        x=pareto_data['Defect Type'],
        y=pareto_data['Count'],
        name='Pareto',
        marker_color=[defect_style_map.get(dtype, 'grey') for dtype in pareto_data['Defect Type']]
    )

def create_grouped_pareto_trace(df):
    """
    Creates a grouped Pareto bar chart to compare defect counts across all quadrants.
    """
    if df.empty:
        return [] # Return an empty list if there's no data
        
    grouped_data = df.groupby(['QUADRANT', 'DEFECT_TYPE']).size().reset_index(name='Count')
    top_defects = df['DEFECT_TYPE'].value_counts().index.tolist()
    traces = []
    quadrants = ['Q1', 'Q2', 'Q3', 'Q4']
    
    for quadrant in quadrants:
        quadrant_data = grouped_data[grouped_data['QUADRANT'] == quadrant]
        pivot = quadrant_data.pivot(index='DEFECT_TYPE', columns='QUADRANT', values='Count').reindex(top_defects).fillna(0)
        
        if not pivot.empty:
            traces.append(go.Bar(
                name=quadrant,
                x=pivot.index,
                y=pivot[quadrant]
            ))
            
    return traces

# src/plotting.py
# This module contains all functions that create visualizations.

import plotly.graph_objects as go
import pandas as pd

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
    
def create_pareto_trace(df):
    """
    Creates the traces for a true Pareto chart, including bars and a cumulative line.
    Returns a list containing the bar trace and the line trace.
    """
    if df.empty:
        return []

    # 1. Calculate Pareto data
    pareto_data = df['DEFECT_TYPE'].value_counts().reset_index()
    pareto_data.columns = ['Defect Type', 'Count']
    pareto_data['Cumulative Percentage'] = (pareto_data['Count'].cumsum() / pareto_data['Count'].sum()) * 100

    # 2. Create the bar chart trace
    bar_trace = go.Bar(
        x=pareto_data['Defect Type'],
        y=pareto_data['Count'],
        name='Count',
        marker_color=[defect_style_map.get(dtype, 'grey') for dtype in pareto_data['Defect Type']],
        yaxis='y1' # Assign to the primary y-axis
    )

    # 3. Create the cumulative line trace
    line_trace = go.Scatter(
        x=pareto_data['Defect Type'],
        y=pareto_data['Cumulative Percentage'],
        name='Cumulative %',
        mode='lines+markers',
        line=dict(color='crimson', width=3),
        marker=dict(size=7),
        yaxis='y2' # Assign to the secondary y-axis
    )

    return [bar_trace, line_trace]

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

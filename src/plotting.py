# src/plotting.py
# This module contains all functions that create visualizations.

import plotly.graph_objects as go
import pandas as pd

# Import the style configurations
from src.config import defect_style_map

# ==============================================================================
# --- VISUALIZATION FUNCTIONS ---
# ==============================================================================

def create_grid_shapes(panel_rows, panel_cols, gap_size, theme, quadrant='All'):
    """
    Generates the shapes for the 2x2 panel grid using colors from the selected theme.
    Can draw all 4 panels or a single, specified quadrant for zoom view.
    Includes scribe lines.
    """
    shapes = []
    all_origins = {
        'Q1': (0, 0), 'Q2': (panel_cols + gap_size, 0),
        'Q3': (0, panel_rows + gap_size), 'Q4': (panel_cols + gap_size, panel_rows + gap_size)
    }
    origins_to_draw = all_origins if quadrant == 'All' else {quadrant: all_origins[quadrant]}

    if quadrant == 'All':
        shapes.append(dict(type="rect", x0=panel_cols, y0=0, x1=panel_cols + gap_size, y1=2 * panel_rows + gap_size, fillcolor='#A8652A', line_width=0, layer='below'))
        shapes.append(dict(type="rect", x0=0, y0=panel_rows, x1=2 * panel_cols + gap_size, y1=panel_rows + gap_size, fillcolor='#A8652A', line_width=0, layer='below'))

    for x_start, y_start in origins_to_draw.values():
        shapes.append(dict(type="rect", x0=x_start, y0=y_start, x1=x_start + panel_cols, y1=y_start + panel_rows, line=dict(color=theme["GRID_COLOR"], width=3), fillcolor=theme["PANEL_COLOR"], layer='below'))
        for i in range(1, panel_cols):
            shapes.append(dict(type="line", x0=x_start + i, y0=y_start, x1=x_start + i, y1=y_start + panel_rows, line=dict(color=theme["GRID_COLOR"], width=0.5, dash='dot'), opacity=0.5, layer='below'))
        for i in range(1, panel_rows):
            shapes.append(dict(type="line", x0=x_start, y0=y_start + i, x1=x_start + panel_cols, y1=y_start + i, line=dict(color=theme["GRID_COLOR"], width=0.5, dash='dot'), opacity=0.5, layer='below'))
            
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
        return []

    # Use pivot_table to reshape the data, counting defects by type and quadrant
    pivot_df = df.pivot_table(index='DEFECT_TYPE', columns='QUADRANT', aggfunc='size', fill_value=0)

    # Ensure all quadrants are present, even if they have no defects
    for quad in ['Q1', 'Q2', 'Q3', 'Q4']:
        if quad not in pivot_df.columns:
            pivot_df[quad] = 0

    # Sort the defect types by their total count across all quadrants
    pivot_df = pivot_df.loc[pivot_df.sum(axis=1).sort_values(ascending=False).index]

    traces = []
    for quadrant in ['Q1', 'Q2', 'Q3', 'Q4']:
        traces.append(go.Bar(
            name=quadrant,
            x=pivot_df.index,
            y=pivot_df[quadrant]
        ))
        
    return traces


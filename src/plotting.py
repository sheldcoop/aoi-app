# src/plotting.py
# This module contains all functions that create visualizations.

import plotly.graph_objects as go
import pandas as pd

# Import the style configurations
from src.config import PANEL_COLOR, GRID_COLOR, defect_style_map

# ==============================================================================
# --- VISUALIZATION FUNCTIONS ---
# ==============================================================================

def create_grid_shapes(panel_rows, panel_cols, gap_size, quadrant='All'):
    """
    Generates the shapes for the 2x2 panel grid.
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
        shapes.append(dict(type="rect", x0=x_start, y0=y_start, x1=x_start + panel_cols, y1=y_start + panel_rows, line=dict(color=GRID_COLOR, width=3), fillcolor=PANEL_COLOR, layer='below'))
        for i in range(1, panel_cols):
            shapes.append(dict(type="line", x0=x_start + i, y0=y_start, x1=x_start + i, y1=y_start + panel_rows, line=dict(color=GRID_COLOR, width=0.5, dash='dot'), opacity=0.5, layer='below'))
        for i in range(1, panel_rows):
            shapes.append(dict(type="line", x0=x_start, y0=y_start + i, x1=x_start + panel_cols, y1=y_start + i, line=dict(color=GRID_COLOR, width=0.5, dash='dot'), opacity=0.5, layer='below'))
            
    return shapes

def create_defect_traces(df):
    """
    Creates a scatter trace for each defect type.
    Includes image_path in customdata for hover events.
    """
    traces = []
    # Ensure the image_path column exists
    if 'image_path' not in df.columns:
        df['image_path'] = None

    for dtype, color in defect_style_map.items():
        dff = df[df['DEFECT_TYPE'] == dtype]
        if not dff.empty:
            traces.append(go.Scatter(
                x=dff['plot_x'],
                y=dff['plot_y'],
                mode='markers',
                marker=dict(color=color, size=8, line=dict(width=1, color='black')),
                name=dtype,
                # Include all necessary data for the hover event
                customdata=dff[['UNIT_INDEX_X', 'UNIT_INDEX_Y', 'DEFECT_TYPE', 'image_path']],
                hovertemplate=(
                    "<b>Type: %{customdata[2]}</b><br>"
                    "Location (X, Y): (%{customdata[0]}, %{customdata[1]})<br>"
                    "Image Available: %{customdata[3]}"
                    "<extra></extra>"
                )
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


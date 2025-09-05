# src/plotting.py

import plotly.graph_objects as go
import pandas as pd

# (You may have other plotting functions here like create_defect_traces, etc. Leave them as they are)

# ==============================================================================
# --- DEFINITIVE create_grid_shapes FUNCTION ---
# ==============================================================================

def create_grid_shapes(panel_rows, panel_cols, gap_size, quadrant='All', panel_fill_color='#8B4513', grid_line_color='black'):
    """
    Generates the shape objects for the panel grid.

    This function is now a simple 'artist'. It only draws what it's told to draw
    with the colors it is given. It handles both the 'All' view and single quadrant views.
    """
    shapes = []

    if quadrant == 'All':
        # Define the starting corner for each of the four panels
        panel_origins = [
            (0, 0),                                      # Bottom-Left (Q1)
            (panel_cols + gap_size, 0),                  # Bottom-Right (Q2)
            (0, panel_rows + gap_size),                  # Top-Left (Q3)
            (panel_cols + gap_size, panel_rows + gap_size) # Top-Right (Q4)
        ]
        
        for x_start, y_start in panel_origins:
            # Add the main panel rectangle
            shapes.append(go.layout.Shape(
                type="rect",
                x0=x_start, y0=y_start,
                x1=x_start + panel_cols, y1=y_start + panel_rows,
                line=dict(color=grid_line_color, width=3),
                fillcolor=panel_fill_color,
                layer='below'
            ))
            # Add the inner grid lines
            for i in range(1, panel_cols):
                shapes.append(go.layout.Shape(type="line", x0=x_start + i, y0=y_start, x1=x_start + i, y1=y_start + panel_rows, line=dict(color=grid_line_color, width=0.5), layer='below'))
            for i in range(1, panel_rows):
                shapes.append(go.layout.Shape(type="line", x0=x_start, y0=y_start + i, x1=x_start + panel_cols, y1=y_start + i, line=dict(color=grid_line_color, width=0.5), layer='below'))
    
    else: # Handle single quadrant view (e.g., 'Q1', 'Q2', etc.)
        # In a single quadrant view, we draw only one panel, and we draw it at origin (0,0)
        # because the axis range in app.py will handle the zoom.
        x_start, y_start = 0, 0
        shapes.append(go.layout.Shape(
            type="rect",
            x0=x_start, y0=y_start,
            x1=x_start + panel_cols, y1=y_start + panel_rows,
            line=dict(color=grid_line_color, width=3),
            fillcolor=panel_fill_color,
            layer='below'
        ))
        for i in range(1, panel_cols):
            shapes.append(go.layout.Shape(type="line", x0=x_start + i, y0=y_start, x1=x_start + i, y1=y_start + panel_rows, line=dict(color=grid_line_color, width=0.5), layer='below'))
        for i in range(1, panel_rows):
            shapes.append(go.layout.Shape(type="line", x0=x_start, y0=y_start + i, x1=x_start + panel_cols, y1=y_start + i, line=dict(color=grid_line_color, width=0.5), layer='below'))
            
    return shapes

# ==============================================================================
# --- Your Other Plotting Functions (Unchanged) ---
# ==============================================================================

def create_defect_traces(df):
    # Your existing code for this function...
    traces = []
    defect_types = df['DEFECT_TYPE'].unique()
    for defect in defect_types:
        defect_df = df[df['DEFECT_TYPE'] == defect]
        traces.append(go.Scatter(
            x=defect_df['PLOT_X'],
            y=defect_df['PLOT_Y'],
            mode='markers',
            name=defect,
            marker=dict(size=8, opacity=0.8)
        ))
    return traces

def create_pareto_trace(df):
    # Your existing code for this function...
    counts = df['DEFECT_TYPE'].value_counts()
    return go.Bar(x=counts.index, y=counts.values)

def create_grouped_pareto_trace(df):
    # Your existing code for this function...
    grouped = df.groupby(['QUADRANT', 'DEFECT_TYPE']).size().reset_index(name='COUNT')
    traces = []
    quadrants = ['Q1', 'Q2', 'Q3', 'Q4']
    all_defects = df['DEFECT_TYPE'].unique()
    for quad in quadrants:
        quad_df = grouped[grouped['QUADRANT'] == quad]
        # Ensure all defect types are present for consistent grouping
        counts = {defect: 0 for defect in all_defects}
        for _, row in quad_df.iterrows():
            counts[row['DEFECT_TYPE']] = row['COUNT']
        traces.append(go.Bar(
            name=quad,
            x=list(counts.keys()),
            y=list(counts.values())
        ))
    return traces

import pytest
import pandas as pd
import plotly.graph_objects as go

# Make sure the app's root directory is in the path
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.plotting import (
    create_pareto_trace, create_defect_traces, create_grouped_pareto_trace,
    create_dynamic_grid, create_single_panel_grid
)
from src.config import defect_style_map

@pytest.fixture
def sample_df():
    """Fixture for a sample DataFrame."""
    data = {
        'DEFECT_TYPE': ['Nick', 'Short', 'Nick', 'Cut', 'Short', 'Nick'],
        'QUADRANT': ['Q1', 'Q1', 'Q2', 'Q2', 'Q3', 'Q4'],
        'plot_x': [1, 2, 3, 4, 5, 6],
        'plot_y': [1, 2, 3, 4, 5, 6],
        'UNIT_INDEX_X': [1, 2, 3, 4, 5, 6],
        'UNIT_INDEX_Y': [1, 2, 3, 4, 5, 6],
    }
    return pd.DataFrame(data)

def test_create_pareto_trace(sample_df):
    """Test the creation of Pareto traces."""
    traces = create_pareto_trace(sample_df)

    assert len(traces) == 2  # One bar, one line

    bar_trace, line_trace = traces
    assert isinstance(bar_trace, go.Bar)
    assert isinstance(line_trace, go.Scatter)

    # Check cumulative percentage calculation
    # Expected: Nick (3), Short (2), Cut (1) -> Total 6
    # CumSum: 3, 5, 6
    # CumPct: (3/6)*100=50, (5/6)*100=83.33, (6/6)*100=100
    assert line_trace.y[-1] == 100
    assert pytest.approx(line_trace.y[0]) == 50

def test_create_defect_traces(sample_df):
    """Test creation of defect scatter traces."""
    traces = create_defect_traces(sample_df)

    # Expected defect types in sample_df: Nick, Short, Cut
    assert len(traces) == 3

    trace_names = {trace.name for trace in traces}
    assert trace_names == {'Nick', 'Short', 'Cut'}

def test_create_grouped_pareto_trace(sample_df):
    """Test the creation of grouped Pareto traces for quadrant comparison."""
    traces = create_grouped_pareto_trace(sample_df)

    # Expect a trace for each quadrant that has data
    assert len(traces) == 4 # Q1, Q2, Q3, Q4

    q1_trace = next(t for t in traces if t.name == 'Q1')
    assert q1_trace.y[q1_trace.x.tolist().index('Nick')] == 1
    assert q1_trace.y[q1_trace.x.tolist().index('Short')] == 1

def test_create_dynamic_grid():
    """Test the dynamic grid layout function."""
    layout_data = create_dynamic_grid(7, 7, 1, 800, 800, dict(l=20, r=20, t=20, b=20))

    assert "shapes" in layout_data
    assert "cell_size" in layout_data
    assert "x_axis_range" in layout_data
    assert isinstance(layout_data['shapes'], list)
    assert isinstance(layout_data['cell_size'], float)

def test_create_single_panel_grid():
    """Test the single panel grid layout function."""
    shapes = create_single_panel_grid(10, 10)

    assert isinstance(shapes, list)
    assert len(shapes) > 0
    assert isinstance(shapes[0], go.layout.Shape)

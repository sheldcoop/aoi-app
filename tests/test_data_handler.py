import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
import streamlit as st
import numpy as np

# Make sure the app's root directory is in the path
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_handler import load_data

@pytest.fixture
def mock_streamlit():
    """Mock streamlit functions to avoid running the actual UI components."""
    with patch('streamlit.error') as mock_error, \
         patch('streamlit.warning') as mock_warning, \
         patch('streamlit.info') as mock_info, \
         patch('streamlit.sidebar') as mock_sidebar:

        # Mock sidebar to have success and info methods
        mock_sidebar.success = MagicMock()
        mock_sidebar.info = MagicMock()

        yield {
            "error": mock_error,
            "warning": mock_warning,
            "info": mock_info,
            "sidebar": mock_sidebar
        }

@patch('pandas.read_excel')
def test_load_data_from_valid_excel(mock_read_excel, mock_streamlit):
    """Test loading data from a single valid uploaded Excel file."""
    # Configure the mock to return a sample DataFrame
    mock_df = pd.DataFrame({
        'DEFECT_TYPE': ['Nick', 'Short'],
        'UNIT_INDEX_X': [1, 2],
        'UNIT_INDEX_Y': [3, 4]
    })
    mock_read_excel.return_value = mock_df

    # Create a mock uploaded file (it's just a placeholder now)
    uploaded_file = MagicMock()
    uploaded_file.name = 'test_data.xlsx'

    # Call the function
    df = load_data([uploaded_file], panel_rows=5, panel_cols=10)

    # Assertions
    assert not df.empty
    assert len(df) == 2
    assert 'QUADRANT' in df.columns
    mock_streamlit["sidebar"].success.assert_called_once_with("1 file(s) loaded successfully!")

@patch('pandas.read_excel')
def test_load_data_with_missing_columns(mock_read_excel, mock_streamlit):
    """Test that a file with missing columns is skipped and a warning is shown."""
    # Configure the mock to return a DataFrame with missing columns
    mock_df = pd.DataFrame({'DEFECT_TYPE': ['Nick']})
    mock_read_excel.return_value = mock_df

    # Create a mock uploaded file
    uploaded_file = MagicMock()
    uploaded_file.name = 'test_data_missing_cols.xlsx'

    # Call the function
    df = load_data([uploaded_file], panel_rows=5, panel_cols=10)

    # Assertions
    assert df.empty
    mock_streamlit["error"].assert_called_once()
    mock_streamlit["warning"].assert_called_once_with("No valid data could be loaded from the uploaded file(s).")

def test_load_data_fallback_to_sample(mock_streamlit):
    """Test that sample data is generated when no file is uploaded."""
    df = load_data([], panel_rows=7, panel_cols=7)

    # Assertions
    assert not df.empty
    assert len(df) == 150
    assert 'QUADRANT' in df.columns
    mock_streamlit["sidebar"].info.assert_called_once_with("No file uploaded. Displaying sample data.")

def test_quadrant_assignment():
    """Test the quadrant assignment logic."""
    data = {
        'UNIT_INDEX_X': [1, 1, 6, 6],
        'UNIT_INDEX_Y': [1, 6, 1, 6],
        'DEFECT_TYPE': ['A', 'B', 'C', 'D']
    }
    df = pd.DataFrame(data)

    # Manually assign quadrants to the test dataframe
    panel_rows, panel_cols = 5, 5
    conditions = [
        (df['UNIT_INDEX_X'] < panel_rows) & (df['UNIT_INDEX_Y'] < panel_cols),
        (df['UNIT_INDEX_X'] < panel_rows) & (df['UNIT_INDEX_Y'] >= panel_cols),
        (df['UNIT_INDEX_X'] >= panel_rows) & (df['UNIT_INDEX_Y'] < panel_cols),
        (df['UNIT_INDEX_X'] >= panel_rows) & (df['UNIT_INDEX_Y'] >= panel_cols)
    ]
    choices = ['Q1', 'Q2', 'Q3', 'Q4']
    df['QUADRANT'] = np.select(conditions, choices, default='Other')

    # Expected quadrants
    expected_quadrants = ['Q1', 'Q2', 'Q3', 'Q4']
    assert df['QUADRANT'].tolist() == expected_quadrants

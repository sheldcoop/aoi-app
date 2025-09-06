import pytest
import pandas as pd
import io

# Make sure the app's root directory is in the path
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.reporting import generate_excel_report

@pytest.fixture
def sample_full_df():
    """Fixture for a sample DataFrame representing the full dataset."""
    data = {
        'UNIT_INDEX_X': [1, 6, 1, 8],
        'UNIT_INDEX_Y': [1, 1, 8, 8],
        'DEFECT_TYPE': ['Nick', 'Short', 'Cut', 'Island'],
        'QUADRANT': ['Q1', 'Q2', 'Q3', 'Q4']
    }
    return pd.DataFrame(data)

def test_generate_excel_report(sample_full_df):
    """
    Test the Excel report generation.
    Checks if the output is a valid Excel file in bytes with the correct sheets.
    """
    panel_rows = 5
    panel_cols = 5

    # Generate the report
    excel_bytes = generate_excel_report(sample_full_df, panel_rows, panel_cols)

    # 1. Check if the output is bytes and is not empty
    assert isinstance(excel_bytes, bytes)
    assert len(excel_bytes) > 0

    # 2. Check if it's a valid Excel file by trying to read it
    try:
        excel_file = pd.ExcelFile(io.BytesIO(excel_bytes), engine='openpyxl')
    except Exception as e:
        pytest.fail(f"Could not read the generated Excel bytes: {e}")

    # 3. Check if the expected sheets are present
    expected_sheets = [
        'Quarterly Summary',
        'Q1 Top Defects',
        'Q2 Top Defects',
        'Q3 Top Defects',
        'Q4 Top Defects',
        'Full Defect List'
    ]
    assert all(sheet in excel_file.sheet_names for sheet in expected_sheets)

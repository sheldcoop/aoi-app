# Wafer Defect Analysis Dashboard

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)](https://github.com/your-repo/actions)

An interactive web application built with Streamlit for visualizing and analyzing semiconductor wafer defect data. This tool is designed to help engineers and technicians quickly identify, analyze, and report on defect patterns on semiconductor wafers or similar panel-based products.

The application is built with a modular structure, making the code clean, maintainable, and easy to extend.

## Features

- **Interactive Defect Map**: Visualize the spatial distribution of different defect types across a 2x2 panel layout.
- **Dynamic Grid Configuration**: Customize the grid dimensions (rows and columns) of each panel to match your specific wafer layout.
- **True Pareto Analysis**: A proper Pareto chart that identifies the most significant defect types by count and shows the cumulative impact, helping to prioritize quality improvement efforts.
- **Quadrant Filtering**: Isolate and analyze data from any of the four quadrants (Q1-Q4) or view all quadrants at once.
- **File Uploader**: Easily upload one or more of your own defect data files (`.xlsx`, `.xls`).
- **Sample Data**: The application loads with sample data, so you can explore its features without needing your own file.
- **Comprehensive Summary View**: Get key performance indicators (KPIs) like defect density and estimated yield, plus a breakdown of defect types.
- **Excel Report Generation**: Download a professionally formatted, multi-sheet Excel report of the complete dataset with a single click.

## How to Run This Application

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd wafer-defect-analysis-dashboard
    ```

2.  **Install the required libraries:**
    It is recommended to create a virtual environment first.
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3.  **Run the Streamlit app:**
    ```bash
    streamlit run app.py
    ```
    The application will open in your web browser. You can then upload your own Excel file(s) using the "Upload Your Defect Data" button in the sidebar.

## Development

This project uses `pytest` for unit testing. To run the tests:

1.  Make sure you have installed the development dependencies from `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```

2.  Run the test suite from the root directory:
    ```bash
    pytest
    ```

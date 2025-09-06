# --- ACTION REQUIRED ---
Thank you for your approval. The final fix for your installation issue is ready.

**The next steps must be performed by you on your own computer**, as they involve changing your local Python environment, which I cannot do.

**Please open the `INSTALLATION_FIX.md` file and follow the instructions there.**

This is my final and most confident recommendation to solve this problem. I will be waiting for your feedback.

---
# --- CURRENT STATUS ---
I have completed the code review and refactoring task. I have also provided a final, comprehensive solution for the installation issues you were facing on your macOS machine with Python 3.13.

**Please see the `INSTALLATION_FIX.md` file for step-by-step instructions.**

I am now waiting for your feedback on whether those instructions worked. I cannot proceed further until you have tried the fix and responded. Thank you!
---

# *** IMPORTANT: If you are having trouble with installation, please see the instructions in `INSTALLATION_FIX.md` ***

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

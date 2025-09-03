Wafer Defect Analysis Dashboard
This is an interactive web application built with Streamlit for visualizing and analyzing semiconductor wafer defect data.

This application is built from modular Python files located in the src/ directory, making the code clean, maintainable, and easy to debug.

Features
Interactive Defect Map: Visualize the spatial distribution of different defect types.

Pareto Analysis: Quickly identify the most common defects across the entire wafer or within a specific quadrant.

Dynamic Grid: Configure the dimensions of the wafer map to match your data.

Quadrant Filtering: Isolate and analyze data from one of the four quadrants (Q1-Q4).

How to Run This Application
Clone the repository:

git clone <your-repository-url>
cd defect-analysis-app

Install the required libraries:

pip install -r requirements.txt

Place your data file (e.g., my_defects.xlsx) inside the data/ directory.
Note: You will need to update the data_handler.py file to read from your specific file.

Run the Streamlit app from your terminal:

streamlit run app.py

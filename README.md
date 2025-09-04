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

Run the Streamlit app from your terminal:

streamlit run app.py

Once the app is running, use the "Control Panel" on the sidebar to upload your own defect data in Excel format. The app will dynamically update with your data. If no file is uploaded, the app will display a sample dataset.

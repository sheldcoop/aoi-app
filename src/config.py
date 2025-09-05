# src/config.py
# This module contains all configuration and styling variables for the application.

# --- Style Theme: Post-Etch AOI Panel ---
# This palette is designed to look like a copper-clad panel from the PCB/IC Substrate industry.

PANEL_COLOR = '#E58A60'
GRID_COLOR = 'black'
BACKGROUND_COLOR ='white'
PLOT_AREA_COLOR = '#F4A460'
TEXT_COLOR = 'black'       # White text for readability on the dark background.

# --- UI Element Styling ---
BUTTON_COLOR = '#4CAF50'        # A pleasant green
BUTTON_HOVER_COLOR = '#45a049'  # A slightly darker green for hover
BUTTON_BORDER_COLOR = '#4A4A4A' # A dark grey for the border

# --- Defect Styling (Unchanged) ---
defect_style_map = {
    'Nick': 'magenta', 'Short': 'red', 'Missing Feature': 'lime', 'Cut': 'cyan',
    'Fine Short': '#DDA0DD', 'Pad Violation': 'white', 'Island': 'orange',
    'Cut/Short': '#00BFFF', 'Nick/Protrusion': 'yellow'
}


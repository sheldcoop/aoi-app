# src/config.py
# This module contains all configuration and styling variables for the application.

# --- Style Theme: Post-Etch AOI Panel ---
# This palette is designed to look like a copper-clad panel from the PCB/IC Substrate industry.

PANEL_COLOR = '#E58A60'
GRID_COLOR = 'black'
BACKGROUND_COLOR ='white'
PLOT_AREA_COLOR = '#F4A460'
TEXT_COLOR = 'black'       # White text for readability on the dark background.

# --- Defect Styling (Unchanged) ---
defect_style_map = {
    'Nick': 'magenta', 'Short': 'red', 'Missing Feature': 'lime', 'Cut': 'cyan',
    'Fine Short': '#DDA0DD', 'Pad Violation': 'white', 'Island': 'orange',
    'Cut/Short': '#00BFFF', 'Nick/Protrusion': 'yellow'
}


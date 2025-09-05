# src/config.py
# This module contains all configuration and styling variables for the application.

# --- Style Theme: Post-Etch AOI Panel ---
# This palette is designed to look like a copper-clad panel from the PCB/IC Substrate industry.

PANEL_COLOR = '#8B4513'
GRID_COLOR = '#FFFFFF'
BACKGROUND_COLOR = 'white'
PLOT_AREA_COLOR = '#F4A460'
TEXT_COLOR = '#FFFFFF'       # White text for readability on the dark background.

# --- Defect Styling (Unchanged) ---
defect_style_map = {
    'Nick': 'magenta', 'Short': 'red', 'Missing Feature': 'lime', 'Cut': 'cyan',
    'Fine Short': '#DDA0DD', 'Pad Violation': 'white', 'Island': 'orange',
    'Cut/Short': '#00BFFF', 'Nick/Protrusion': 'yellow'
}


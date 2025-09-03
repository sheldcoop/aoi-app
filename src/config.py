# src/config.py
# This module contains all configuration and styling variables for the application.

# --- Style Theme: Post-Etch AOI Panel ---
# This palette is designed to look like a copper-clad panel from the PCB/IC Substrate industry.

PANEL_COLOR = '#B87333'      # A metallic, classic copper color for the panels.
GRID_COLOR = '#000000'       # Black for the main grid lines for high contrast.
BACKGROUND_COLOR = '#212121' # A dark charcoal grey for the app background, mimicking an inspection machine.
PLOT_AREA_COLOR = '#333333'  # A slightly lighter grey for the plot area to create subtle depth.
TEXT_COLOR = '#FFFFFF'       # White text for readability on the dark background.

# --- Defect Styling (Unchanged) ---
defect_style_map = {
    'Nick': 'magenta', 'Short': 'red', 'Missing Feature': 'lime', 'Cut': 'cyan',
    'Fine Short': '#DDA0DD', 'Pad Violation': 'white', 'Island': 'orange',
    'Cut/Short': '#00BFFF', 'Nick/Protrusion': 'yellow'
}


# src/config.py
# This module contains all configuration and styling variables for the application.

# --- Defect Styling ---
# This map is constant across all themes.
# Note: 'Pad Violation' color changed from 'white' to 'grey' for better visibility on light themes.
defect_style_map = {
    'Nick': 'magenta',
    'Short': 'red',
    'Missing Feature': 'lime',
    'Cut': 'cyan',
    'Fine Short': '#DDA0DD',
    'Pad Violation': 'grey',  # Changed from white for better visibility
    'Island': 'orange',
    'Cut/Short': '#00BFFF',
    'Nick/Protrusion': 'yellow'
}

# --- UI Themes ---
# Contains color palettes for different UI themes.
THEMES = {
    "Dark": {
        "PANEL_COLOR": '#B87333',      # A metallic, classic copper color for the panels.
        "GRID_COLOR": '#000000',       # Black for the main grid lines for high contrast.
        "BACKGROUND_COLOR": '#212121', # A dark charcoal grey for the app background.
        "PLOT_AREA_COLOR": '#333333',  # A slightly lighter grey for the plot area.
        "TEXT_COLOR": '#FFFFFF'        # White text for readability.
    },
    "Light": {
        "PANEL_COLOR": '#D2E3FC',      # A soft, professional light blue for panels.
        "GRID_COLOR": '#4F8BFF',       # A stronger, clear blue for grid lines.
        "BACKGROUND_COLOR": '#FFFFFF', # Clean white background.
        "PLOT_AREA_COLOR": '#F0F2F6',   # A very light grey for the plot area to give subtle depth.
        "TEXT_COLOR": '#000000'        # Black text for maximum readability.
    }
}

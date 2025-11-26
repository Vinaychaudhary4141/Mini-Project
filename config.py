# Grid configuration
GRID_SIZE = 10          # 10×10 grid
CELL_SIZE = 60          # each cell = 60 pixels

# Simulation parameters
FPS = 60                # backend won't use this, pygame did

# UI layout (used only in original pygame)
LEFT_PANEL_WIDTH = 400
WINDOW_WIDTH = GRID_SIZE * CELL_SIZE + LEFT_PANEL_WIDTH
WINDOW_HEIGHT = GRID_SIZE * CELL_SIZE

# Colors (not used by backend)
BACKGROUND_COLOR = (245, 245, 245)

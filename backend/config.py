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
# --- Reward / RL shaping constants (Hybrid) ---
REWARD_PICKUP = 5.0
REWARD_DELIVER = 10.0
REWARD_MOVE = -0.05           # small penalty per movement step
REWARD_AVOID = 1.0            # positive for successful obstacle avoidance (replanning)
REWARD_BLOCKED = -5.0         # penalty when no path can be found
REWARD_LOW_BATTERY = -3.0
REWARD_RETURN_BASE = 2.0
REWARD_SHORT_PATH_MULTIPLIER = 0.5  # bonus multiplied by (GRID_SIZE - path_len)
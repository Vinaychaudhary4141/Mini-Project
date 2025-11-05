import config

def get_cell_center(grid_cells, label):
    if label in grid_cells:
        rect = grid_cells[label]
        return (rect.centerx, rect.centery)
    return None

def pixel_to_grid(pos):
    col = int(pos[0] // config.CELL_SIZE)
    row = int(pos[1] // config.CELL_SIZE)
  
    # Clamp values to be within the grid
    row = max(0, min(row, config.GRID_SIZE - 1))
    col = max(0, min(col, config.GRID_SIZE - 1))
    return (row, col)

def grid_to_pixel_center(pos):
    row, col = pos
    x = col * config.CELL_SIZE + config.CELL_SIZE // 2
    y = row * config.CELL_SIZE + config.CELL_SIZE // 2
    return (x, y)

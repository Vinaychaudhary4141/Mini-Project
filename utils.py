import config

def pixel_to_grid(pos):
    """
    Convert pixel position to grid cell (row, col)
    using the SAME grid that grid_cells uses.
    """
    x, y = pos

    col = int(x // config.CELL_SIZE)
    row = int(y // config.CELL_SIZE)

    # Clamp values
    row = max(0, min(row, config.GRID_SIZE - 1))
    col = max(0, min(col, config.GRID_SIZE - 1))

    return (row, col)


def grid_to_pixel_center(pos):
    """
    Convert grid (row, col) to the REAL pixel center used by grid_cells.
    """
    row, col = pos
    x = col * config.CELL_SIZE + config.CELL_SIZE // 2
    y = row * config.CELL_SIZE + config.CELL_SIZE // 2
    return (x, y)


def get_cell_center(grid_cells, label):
    """
    Use the REAL grid cell coordinates directly.
    Ensures pickup/drop ALWAYS match drone’s perception.
    """
    if label in grid_cells:
        rect = grid_cells[label]
        return (rect.centerx, rect.centery)
    return None

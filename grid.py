import pygame
import config

def draw_grid(surface, font, grid_cells, obstacles_rects):
    for label, rect in grid_cells.items():
        if rect in obstacles_rects:
            pygame.draw.rect(surface, config.OBSTACLE_COLOR, rect)
        else:
            pygame.draw.rect(surface, config.GRID_LINE_COLOR, rect, 1)

        text = font.render(label, True, config.TEXT_COLOR)
        surface.blit(text, (rect.x + 5, rect.y + 5))

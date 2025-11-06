import pygame
import config

def draw_ui_panel(surface, font, drones):
    panel_rect = pygame.Rect(config.LEFT_PANEL_WIDTH, 0, config.WINDOW_WIDTH - config.LEFT_PANEL_WIDTH, config.WINDOW_HEIGHT)
    pygame.draw.rect(surface, config.UI_PANEL_COLOR, panel_rect)
    
    info_y = 470
    title_text = font.render("--- Drone Status ---", True, config.INFO_TEXT_COLOR)
    surface.blit(title_text, (config.LEFT_PANEL_WIDTH + 30, info_y))
    
    for i, drone in enumerate(drones):
        battery_level = int(drone.battery)
        color = (0, 255, 0) if battery_level > drone.low_battery_threshold else (255, 0, 0)
        
        info_text = font.render(f"Bot {drone.id} | State: {drone.state.upper()}", True, config.INFO_TEXT_COLOR)
        surface.blit(info_text, (config.LEFT_PANEL_WIDTH + 30, info_y + 30 + i*50))
        
        battery_text = font.render(f"Battery: {battery_level}%", True, color)
        surface.blit(battery_text, (config.LEFT_PANEL_WIDTH + 30, info_y + 55 + i*50))

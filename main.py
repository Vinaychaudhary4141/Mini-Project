import pygame
import pygame_gui
import random
import math

# Import our new modules
import config
import utils
from aiml.agent import Drone
from ui.grid import draw_grid
from ui.panel import draw_ui_panel

def main():
    pygame.init()

    # WINDOW SETUP 
    screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
    pygame.display.set_caption("Modular Drone Delivery Simulation")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    # UI MANAGER 
    manager = pygame_gui.UIManager((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
    input_rect = pygame.Rect(config.LEFT_PANEL_WIDTH + 20, 40, 350, 40)
    text_entry = pygame_gui.elements.UITextEntryLine(relative_rect=input_rect, manager=manager)
    log_rect = pygame.Rect(config.LEFT_PANEL_WIDTH + 20, 100, 350, 350)
    log_box = pygame_gui.elements.UITextBox(html_text="<b>Command Log</b><br>Click grid to add/remove obstacles.<br>", relative_rect=log_rect, manager=manager)

    # GRID & OBSTACLE SETUP 
    grid_cells = {}
    for row in range(config.GRID_SIZE):
        for col in range(config.GRID_SIZE):
            label = f"{chr(65 + row)}{col + 1}"
            rect = pygame.Rect(col * config.CELL_SIZE, row * config.CELL_SIZE, config.CELL_SIZE, config.CELL_SIZE)
            grid_cells[label] = rect

    obstacle_labels = random.sample(list(grid_cells.keys()), 15)
    obstacles_rects = [grid_cells[label] for label in obstacle_labels]
    obstacle_grid_coords = {utils.pixel_to_grid(r.topleft) for r in obstacles_rects}

    def toggle_obstacle(grid_pos):
        label = f"{chr(65 + grid_pos[0])}{grid_pos[1] + 1}"
        rect = grid_cells[label]
        if grid_pos in obstacle_grid_coords:
            obstacle_grid_coords.remove(grid_pos)
            obstacle_labels.remove(label)
            obstacles_rects.remove(rect)
        else:
            obstacle_grid_coords.add(grid_pos)
            obstacle_labels.append(label)
            obstacles_rects.append(rect)

    # CREATE DRONES 
    drones = [
        Drone(1, 30, 30, 'drone_icon.png'),
        Drone(2, 90, 30, 'drone_icon.png')
    ]

    # MAIN LOOP 
    running = True
    while running:
        time_delta = clock.tick(config.FPS) / 1000.0

        # EVENT HANDLING 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if event.pos[0] < config.LEFT_PANEL_WIDTH:
                    grid_pos = utils.pixel_to_grid(event.pos)
                    toggle_obstacle(grid_pos)

            if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                text = event.text.strip().upper()
                try:
                    pickup_label, drop_label = text.split()
                    if pickup_label in obstacle_labels or drop_label in obstacle_labels:
                        log_box.append_html_text("<font color='red'>Cannot set task in an obstacle!</font><br>")
                    else:
                        pickup = utils.get_cell_center(grid_cells, pickup_label)
                        drop = utils.get_cell_center(grid_cells, drop_label)
                        if not pickup or not drop: raise ValueError

                        available_drones = [d for d in drones if d.state == "idle" and d.battery > d.low_battery_threshold]
                        
                        if not available_drones:
                            log_box.append_html_text("<font color='orange'>All drones are busy or have low battery.</font><br>")
                        else:
                            closest_drone = min(available_drones, key=lambda d: math.hypot(d.x - pickup[0], d.y - pickup[1]))
                            closest_drone.set_task(pickup, drop)
                            log_box.append_html_text(f"<b>Bot {closest_drone.id}</b> auto-assigned task {pickup_label} → {drop_label}<br>")
                except Exception:
                    log_box.append_html_text("<font color='red'>Invalid format! Use: A1 G8</font><br>")

            manager.process_events(event)

        # UPDATES 
        manager.update(time_delta)
        for drone in drones:
            log_message = drone.update(obstacle_grid_coords)
            if log_message:
                log_box.append_html_text(log_message)

        # DRAWING 
        screen.fill(config.BACKGROUND_COLOR)
        draw_grid(screen, font, grid_cells, obstacles_rects)
        draw_ui_panel(screen, font, drones)
        for drone in drones:
            drone.draw(screen, font)
        manager.draw_ui(screen)
        
        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()

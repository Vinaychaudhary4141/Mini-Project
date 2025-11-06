import pygame
import math
import random

# Import from other project files
from utils import pixel_to_grid, grid_to_pixel_center
from aiml.pathfinding import astar_pathfinding
import config

class Drone:
    def __init__(self, id, x, y, image_path):
        self.id = id
        self.x = x
        self.y = y
        self.task = None
        self.state = "idle"
        self.speed = config.DRONE_SPEED
        self.package = False
        self.path = []
        self.current_waypoint_index = 0
        self.battery = config.DRONE_BATTERY_START
        self.low_battery_threshold = config.DRONE_LOW_BATTERY_THRESHOLD

        # Q-Learning Attributes
        # The Q-Table: maps state (grid label) to action values [Stay, GoToDepot]
        self.q_table = {f"{chr(65+r)}{c+1}": [0.0, 0.0] for r in range(10) for c in range(10)}
        self.learning_rate = 0.1
        self.discount_factor = 0.9
        self.epsilon = 0.2

        # Memory for the last strategic decision
        self.last_strategic_state_label = None
        self.last_strategic_action = None

        try:
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (40, 40))
        except pygame.error:
            print(f"Cannot load image at {image_path}.")
            self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (0, 255, 0), (15, 15), 15)

    def choose_strategic_action(self):
        """Uses Q-table to decide what to do next (Stay or Go to Depot)."""
        current_grid_pos = pixel_to_grid((self.x, self.y))
        self.last_strategic_state_label = f"{chr(65 + current_grid_pos[0])}{current_grid_pos[1] + 1}"

        if random.uniform(0, 1) < self.epsilon:
            self.last_strategic_action = random.choice([0, 1])
        else:
            q_values = self.q_table[self.last_strategic_state_label]
            self.last_strategic_action = q_values.index(max(q_values))

        if self.last_strategic_action == 1:
            depot_coords = grid_to_pixel_center((0, 0))
            self.set_task(depot_coords, depot_coords, is_strategic=True)
            return f"<font color='cyan'>Bot {self.id} is returning to Depot.</font><br>"
        else:
            return f"<font color='cyan'>Bot {self.id} is staying put.</font><br>"

    def set_task(self, pickup_coords, drop_coords, is_strategic=False):
        if self.last_strategic_state_label is not None and not is_strategic:
            travel_dist = math.hypot(pickup_coords[0] - self.x, pickup_coords[1] - self.y)
            reward = (config.WINDOW_WIDTH - travel_dist) / 100

            if self.last_strategic_action == 1:
                reward -= 5

            old_q_value = self.q_table[self.last_strategic_state_label][self.last_strategic_action]
            
            current_grid_pos = pixel_to_grid((self.x, self.y))
            next_state_label = f"{chr(65 + current_grid_pos[0])}{current_grid_pos[1] + 1}"
            future_optimal_value = max(self.q_table[next_state_label])

            new_q_value = old_q_value + self.learning_rate * \
                          (reward + self.discount_factor * future_optimal_value - old_q_value)
            
            self.q_table[self.last_strategic_state_label][self.last_strategic_action] = new_q_value
            self.last_strategic_state_label = None
        
        self.task = {"pickup": pickup_coords, "drop": drop_coords, "is_strategic_move": is_strategic}
        self.state = "to_pickup"
        self.package = False
        self.path = []
        self.current_waypoint_index = 0

    def move_along_path(self):
        log_message = None
        if self.battery > 0:
            drain_rate = config.DRAIN_RATE_WITH_PACKAGE if self.package else config.DRAIN_RATE_IDLE
            self.battery -= drain_rate
        else:
            self.battery = 0
            log_message = f"<font color='red'>Bot {self.id}: Out of battery!</font><br>"
            self.task = None
            self.state = "idle"
            return True, log_message
            
        if not self.path or self.current_waypoint_index >= len(self.path):
            return True, log_message

        target_pos = self.path[self.current_waypoint_index]
        tx, ty = target_pos
        dx, dy = tx - self.x, ty - self.y
        dist = math.hypot(dx, dy)

        if dist < self.speed:
            self.current_waypoint_index += 1
            if self.current_waypoint_index >= len(self.path):
                return True, log_message
            return False, log_message

        self.x += self.speed * dx / dist
        self.y += self.speed * dy / dist
        return False, log_message

    def update(self, obstacle_grid_coords):
        log_message = None
        if self.task is None:
            if self.state != 'idle':
                 self.state = 'idle'
            return None

        # DYNAMIC RE-PLANNING LOGIC 
        if self.path:
            if self.current_waypoint_index < len(self.path):
                next_waypoint_pixel = self.path[self.current_waypoint_index]
                next_waypoint_grid = pixel_to_grid(next_waypoint_pixel)
                
                if next_waypoint_grid in obstacle_grid_coords:
                    self.path = []
                    log_message = f"<font color='orange'>Bot {self.id}: Obstacle detected! Re-planning path...</font><br>"
        #  END OF RE-PLANNING LOGIC 

        if not self.path:
            start_grid = pixel_to_grid((self.x, self.y))
            end_grid = pixel_to_grid(self.task["pickup"]) if self.state == "to_pickup" else pixel_to_grid(self.task["drop"])
            
            path_grid = astar_pathfinding(config.GRID_SIZE, start_grid, end_grid, obstacle_grid_coords)

            if path_grid:
                self.path = [grid_to_pixel_center(p) for p in path_grid]
                self.current_waypoint_index = 0
            else:
                log_message = f"<font color='orange'>Bot {self.id}: Cannot find path!</font><br>"
                self.task = None
                self.state = "idle"
                return log_message

        reached_destination, move_log = self.move_along_path()
        if move_log:
             log_message = (log_message if log_message else "") + move_log

        if reached_destination:
            if self.task.get('is_strategic_move', False):
                self.task = None
                self.state = "idle"
                self.path = []
                return log_message

            if self.state == "to_pickup":
                self.state = "to_drop"
                self.package = True
                self.path = [] 
            elif self.state == "to_drop":
                self.state = "dropping"
            elif self.state == "dropping":
                self.package = False
                self.task = None
                self.state = "idle"
                self.path = []
                new_log = self.choose_strategic_action()
                log_message = (log_message if log_message else "") + new_log
        
        return log_message

    def draw(self, surface, font):
        if self.path and len(self.path) > self.current_waypoint_index:
            points = [(self.x, self.y)] + self.path[self.current_waypoint_index:]
            pygame.draw.lines(surface, config.PATH_COLOR, False, points, 2)

        img_rect = self.image.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(self.image, img_rect)
        
        label = font.render(f"Bot {self.id}", True, config.INFO_TEXT_COLOR)
        surface.blit(label, (self.x - 15, self.y - 35))
        
        if self.package:
            pygame.draw.rect(surface, (255, 255, 0), (self.x - 4, self.y + 12, 8, 8))

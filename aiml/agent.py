# aiml/agent.py
import math
import random

from utils import pixel_to_grid, grid_to_pixel_center
from aiml.pathfinding import astar_pathfinding
import config

class Drone:
    def __init__(self, id, x, y, image_path):
        self.id = id
        self.x = float(x)
        self.y = float(y)
        self.task = None
        self.state = "idle"
        self.speed = getattr(config, "DRONE_SPEED", 2.0)
        self.package = False
        self.path = []
        self.current_waypoint_index = 0
        self.battery = getattr(config, "DRONE_BATTERY_START", 100.0)
        self.low_battery_threshold = getattr(config, "DRONE_LOW_BATTERY_THRESHOLD", 20.0)

        # Q-Learning Attributes (kept)
        size = getattr(config, "GRID_SIZE", 10)
        self.q_table = {f"{chr(65+r)}{c+1}": [0.0, 0.0] for r in range(size) for c in range(size)}
        self.learning_rate = 0.1
        self.discount_factor = 0.9
        self.epsilon = 0.2

        self.last_strategic_state_label = None
        self.last_strategic_action = None

        # RL reward tracking
        self.reward_step = 0.0     # reward obtained in current update step
        self.reward_total = 0.0    # accumulated reward for current episode/task

        # used to compute short-path bonus on delivery
        self.current_task_pathlen = None

        # image load (defensive)
        try:
            import pygame
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (40, 40))
        except Exception:
            try:
                import pygame
                self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
                pygame.draw.circle(self.image, (0, 255, 0), (15, 15), 15)
            except Exception:
                self.image = None

    def _add_reward(self, amount):
        """Internal helper to add reward for the step and to total."""
        self.reward_step += float(amount)
        self.reward_total += float(amount)

    def choose_strategic_action(self):
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
            # small positive for returning safely
            self._add_reward(getattr(config, "REWARD_RETURN_BASE", 2.0))
            return f"Bot {self.id} returning to depot. (+{getattr(config, 'REWARD_RETURN_BASE', 2.0):.2f})"
        else:
            return f"Bot {self.id} staying idle."

    def set_task(self, pickup_coords, drop_coords, is_strategic=False):
        # Q-learning update for last strategic choice (kept from previous)
        if self.last_strategic_state_label is not None and not is_strategic:
            travel_dist = math.hypot(pickup_coords[0] - self.x, pickup_coords[1] - self.y)
            reward = (getattr(config, "WINDOW_WIDTH", 0) - travel_dist) / 100.0

            if self.last_strategic_action == 1:
                reward -= 5.0

            old_q_value = self.q_table[self.last_strategic_state_label][self.last_strategic_action]
            current_grid_pos = pixel_to_grid((self.x, self.y))
            next_state_label = f"{chr(65 + current_grid_pos[0])}{current_grid_pos[1] + 1}"
            future_optimal_value = max(self.q_table[next_state_label])
            new_q_value = old_q_value + self.learning_rate * (
                reward + self.discount_factor * future_optimal_value - old_q_value
            )
            self.q_table[self.last_strategic_state_label][self.last_strategic_action] = new_q_value
            self.last_strategic_state_label = None

        self.task = {"pickup": pickup_coords, "drop": drop_coords, "is_strategic_move": is_strategic}
        self.state = "to_pickup"
        self.package = False
        self.path = []
        self.current_waypoint_index = 0
        self.current_task_pathlen = None
        # no immediate reward here

    def move_along_path(self):
        """returns (reached_destination_bool, optional_log_message)"""
        self.reward_step = 0.0   # reset per-step reward accumulation at start of movement step
        log_message = None
        # battery drain and movement penalty/shaping
        if self.battery > 0:
            drain_rate = getattr(config, "DRAIN_RATE_WITH_PACKAGE", 0.05) if self.package else getattr(config, "DRAIN_RATE_IDLE", 0.02)
            self.battery -= drain_rate
            # per-step small penalty (shaping)
            self._add_reward(getattr(config, "REWARD_MOVE", -0.05))
        else:
            # out of battery penalty
            self.battery = 0.0
            self._add_reward(getattr(config, "REWARD_LOW_BATTERY", -3.0))
            log_message = f"Bot {self.id} out of battery. (-{abs(getattr(config,'REWARD_LOW_BATTERY',-3.0)):.2f})"
            self.task = None
            self.state = "idle"
            return True, log_message

        if not self.path or self.current_waypoint_index >= len(self.path):
            return True, log_message

        target_pos = self.path[self.current_waypoint_index]
        tx, ty = target_pos
        dx, dy = tx - self.x, ty - self.y
        dist = math.hypot(dx, dy)

        tolerance = getattr(config, "WAYPOINT_TOLERANCE", 1.0)
        if dist <= self.speed + tolerance:
            self.x, self.y = float(tx), float(ty)
            self.current_waypoint_index += 1
            if self.current_waypoint_index >= len(self.path):
                return True, log_message
            return False, log_message

        self.x += (dx / dist) * self.speed
        self.y += (dy / dist) * self.speed
        return False, log_message

    def update(self, obstacle_grid_coords):
        # reset step reward at beginning of update (so UI shows reward_step for this step)
        self.reward_step = 0.0
        log_message = None

        if self.task is None:
            if self.state != "idle":
                self.state = "idle"
            return None

        # dynamic replanning: if next waypoint or current cell is blocked -> replan and give small positive reward for avoiding
        if self.path and self.current_waypoint_index < len(self.path):
            next_waypoint_pixel = self.path[self.current_waypoint_index]
            next_waypoint_grid = pixel_to_grid(next_waypoint_pixel)
            current_grid = pixel_to_grid((self.x, self.y))

            if next_waypoint_grid in obstacle_grid_coords or current_grid in obstacle_grid_coords:
                self.path = []
                self._add_reward(getattr(config, "REWARD_AVOID", 1.0))
                log_message = f"Bot {self.id} obstacle detected — replanning. (+{getattr(config,'REWARD_AVOID',1.0):.2f})"

        # compute path if needed
        if not self.path:
            start_grid = pixel_to_grid((self.x, self.y))
            end_grid = pixel_to_grid(self.task["pickup"]) if self.state == "to_pickup" else pixel_to_grid(self.task["drop"])

            path_grid = astar_pathfinding(getattr(config, "GRID_SIZE", 10), start_grid, end_grid, obstacle_grid_coords)

            if path_grid:
                self.path = [grid_to_pixel_center(p) for p in path_grid]
                self.current_waypoint_index = 0
                self.current_task_pathlen = len(path_grid)  # store for short-path bonus
            else:
                # could not find path -> penalty
                self._add_reward(getattr(config, "REWARD_BLOCKED", -5.0))
                log_message = f"Bot {self.id} cannot find path. (-{abs(getattr(config,'REWARD_BLOCKED',-5.0)):.2f})"
                self.task = None
                self.state = "idle"
                return log_message

        reached_destination, move_log = self.move_along_path()
        if move_log:
            log_message = (log_message if log_message else "") + move_log

        if reached_destination:
            # strategic move finish
            if self.task.get("is_strategic_move", False):
                # no extra reward beyond the return base applied earlier
                self.task = None
                self.state = "idle"
                self.path = []
                return log_message

            if self.state == "to_pickup":
                # snap to pickup and give pickup reward
                self.x, self.y = self.task["pickup"]
                self.state = "to_drop"
                self.package = True
                self.path = []
                self._add_reward(getattr(config, "REWARD_PICKUP", 5.0))
                log_message = (log_message or "") + f"Bot {self.id} reached pickup. (+{getattr(config,'REWARD_PICKUP',5.0):.2f})"
            elif self.state == "to_drop":
                self.state = "dropping"
            elif self.state == "dropping":
                # delivered: base reward + short path bonus
                self.package = False
                base = getattr(config, "REWARD_DELIVER", 10.0)
                self._add_reward(base)
                bonus = 0.0
                if self.current_task_pathlen is not None:
                    bonus = max(0.0, (getattr(config, "GRID_SIZE", 10) - self.current_task_pathlen)) * getattr(config, "REWARD_SHORT_PATH_MULTIPLIER", 0.5)
                    if bonus > 0:
                        self._add_reward(bonus)
                total_gain = base + bonus
                log_message = (log_message or "") + f"Bot {self.id} delivered the package. (+{total_gain:.2f})"

                # reset state
                self.task = None
                self.state = "idle"
                self.path = []
                # after delivery, may choose strategic action
                strategic_msg = self.choose_strategic_action()
                # choose_strategic_action may add return_base reward and will also set a task if returning
                if strategic_msg:
                    log_message = (log_message or "") + " " + strategic_msg

        # return log message (string), reward_step accessible via attributes
        return log_message

    def draw(self, surface, font):
        try:
            import pygame
            if self.path and len(self.path) > self.current_waypoint_index:
                points = [(self.x, self.y)] + self.path[self.current_waypoint_index:]
                pygame.draw.lines(surface, getattr(config, "PATH_COLOR", (0, 120, 255)), False, points, 2)

            if self.image:
                img_rect = self.image.get_rect(center=(int(self.x), int(self.y)))
                surface.blit(self.image, img_rect)

            label = font.render(f"Bot {self.id}", True, getattr(config, "INFO_TEXT_COLOR", (0, 0, 0)))
            surface.blit(label, (self.x - 15, self.y - 35))

            if self.package:
                pygame.draw.rect(surface, (255, 255, 0), (int(self.x) - 4, int(self.y) + 12, 8, 8))
        except Exception:
            pass
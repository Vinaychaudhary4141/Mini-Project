import math
from aiml.rl_controller import RLController

class Drone:
    def __init__(self, drone_id, x, y, icon_path):
        self.id = drone_id
        self.x = x
        self.y = y
        self.icon_path = icon_path

        # Movement properties
        self.speed = 2.0  # smooth movement speed in pixels per step

        # Battery system
        self.battery = 100
        self.low_battery_threshold = 20

        # Task handling
        self.state = "idle"
        self.task = None

        # Targets
        self.pickup_point = None
        self.drop_point = None
        self.target = None  # used for returning to base

        # RL controller
        self.rl = RLController(grid_size=10)

        # used by RL reward shaping
        self.prev_dist_x = 0
        self.prev_dist_y = 0


    # -----------------------------------------------------
    # Assign delivery task (pickup pixel, drop pixel)
    # -----------------------------------------------------
    def set_task(self, pickup, drop):
        self.pickup_point = pickup
        self.drop_point = drop
        self.state = "to_pickup"
        self.task = {"pickup": pickup, "drop": drop}


    # -----------------------------------------------------
    # Utility: Check collision with obstacles
    # -----------------------------------------------------
    def _collides_with_obstacle(self, obstacles):
        col = int(self.x // 60)
        row = int(self.y // 60)
        return (row, col) in obstacles


    # -----------------------------------------------------
    # Apply RL step to move drone toward a target
    # -----------------------------------------------------
    def _rl_move(self, target, obstacles):
        new_x, new_y = self.rl.step(self, target, obstacles)

        # Smooth transition (keeps animations natural)
        dx = new_x - self.x
        dy = new_y - self.y
        dist = math.hypot(dx, dy)

        if dist < self.speed:
            self.x, self.y = new_x, new_y
        else:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed

        reached = (math.hypot(self.x - target[0], self.y - target[1]) < 12)
        return reached


    # -----------------------------------------------------
    # MAIN UPDATE LOOP
    # -----------------------------------------------------
    def update(self, obstacles):

        # Battery drain
        if self.state != "idle":
            self.battery -= 0.05
            if self.battery <= self.low_battery_threshold:
                self.state = "returning"
                self.target = (30, 30)
                return f"⚠ Bot {self.id}: Low Battery → Returning to base"

        # If idle → do nothing
        if self.state == "idle":
            return None

        # -----------------------------
        # MOVING TO PICKUP LOCATION
        # -----------------------------
        if self.state == "to_pickup":
            reached = self._rl_move(self.pickup_point, obstacles)

            if self._collides_with_obstacle(obstacles):
                return f"Bot {self.id}: Avoiding obstacle!"

            if reached:
                self.state = "to_drop"
                return f"Bot {self.id}: Picked package"


        # -----------------------------
        # MOVING TO DROP LOCATION
        # -----------------------------
        elif self.state == "to_drop":
            reached = self._rl_move(self.drop_point, obstacles)

            if self._collides_with_obstacle(obstacles):
                return f"Bot {self.id}: Avoiding obstacle!"

            if reached:
                self.state = "returning"
                self.target = (30, 30)
                return f"Bot {self.id}: Delivered package"


        # -----------------------------
        # RETURNING TO BASE
        # -----------------------------
        elif self.state == "returning":
            reached = self._rl_move(self.target, obstacles)

            if self._collides_with_obstacle(obstacles):
                return f"Bot {self.id}: Avoiding obstacle!"

            if reached:
                self.state = "idle"
                self.task = None
                return f"Bot {self.id}: Returned to base"

        return None

import math
import random

# Actions the drone can take in grid space
ACTIONS = [
    (0, 1),    # right
    (0, -1),   # left
    (1, 0),    # down
    (-1, 0),   # up
]

class RLController:
    def __init__(self, grid_size):
        self.grid_size = grid_size

    # ----------------------------------------------------
    # Convert pixel → grid coordinate
    # ----------------------------------------------------
    def pixel_to_grid(self, x, y):
        col = int(x // 60)
        row = int(y // 60)
        return (row, col)

    # ----------------------------------------------------
    # Reward function used by RL
    # ----------------------------------------------------
    def compute_reward(self, drone, target, obstacles):
        dr, dc = self.pixel_to_grid(drone.x, drone.y)
        tr, tc = self.pixel_to_grid(*target)

        # Negative reward for obstacles
        if (dr, dc) in obstacles:
            return -10

        # Large reward if goal reached
        if abs(dr - tr) < 1 and abs(dc - tc) < 1:
            return 20

        # Shaping: distance improvement
        dist_before = math.hypot(drone.prev_dist_x, drone.prev_dist_y)
        dist_now = math.hypot(dr - tr, dc - tc)

        reward = (dist_before - dist_now)

        return reward

    # ----------------------------------------------------
    # Select action (epsilon-greedy)
    # ----------------------------------------------------
    def choose_action(self, drone, target, obstacles):
        dr, dc = self.pixel_to_grid(drone.x, drone.y)
        tr, tc = self.pixel_to_grid(*target)

        # store previous dist
        drone.prev_dist_x = dr - tr
        drone.prev_dist_y = dc - tc

        # RL behavior: 80% greedy, 20% exploration
        if random.random() < 0.2:
            return random.choice(ACTIONS)

        # Greedy: pick action minimizing distance
        best_action = None
        best_dist = float('inf')

        for a in ACTIONS:
            nr, nc = dr + a[0], dc + a[1]

            # skip out of bounds
            if nr < 0 or nr >= self.grid_size or nc < 0 or nc >= self.grid_size:
                continue

            # skip obstacles
            if (nr, nc) in obstacles:
                continue

            dist = math.hypot(nr - tr, nc - tc)
            if dist < best_dist:
                best_dist = dist
                best_action = a

        return best_action if best_action else (0, 0)

    # ----------------------------------------------------
    # Apply RL step and return next pixel position
    # ----------------------------------------------------
    def step(self, drone, target, obstacles):
        dr, dc = self.pixel_to_grid(drone.x, drone.y)

        best_action = self.choose_action(drone, target, obstacles)

        nr = dr + best_action[0]
        nc = dc + best_action[1]

        # pixel coordinates
        new_x = nc * 60 + 30
        new_y = nr * 60 + 30

        return new_x, new_y
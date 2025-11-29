# backend/simulation.py
import math
from typing import List, Tuple, Dict
import config
from aiml.agent import Drone
import threading

# ---------------------------------------------
# Helper Functions
# ---------------------------------------------
def label_to_coord(label: str) -> Tuple[int, int]:
    """Convert 'A1' to (0,0), 'B4' to (1,3) etc."""
    row = ord(label[0].upper()) - 65
    col = int(label[1:]) - 1
    return (row, col)

def coord_to_center(row: int, col: int) -> Tuple[int, int]:
    """Convert cell (row,col) → pixel center (x,y)."""
    x = col * config.CELL_SIZE + config.CELL_SIZE // 2
    y = row * config.CELL_SIZE + config.CELL_SIZE // 2
    return (x, y)


# ---------------------------------------------
# MAIN SIMULATION CLASS
# ---------------------------------------------
class Simulation:
    def __init__(self):
        self.grid_size = config.GRID_SIZE
        self.cell_size = config.CELL_SIZE

        self.obstacle_grid_coords = set()

        # initialize drones
        self.drones = [
            Drone(1, 30, 30, 'drone_icon.png'),
            Drone(2, 90, 30, 'drone_icon.png')
        ]

        self.logs = []
        self._lock = threading.Lock()

    # ---------------------------------------------
    # Toggle obstacles
    # ---------------------------------------------
    def toggle_obstacle_by_label(self, label: str):
        try:
            r, c = label_to_coord(label)
        except Exception:
            return False

        with self._lock:
            if (r, c) in self.obstacle_grid_coords:
                self.obstacle_grid_coords.remove((r, c))
                self.logs.append(f"Removed obstacle {label}")
            else:
                self.obstacle_grid_coords.add((r, c))
                self.logs.append(f"Added obstacle {label}")
        return True

    # ---------------------------------------------
    # Assign Task
    # ---------------------------------------------
    def assign_task(self, pickup_label: str, drop_label: str) -> Dict:
        try:
            pickup_center = coord_to_center(*label_to_coord(pickup_label))
            drop_center = coord_to_center(*label_to_coord(drop_label))
        except Exception:
            return {"success": False, "message": "Invalid labels"}

        with self._lock:
            available = [
                d for d in self.drones
                if d.state == "idle" and getattr(d, "battery", 100) > getattr(d, "low_battery_threshold", 0)
            ]

            if not available:
                msg = "All drones are busy or have low battery."
                self.logs.append(msg)
                return {"success": False, "message": msg}

            # choose closest drone
            closest = min(
                available,
                key=lambda d: math.hypot(d.x - pickup_center[0], d.y - pickup_center[1])
            )

            closest.set_task(pickup_center, drop_center)
            msg = f"Bot {closest.id} assigned {pickup_label} → {drop_label}"
            self.logs.append(msg)

            return {"success": True, "message": msg, "drone_id": closest.id}

    # ---------------------------------------------
    # Step Simulation
    # ---------------------------------------------
    def step(self) -> List[str]:
        step_logs = []
        with self._lock:
            for d in self.drones:
                msg = d.update(self.obstacle_grid_coords)
                if msg:
                    step_logs.append(msg)
                    self.logs.append(msg)
        return step_logs

    # ---------------------------------------------
    # Reset Simulation
    # ---------------------------------------------
    def reset(self):
        with self._lock:
            self.obstacle_grid_coords.clear()
            self.logs.append("Environment reset")

            for idx, d in enumerate(self.drones):
                d.x = 30 + idx * 60
                d.y = 30
                d.state = "idle"
                d.task = None
                if hasattr(d, "battery"):
                    d.battery = 100
                if hasattr(d, "reward_total"):
                    d.reward_total = 0
                if hasattr(d, "reward_step"):
                    d.reward_step = 0

    # ---------------------------------------------
    # Get State (FINAL FIXED)
    # ---------------------------------------------
    def get_state(self):
        with self._lock:
            drones_state = []
            for d in self.drones:
                drones_state.append({
                    "id": d.id,
                    "x": d.x,
                    "y": d.y,
                    "state": d.state,
                    "battery": getattr(d, "battery", None),
                    "task": getattr(d, "task", None),

                    # Rewards for RL UI
                    "reward_step": getattr(d, "reward_step", 0),
                    "reward_total": getattr(d, "reward_total", 0)
                })

            obstacles = [{"row": r, "col": c} for (r, c) in list(self.obstacle_grid_coords)]
            logs = list(self.logs)

            return {
                "drones": drones_state,
                "obstacles": obstacles,
                "logs": logs,
                "grid_size": self.grid_size,
                "cell_size": self.cell_size
            }
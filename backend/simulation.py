# backend/simulation.py
import math
from typing import List, Tuple, Dict
import config   # your project config.py
from aiml.agent import Drone  # uses your existing Drone class
import threading

# Helper label <-> grid coord conversions (same logic as main.py)
def label_to_coord(label: str) -> Tuple[int,int]:
    # Expect labels like "A1", "B12" etc.
    row = ord(label[0].upper()) - 65
    col = int(label[1:]) - 1
    return (row, col)

def coord_to_center(row: int, col: int) -> Tuple[int,int]:
    # center pixel of the grid cell
    x = col * config.CELL_SIZE + config.CELL_SIZE // 2
    y = row * config.CELL_SIZE + config.CELL_SIZE // 2
    return (x, y)

class Simulation:
    def __init__(self):
        self.grid_size = config.GRID_SIZE
        self.cell_size = config.CELL_SIZE

        # obstacles set of (row, col)
        self.obstacle_grid_coords = set()

        # initialize drones using the same constructor you had
        self.drones = [
            Drone(1, 30, 30, 'drone_icon.png'),
            Drone(2, 90, 30, 'drone_icon.png')
        ]

        # logs
        self.logs = []
        # lock for thread-safety (not strictly necessary for step-driven)
        self._lock = threading.Lock()

    # toggle obstacle by label "A1"
    def toggle_obstacle_by_label(self, label: str):
        try:
            r,c = label_to_coord(label)
        except Exception:
            return False
        with self._lock:
            if (r,c) in self.obstacle_grid_coords:
                self.obstacle_grid_coords.remove((r,c))
                self.logs.append(f"Removed obstacle {label}")
            else:
                self.obstacle_grid_coords.add((r,c))
                self.logs.append(f"Added obstacle {label}")
        return True

    # assign task pickup_label and drop_label
    def assign_task(self, pickup_label: str, drop_label: str) -> Dict:
        try:
            pickup_center = coord_to_center(*label_to_coord(pickup_label))
            drop_center = coord_to_center(*label_to_coord(drop_label))
        except Exception:
            return {"success": False, "message": "Invalid labels"}

        with self._lock:
            # find available drones (same condition you used)
            available = [d for d in self.drones if d.state == "idle" and getattr(d, "battery", 100) > getattr(d, "low_battery_threshold", 0)]
            if not available:
                msg = "All drones are busy or have low battery."
                self.logs.append(msg)
                return {"success": False, "message": msg}

            # choose closest drone
            def dist(d):
                return math.hypot(d.x - pickup_center[0], d.y - pickup_center[1])
            closest = min(available, key=dist)
            closest.set_task(pickup_center, drop_center)
            msg = f"Bot {closest.id} assigned {pickup_label} → {drop_label}"
            self.logs.append(msg)
            return {"success": True, "message": msg, "drone_id": closest.id}

    # single step: call update() on each drone and collect logs
    def step(self) -> List[str]:
        step_logs = []
        with self._lock:
            for d in self.drones:
                msg = d.update(self.obstacle_grid_coords)   # **calls your Drone.update exactly**
                if msg:
                    step_logs.append(msg)
                    self.logs.append(msg)
        return step_logs

    # reset environment (keeps Drone class but resets their state/pos/battery)
    def reset(self):
        with self._lock:
            # reset obstacles and drones
            self.obstacle_grid_coords.clear()
            self.logs.append("Environment reset")
            # reset drones to initial positions (same as you had)
            for idx, d in enumerate(self.drones):
                d.x = 30 + idx * 60
                d.y = 30
                d.state = "idle"
                d.task = None
                if hasattr(d, "battery"):
                    d.battery = 100

    # return full state for frontend
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
                    "task": getattr(d, "task", None)
                })
            obstacles = [{"row": r, "col": c} for (r,c) in list(self.obstacle_grid_coords)]
            # include logs but do not clear here (so frontend can display)
            logs = list(self.logs)
            # you can optionally clear logs here if you want: self.logs.clear()
            return {
                "drones": drones_state,
                "obstacles": obstacles,
                "logs": logs,
                "grid_size": self.grid_size,
                "cell_size": self.cell_size
            }

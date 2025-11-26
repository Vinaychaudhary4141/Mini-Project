# backend/model.py
from pydantic import BaseModel
from typing import List, Optional

class ToggleObstacleRequest(BaseModel):
    label: str

class AssignTaskRequest(BaseModel):
    pickup: str
    drop: str

class DroneState(BaseModel):
    id: int
    x: float
    y: float
    state: str
    battery: Optional[float] = None
    task: Optional[dict] = None

class Obstacle(BaseModel):
    row: int
    col: int

class StateResponse(BaseModel):
    drones: List[DroneState]
    obstacles: List[Obstacle]
    logs: List[str]
    grid_size: int
    cell_size: int

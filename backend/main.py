from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.model import ToggleObstacleRequest, AssignTaskRequest
from backend.simulation import Simulation

app = FastAPI(title="Drone Simulation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

sim = Simulation()

@app.get("/state")
def get_state():
    return sim.get_state()

@app.post("/toggle_obstacle")
def toggle_obstacle(req: ToggleObstacleRequest):
    ok = sim.toggle_obstacle_by_label(req.label)
    return {"success": ok}

@app.post("/assign_task")
def assign_task(req: AssignTaskRequest):
    return sim.assign_task(req.pickup, req.drop)

@app.post("/step")
def step():
    sim.step()
    return sim.get_state()

@app.post("/reset")
def reset():
    sim.reset()
    return sim.get_state()
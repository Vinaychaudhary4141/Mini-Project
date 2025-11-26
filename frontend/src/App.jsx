import React, { useEffect, useState, useRef } from "react";
import axios from "axios";

const BACKEND = process.env.REACT_APP_BACKEND || "http://localhost:8000";

function App() {
  const [state, setState] = useState(null);
  const intervalRef = useRef(null);

  useEffect(() => {
    // initial fetch
    fetchState();

    // start stepping every 120ms
    intervalRef.current = setInterval(async () => {
      try {
        const res = await axios.post(`${BACKEND}/step`);
        setState(res.data);
      } catch (err) {
        // fallback: get state
        fetchState();
      }
    }, 120);

    return () => {
      clearInterval(intervalRef.current);
    };
  }, []);

  async function fetchState() {
    try {
      const res = await axios.get(`${BACKEND}/state`);
      setState(res.data);
    } catch (err) {
      console.error("fetch state error", err);
    }
  }

  async function toggleObstacle(label) {
    await axios.post(`${BACKEND}/toggle_obstacle`, { label });
    fetchState();
  }

  async function assignTask(pickup, drop) {
    await axios.post(`${BACKEND}/assign_task`, { pickup, drop });
    fetchState();
  }

  if (!state) return <div style={{padding:20}}>Loading...</div>;

  const gridSize = state.grid_size;
  const cellSize = state.cell_size;

  // convert obstacles into set for click detection
  const obsSet = new Set(state.obstacles.map(o => `${o.row}-${o.col}`));

  return (
    <div className="app">
      <div className="left">
        <div className="grid" style={{width: gridSize*cellSize, height: gridSize*cellSize}}>
          {/* cells as background grid lines (optional) */}
          {[...Array(gridSize)].map((_, r) => (
            [...Array(gridSize)].map((__, c) => {
              const left = c * cellSize;
              const top = r * cellSize;
              const label = `${String.fromCharCode(65 + r)}${c+1}`;
              const key = `cell-${r}-${c}`;
              const isObs = obsSet.has(`${r}-${c}`);
              return (
                <div
                  key={key}
                  className={"cell"}
                  style={{
                    left: left,
                    top: top,
                    width: cellSize - 2,
                    height: cellSize - 2,
                    background: isObs ? "#b22222" : "#fff",
                    border: "1px solid #eee",
                    position: "absolute",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: 12,
                    cursor: "pointer"
                  }}
                  onClick={() => toggleObstacle(label)}
                  title={label}
                >
                  <div style={{pointerEvents:"none"}}>{label}</div>
                </div>
              );
            })
          ))}
          {/* drones */}
          {state.drones.map(d => (
            <img
              key={"d"+d.id}
              src={`${process.env.PUBLIC_URL}/drone_icon.png`}
              alt="drone"
              className="drone"
              style={{
                left: d.x,
                top: d.y,
                width: cellSize * 0.8,
                height: cellSize * 0.8,
                position: "absolute",
                transform: "translate(-50%,-50%)",
                transition: "left 0.12s linear, top 0.12s linear"
              }}
            />
          ))}
        </div>
      </div>

      <div className="right">
        <h3>Controls</h3>
        <div>
          <button onClick={() => axios.post(`${BACKEND}/reset`)}>Reset</button>
          <button onClick={() => fetchState()}>Refresh</button>
        </div>

        <h4>Assign Task</h4>
        <TaskForm onAssign={assignTask} />
        <h4>Logs</h4>
        <div className="logs">
          {state.logs && state.logs.length ? state.logs.slice(-20).reverse().map((l,i) => <div key={i}>{l}</div>) : <div>No logs yet</div>}
        </div>

        <h4>Drones</h4>
        <ul>
          {state.drones.map(d => <li key={d.id}>Drone {d.id} — {d.state} — Battery: {d.battery?.toFixed(1) ?? "N/A"}</li>)}
        </ul>
      </div>
    </div>
  );
}

function TaskForm({ onAssign }) {
  const [text, setText] = useState("");
  async function submit() {
    const parts = text.trim().toUpperCase().split(/\s+/);
    if (parts.length !== 2) { alert("Use format: A1 G8"); return; }
    await onAssign(parts[0], parts[1]);
    setText("");
  }
  return (
    <div>
      <input value={text} onChange={e => setText(e.target.value)} placeholder="A1 G8" />
      <button onClick={submit}>Assign</button>
    </div>
  );
}

export default App;

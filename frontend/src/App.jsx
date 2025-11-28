import React, { useEffect, useState, useRef } from "react";
import axios from "axios";

const BACKEND = process.env.REACT_APP_BACKEND || "http://localhost:8000";

function App() {
  const [state, setState] = useState(null);
  const intervalRef = useRef(null);

  useEffect(() => {
    fetchState();

    intervalRef.current = setInterval(async () => {
      try {
        const res = await axios.post(`${BACKEND}/step`);
        setState(res.data);
      } catch {
        fetchState();
      }
    }, 120);

    return () => clearInterval(intervalRef.current);
  }, []);

  async function fetchState() {
    try {
      const res = await axios.get(`${BACKEND}/state`);
      setState(res.data);
    } catch (err) {
      console.error("Error fetching state:", err);
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

  if (!state)
    return <div style={{ padding: 20, fontSize: 20 }}>Loading...</div>;

  const gridSize = state.grid_size;
  const cellSize = state.cell_size;

  const obsSet = new Set(state.obstacles.map((o) => `${o.row}-${o.col}`));

  return (
    <div className="app">
      {/* LEFT GRID SECTION -------------------------------------------------- */}
      <div className="left">
        <div
          className="grid"
          style={{
            width: gridSize * cellSize,
            height: gridSize * cellSize,
            position: "relative",
            border: "2px solid #ccc",
            background: "#fafafa"
          }}
        >
          {/* GRID CELLS */}
          {[...Array(gridSize)].map((_, r) =>
            [...Array(gridSize)].map((__, c) => {
              const left = c * cellSize;
              const top = r * cellSize;
              const label = `${String.fromCharCode(65 + r)}${c + 1}`;
              const key = `cell-${r}-${c}`;
              const isObs = obsSet.has(`${r}-${c}`);

              return (
                <div
                  key={key}
                  className={isObs ? "cell obstacle": "cell"}
                  style={{
                    left,
                    top,
                    width: cellSize - 1,
                    height: cellSize - 1,
                    position: "absolute",
                    background: isObs ? "#d9534f" : "#ffffff",
                    border: "1px solid #e0e0e0",
                    fontSize: 12,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    cursor: "pointer",
                    color: "#444",
                    fontWeight: 500
                  }}
                  onClick={() => toggleObstacle(label)}
                >
                  {label}
                </div>
              );
            })
          )}

          {/* DRONES ---------------------------------------------------------- */}
          {state.drones.map((d) => (
            <img
              key={"drone-" + d.id}
              src={`${process.env.PUBLIC_URL}/drone_icon.png`}
              alt="drone"
              style={{
                position: "absolute",
                left: d.x,
                top: d.y,
                width: cellSize * 0.75,
                height: cellSize * 0.75,
                transform: "translate(-50%, -50%)",
                transition: "left 0.12s linear, top 0.12s linear",
                pointerEvents: "none"
              }}
            />
          ))}
        </div>
      </div>

      {/* RIGHT SIDEBAR ------------------------------------------------------ */}
      <div className="right">
        <h2>Drone Controller</h2>

        <button onClick={() => axios.post(`${BACKEND}/reset`)}>Reset</button>
        <button onClick={fetchState} style={{ marginLeft: 8 }}>
          Refresh
        </button>

        <h3 style={{ marginTop: 20 }}>Assign Delivery Task</h3>
        <TaskForm onAssign={assignTask} />

        <h3>Activity Log</h3>
        <div className="logs">
          {state.logs && state.logs.length ? (
            state.logs
              .slice(-20)
              .reverse()
              .map((log, i) => (
                <div key={i} className="log-entry">
                  {log.replace(/<[^>]+>/g, "")}
                </div>
              ))
          ) : (
            <div>No logs yet</div>
          )}
        </div>

        <h3>Drone Status</h3>
        <ul>
  {state.drones.map((d) => (
    <li key={d.id} style={{ marginBottom: 8 }}>
      <strong>Drone {d.id}</strong>
      <div style={{ fontSize: 13, color: "#555" }}>
        State: {d.state} — Battery: {d.battery?.toFixed(1) ?? "N/A"}
      </div>
      <div style={{ fontSize: 13, marginTop: 4 }}>
        Reward (step):{" "}
        <span style={{ color: d.reward_step >= 0 ? "green" : "crimson", fontWeight: 600 }}>
          {d.reward_step >= 0 ? "+" : ""}{d.reward_step?.toFixed(2) ?? "0.00"}
        </span>
        {"  "}
        Total: <span style={{ fontWeight: 700 }}>{d.reward_total?.toFixed(2) ?? "0.00"}</span>
      </div>
    </li>
  ))}
</ul>
      </div>
    </div>
  );
}

function TaskForm({ onAssign }) {
  const [text, setText] = useState("");

  function submit() {
    const parts = text.trim().toUpperCase().split(/\s+/);
    if (parts.length !== 2) {
      alert("Format: A1 G8");
      return;
    }
    onAssign(parts[0], parts[1]);
    setText("");
  }

  return (
    <div>
      <input
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="A1 G8"
      />
      <button onClick={submit}>Assign</button>
    </div>
  );
}

export default App;
"use client"

function PasteurizerControls({ simulationRunning, onStart, onStop, isLoading, connectionStatus }) {
  return (
    <div className="card">
      <h2>Simulation Controls</h2>

      <div className="controls-grid">
        <button
          className={`btn ${simulationRunning ? "btn-secondary" : "btn-primary"}`}
          onClick={onStart}
          disabled={simulationRunning || isLoading || connectionStatus !== "connected"}
        >
          {isLoading ? "⏳ Starting..." : simulationRunning ? "▶️ Running" : "▶️ Start Simulation"}
        </button>

        <button className="btn btn-error" onClick={onStop} disabled={!simulationRunning || isLoading}>
          {isLoading ? "⏳ Stopping..." : "⏹️ Stop Simulation"}
        </button>
      </div>

      <div className="status-info">
        <div className={`simulation-status ${simulationRunning ? "running" : "stopped"}`}>
          <div className="status-dot"></div>
          <span>{simulationRunning ? "Simulation Running" : "Simulation Stopped"}</span>
        </div>
      </div>

      {connectionStatus !== "connected" && (
        <div className="warning-message">
          ⚠️ Backend server must be running on http://127.0.0.1:3001 to start simulation
        </div>
      )}
    </div>
  )
}

export default PasteurizerControls

"use client"

function PasteurizerControls({
  simulationRunning,
  onStart,
  onStop,
  isLoading,
  connectionStatus,
  timeMode,
  onTimeModeChange,
}) {
  return (
    <div className="card">
      <h2>Simulation Controls</h2>

      {/* Time Scale Toggle - now controlled by parent */}
      <div className="time-scale-section">
        <h3>Time Scale Setting</h3>
        <div className="toggle-container">
          <label className="toggle-label">
            <input
              type="checkbox"
              checked={timeMode}
              onChange={(e) => onTimeModeChange(e.target.checked)}
              disabled={isLoading || simulationRunning}
            />
            <span className="toggle-text">{timeMode ? "🕐 Real-time (1)" : "⚡ Simulation-time (0)"}</span>
          </label>
        </div>
        <p className="toggle-description">
          {timeMode
            ? "Real-time mode: Simulation runs at actual speed"
            : "Simulation-time mode: Simulation runs as fast as possible"}
        </p>
      </div>

      <div className="controls-grid">
        <button
          className={`btn ${isLoading ? "btn-secondary" : "btn-primary"}`}
          onClick={onStart}
          disabled={isLoading || connectionStatus !== "connected" || simulationRunning}
        >
          {isLoading ? "⏳ Running..." : "🚀 Start Simulation"}
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
        <div className="time-mode-display">
          <span>Mode: {timeMode ? "Real-time" : "Simulation-time"}</span>
        </div>
      </div>

      {connectionStatus !== "connected" && (
        <div className="warning-message">
          ⚠️ Backend server must be running on http://127.0.0.1:3001 to start simulation
        </div>
      )}

      <style jsx>{`
        .time-scale-section {
          margin-bottom: 1.5rem;
          padding: 1rem;
          background-color: #f8fafc;
          border-radius: 0.5rem;
          border: 1px solid #e2e8f0;
        }

        .time-scale-section h3 {
          margin-bottom: 0.75rem;
          font-size: 1rem;
          font-weight: 600;
          color: #374151;
        }

        .toggle-container {
          margin-bottom: 0.5rem;
        }

        .toggle-label {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          cursor: pointer;
          font-weight: 500;
        }

        .toggle-label input[type="checkbox"] {
          width: 1.25rem;
          height: 1.25rem;
          accent-color: #3b82f6;
        }

        .toggle-text {
          font-size: 1rem;
          color: #1f2937;
        }

        .toggle-description {
          font-size: 0.875rem;
          color: #6b7280;
          margin: 0;
          font-style: italic;
        }

        .time-mode-display {
          margin-left: 1rem;
          padding: 0.25rem 0.75rem;
          background-color: #f1f5f9;
          border-radius: 0.375rem;
          font-size: 0.875rem;
          font-weight: 500;
          color: #475569;
        }
      `}</style>
    </div>
  )
}

export default PasteurizerControls

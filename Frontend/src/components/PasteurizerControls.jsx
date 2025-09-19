"use client"

import { useState } from "react"

function PasteurizerControls({ simulationRunning, onStart, onStop, isLoading, connectionStatus }) {
  const [timeScale, setTimeScale] = useState(false) // false = simtime (0), true = realtime (1)

  const handleQuickSim = async () => {
    const timeMode = timeScale ? "1" : "0"

    try {
      console.log(`🚀 Starting quick simulation with timeMode: ${timeMode}`)

      const response = await fetch("http://localhost:3001/api/quick", {
        method: "POST",
        headers: {
          "Content-Type": "text/plain",
        },
        body: timeMode,
      })

      const data = await response.json()

      if (data.success) {
        console.log("✅ Quick simulation completed:", data.result)
        alert(
          `Simulation completed!\n\nTimeMode: ${timeMode} (${timeScale ? "Real-time" : "Simulation-time"})\n\nCheck console for full results.`,
        )
      } else {
        console.error("❌ Simulation failed:", data.error)
        alert(`Simulation failed: ${data.error}`)
      }
    } catch (error) {
      console.error("❌ Network error:", error)
      alert(`Network error: ${error.message}`)
    }
  }

  return (
    <div className="card">
      <h2>Simulation Controls</h2>

      {/* Time Scale Toggle */}
      <div className="time-scale-section">
        <h3>Time Scale Setting</h3>
        <div className="toggle-container">
          <label className="toggle-label">
            <input
              type="checkbox"
              checked={timeScale}
              onChange={(e) => setTimeScale(e.target.checked)}
              disabled={isLoading}
            />
            <span className="toggle-text">{timeScale ? "🕐 Real-time (1)" : "⚡ Simulation-time (0)"}</span>
          </label>
        </div>
        <p className="toggle-description">
          {timeScale
            ? "Real-time mode: Simulation runs at actual speed"
            : "Simulation-time mode: Simulation runs as fast as possible"}
        </p>
      </div>

      <div className="controls-grid">
        <button
          className={`btn ${isLoading ? "btn-secondary" : "btn-primary"}`}
          onClick={handleQuickSim}
          disabled={isLoading || connectionStatus !== "connected"}
        >
          {isLoading ? "⏳ Running..." : "🚀 Start Quick Simulation"}
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
      `}</style>
    </div>
  )
}

export default PasteurizerControls

"use client"

import { useState } from "react"

function SimulationResults({ results, isRunning }) {
  const [logExpanded, setLogExpanded] = useState(false)

  // 🩵 Early fallback if no data
  if (!results || Object.keys(results).length === 0) {
    return (
      <div className="card">
        <h2>📊 Simulation Results</h2>
        <div className="no-data">
          {isRunning ? "⏳ Waiting for simulation data..." : "🎯 Start a simulation to see results"}
        </div>
      </div>
    )
  }

  // 🧩 Normalize structure (handles both live + final payloads)
  const progress = results.progress ?? results.current_progress ?? 0
  const finalResults = results.final_results || results

  // 🩵 Helpful debug output in console
  console.log("🔍 Rendering SimulationResults:", results)

  return (
    <div className="card">
      <h2>📊 Simulation Results</h2>

      {/* Real-time Status */}
      {isRunning && (
        <div className="real-time-status">
          <h3>🔄 Real-time Status</h3>
          <div className="status-grid">
            <div className="status-item">
              <label>Current Step</label>
              <span>{results.current_step ?? 0}</span>
            </div>
            <div className="status-item">
              <label>Temperature</label>
              <span>{Number(results.temperature)?.toFixed(1) ?? 0}°C</span>
            </div>
            <div className="status-item">
              <label>Start Tank</label>
              <span>{Number(results.start_tank)?.toFixed(1) ?? 0}L</span>
            </div>
            <div className="status-item">
              <label>Balance Tank</label>
              <span>{Number(results.balance_tank)?.toFixed(1) ?? 0}L</span>
            </div>
            <div className="status-item">
              <label>Pasteurized</label>
              <span>{Number(results.pasteurized_total)?.toFixed(1) ?? 0}L</span>
            </div>
            <div className="status-item">
              <label>Burnt</label>
              <span>{Number(results.burnt_total)?.toFixed(1) ?? 0}L</span>
            </div>
          </div>

          <div className="progress-section">
            <div className="progress-header">
              <span>Progress: {progress.toFixed(1)}%</span>
              <span>{results.status || "Processing..."}</span>
            </div>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${progress}%` }}></div>
            </div>
          </div>
        </div>
      )}

      {/* Final Results */}
      {finalResults && (
        <div className="final-results">
          <h3>✅ Final Results</h3>
          <div className="results-grid">
            <div className="result-card success">
              <div className="result-value">
                {Number(finalResults.pasteurized_total)?.toFixed(1) ?? 0}L
              </div>
              <div className="result-label">Pasteurized</div>
              <div className="result-percentage">
                {Number(finalResults.efficiency)?.toFixed(1) ?? 0}%
              </div>
            </div>

            <div className="result-card error">
              <div className="result-value">
                {Number(finalResults.burnt_total)?.toFixed(1) ?? 0}L
              </div>
              <div className="result-label">Burnt/Waste</div>
              <div className="result-percentage">
                {Number(finalResults.waste_percentage)?.toFixed(1) ?? 0}%
              </div>
            </div>

            <div className="result-card info">
              <div className="result-value">
                {Number(finalResults.total_milk)?.toFixed(1) ?? 0}L
              </div>
              <div className="result-label">Total Processed</div>
              <div className="result-percentage">100%</div>
            </div>
          </div>

          {/* Process Log */}
          {finalResults.log_data && Array.isArray(finalResults.log_data) && (
            <div className="process-log">
              <div className="log-header">
                <h4>📋 Process Log</h4>
                <button className="btn btn-secondary" onClick={() => setLogExpanded(!logExpanded)}>
                  {logExpanded ? "▼ Collapse" : "▶ Expand"} ({finalResults.log_data.length} entries)
                </button>
              </div>

              {logExpanded && (
                <div className="log-content">
                  <div className="log-table">
                    <div className="log-header-row">
                      <span>Time</span>
                      <span>Temp</span>
                      <span>Start Tank</span>
                      <span>Balance</span>
                      <span>Pasteurized</span>
                      <span>Status</span>
                    </div>
                    {finalResults.log_data.map((entry, index) => (
                      <div key={index} className="log-row">
                        <span>{entry.time}</span>
                        <span>{entry.temperature}°C</span>
                        <span>{entry.start_tank}L</span>
                        <span>{entry.balance_tank}L</span>
                        <span>{entry.pasteurized_total}L</span>
                        <span className="status-text">{entry.status}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* 🩵 Debug fallback - remove later */}
      <details style={{ marginTop: "1rem", fontSize: "0.85rem", opacity: 0.8 }}>
        <summary>Raw data (debug)</summary>
        <pre>{JSON.stringify(results, null, 2)}</pre>
      </details>
    </div>
  )
}

export default SimulationResults
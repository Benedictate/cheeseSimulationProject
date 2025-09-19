"use client"

import { useState } from "react"

function SimulationResults({ results, isRunning }) {
  const [logExpanded, setLogExpanded] = useState(false)
  const [rawDataExpanded, setRawDataExpanded] = useState(false)

  if (!results) {
    return (
      <div className="card">
        <h2>📊 Simulation Results</h2>
        <div className="no-data">
          {isRunning ? "⏳ Waiting for simulation data..." : "🎯 Start a simulation to see results"}
        </div>
      </div>
    )
  }

  const progress = results.progress || 0
  const finalResults = results.final_results

  return (
    <div className="card">
      <h2>📊 Simulation Results</h2>

      {/* Simulation Metadata */}
      <div className="simulation-metadata">
        <h3>🔧 Simulation Info</h3>
        <div className="metadata-grid">
          <div className="metadata-item">
            <label>Time Mode</label>
            <span className={`time-mode-badge ${results.timeMode === "1" ? "realtime" : "simtime"}`}>
              {results.timeMode === "1" ? "Real-time" : "Simulation-time"}
            </span>
          </div>
          <div className="metadata-item">
            <label>Completed At</label>
            <span>{results.timestamp ? new Date(results.timestamp).toLocaleString() : "N/A"}</span>
          </div>
          <div className="metadata-item">
            <label>Status</label>
            <span className="status-badge completed">✅ Completed</span>
          </div>
        </div>
      </div>

      {/* Real-time Status */}
      {isRunning && (
        <div className="real-time-status">
          <h3>🔄 Real-time Status</h3>
          <div className="status-grid">
            <div className="status-item">
              <label>Current Step</label>
              <span>{results.current_step || 0}</span>
            </div>
            <div className="status-item">
              <label>Temperature</label>
              <span>{results.temperature?.toFixed(1) || 0}°C</span>
            </div>
            <div className="status-item">
              <label>Start Tank</label>
              <span>{results.start_tank?.toFixed(1) || 0}L</span>
            </div>
            <div className="status-item">
              <label>Balance Tank</label>
              <span>{results.balance_tank?.toFixed(1) || 0}L</span>
            </div>
            <div className="status-item">
              <label>Pasteurized</label>
              <span>{results.pasteurized_total?.toFixed(1) || 0}L</span>
            </div>
            <div className="status-item">
              <label>Burnt</label>
              <span>{results.burnt_total?.toFixed(1) || 0}L</span>
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
              <div className="result-value">{finalResults.pasteurized_total?.toFixed(1) || 0}L</div>
              <div className="result-label">Pasteurized</div>
              <div className="result-percentage">{finalResults.efficiency?.toFixed(1) || 0}%</div>
            </div>

            <div className="result-card error">
              <div className="result-value">{finalResults.burnt_total?.toFixed(1) || 0}L</div>
              <div className="result-label">Burnt/Waste</div>
              <div className="result-percentage">{finalResults.waste_percentage?.toFixed(1) || 0}%</div>
            </div>

            <div className="result-card info">
              <div className="result-value">{finalResults.total_milk?.toFixed(1) || 0}L</div>
              <div className="result-label">Total Processed</div>
              <div className="result-percentage">100%</div>
            </div>
          </div>

          {/* Process Log */}
          {finalResults.log_data && (
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

      {/* Raw Output Display */}
      {results.raw_output && (
        <div className="raw-output-section">
          <div className="raw-output-header">
            <h3>📋 Raw Simulation Output</h3>
            <button className="btn btn-secondary" onClick={() => setRawDataExpanded(!rawDataExpanded)}>
              {rawDataExpanded ? "▼ Collapse" : "▶ Expand"} Raw Data
            </button>
          </div>

          {rawDataExpanded && (
            <div className="raw-output-content">
              <pre className="raw-output-text">{results.raw_output}</pre>
            </div>
          )}
        </div>
      )}

      <style jsx>{`
        .simulation-metadata {
          margin-bottom: 2rem;
          padding: 1rem;
          background-color: #f8fafc;
          border-radius: 0.5rem;
          border: 1px solid #e2e8f0;
        }

        .metadata-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 1rem;
        }

        .metadata-item {
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
        }

        .metadata-item label {
          font-size: 0.75rem;
          color: #6b7280;
          font-weight: 500;
        }

        .metadata-item span {
          font-size: 0.875rem;
          font-weight: 600;
          color: #1f2937;
        }

        .time-mode-badge {
          display: inline-flex;
          align-items: center;
          padding: 0.25rem 0.75rem;
          border-radius: 0.375rem;
          font-size: 0.75rem;
          font-weight: 600;
          text-transform: uppercase;
        }

        .time-mode-badge.realtime {
          background-color: #dbeafe;
          color: #1d4ed8;
          border: 1px solid #3b82f6;
        }

        .time-mode-badge.simtime {
          background-color: #dcfce7;
          color: #166534;
          border: 1px solid #22c55e;
        }

        .status-badge {
          display: inline-flex;
          align-items: center;
          padding: 0.25rem 0.75rem;
          border-radius: 0.375rem;
          font-size: 0.75rem;
          font-weight: 600;
        }

        .status-badge.completed {
          background-color: #dcfce7;
          color: #166534;
          border: 1px solid #22c55e;
        }

        .raw-output-section {
          margin-bottom: 2rem;
          border: 1px solid #e2e8f0;
          border-radius: 0.5rem;
          overflow: hidden;
        }

        .raw-output-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem;
          background-color: #f8fafc;
          border-bottom: 1px solid #e2e8f0;
        }

        .raw-output-header h3 {
          margin: 0;
          font-size: 1.125rem;
          font-weight: 600;
          color: #374151;
        }

        .raw-output-content {
          max-height: 400px;
          overflow-y: auto;
          background-color: #1f2937;
        }

        .raw-output-text {
          padding: 1rem;
          margin: 0;
          font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
          font-size: 0.75rem;
          line-height: 1.5;
          color: #f9fafb;
          background-color: transparent;
          white-space: pre-wrap;
          word-wrap: break-word;
        }
      `}</style>
    </div>
  )
}

export default SimulationResults

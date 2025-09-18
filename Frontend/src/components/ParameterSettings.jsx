"use client"

function ParameterSettings({ parameters, onParameterChange, onAnomalyChange, disabled }) {
  const handleInputChange = (key, value, type = "number") => {
    const processedValue = type === "number" ? Number.parseFloat(value) || 0 : value
    onParameterChange(key, processedValue)
  }

  const handleAnomalyToggle = (anomalyKey, field, value) => {
    onAnomalyChange(anomalyKey, field, value)
  }

  return (
    <div className="card">
      <h2>⚙️ Pasteurizer Parameters</h2>

      <div className="parameter-sections">
        {/* Temperature Settings */}
        <div className="parameter-section">
          <h3>🌡️ Temperature Settings (°C)</h3>
          <div className="parameter-grid">
            <div className="parameter-item">
              <label>Minimum Operating Temperature</label>
              <input
                type="number"
                value={parameters.tempMinOperating}
                onChange={(e) => handleInputChange("tempMinOperating", e.target.value)}
                disabled={disabled}
                min="60"
                max="80"
              />
              <span className="unit">°C</span>
            </div>

            <div className="parameter-item">
              <label>Optimal Temperature (Min)</label>
              <input
                type="number"
                value={parameters.tempOptimalMin}
                onChange={(e) => handleInputChange("tempOptimalMin", e.target.value)}
                disabled={disabled}
                min="65"
                max="75"
              />
              <span className="unit">°C</span>
            </div>

            <div className="parameter-item">
              <label>Optimal Temperature</label>
              <input
                type="number"
                value={parameters.tempOptimal}
                onChange={(e) => handleInputChange("tempOptimal", e.target.value)}
                disabled={disabled}
                min="70"
                max="80"
              />
              <span className="unit">°C</span>
            </div>

            <div className="parameter-item">
              <label>Optimal Temperature (Max)</label>
              <input
                type="number"
                value={parameters.tempOptimalMax}
                onChange={(e) => handleInputChange("tempOptimalMax", e.target.value)}
                disabled={disabled}
                min="70"
                max="80"
              />
              <span className="unit">°C</span>
            </div>

            <div className="parameter-item">
              <label>Burn Threshold</label>
              <input
                type="number"
                value={parameters.tempBurnThreshold}
                onChange={(e) => handleInputChange("tempBurnThreshold", e.target.value)}
                disabled={disabled}
                min="75"
                max="85"
              />
              <span className="unit">°C</span>
            </div>
          </div>
        </div>

        {/* Process Settings */}
        <div className="parameter-section">
          <h3>⚡ Process Settings</h3>
          <div className="parameter-grid">
            <div className="parameter-item">
              <label>Total Milk Volume</label>
              <input
                type="number"
                value={parameters.totalMilk}
                onChange={(e) => handleInputChange("totalMilk", e.target.value)}
                disabled={disabled}
                min="100"
                max="5000"
              />
              <span className="unit">L</span>
            </div>

            <div className="parameter-item">
              <label>Flow Rate</label>
              <input
                type="number"
                step="0.1"
                value={parameters.flowRate}
                onChange={(e) => handleInputChange("flowRate", e.target.value)}
                disabled={disabled}
                min="10"
                max="100"
              />
              <span className="unit">L/step</span>
            </div>

            <div className="parameter-item">
              <label>Step Duration</label>
              <input
                type="number"
                value={parameters.stepDurationSec}
                onChange={(e) => handleInputChange("stepDurationSec", e.target.value)}
                disabled={disabled}
                min="5"
                max="60"
              />
              <span className="unit">seconds</span>
            </div>

            <div className="parameter-item">
              <label>Startup Duration</label>
              <input
                type="number"
                value={parameters.startupDuration}
                onChange={(e) => handleInputChange("startupDuration", e.target.value)}
                disabled={disabled}
                min="5"
                max="50"
              />
              <span className="unit">steps</span>
            </div>

            <div className="parameter-item">
              <label>Temperature Drop Rate</label>
              <input
                type="number"
                step="0.1"
                value={parameters.tempDropPerStep}
                onChange={(e) => handleInputChange("tempDropPerStep", e.target.value)}
                disabled={disabled}
                min="0.1"
                max="5"
              />
              <span className="unit">°C/step</span>
            </div>

            <div className="parameter-item">
              <label>Temperature Rise Rate</label>
              <input
                type="number"
                step="0.1"
                value={parameters.tempRiseWhenCold}
                onChange={(e) => handleInputChange("tempRiseWhenCold", e.target.value)}
                disabled={disabled}
                min="0.1"
                max="5"
              />
              <span className="unit">°C/step</span>
            </div>
          </div>
        </div>

        {/* Anomaly Settings */}
        <div className="parameter-section">
          <h3>⚠️ Anomaly Configuration</h3>
          <div className="anomaly-grid">
            {Object.entries(parameters.anomalies).map(([anomalyKey, anomaly]) => (
              <div key={anomalyKey} className="anomaly-item">
                <h4>{anomalyKey.replace(/([A-Z])/g, " $1").replace(/^./, (str) => str.toUpperCase())}</h4>

                <div className="anomaly-controls">
                  <div className="checkbox-control">
                    <input
                      type="checkbox"
                      id={`${anomalyKey}-enabled`}
                      checked={anomaly.enabled}
                      onChange={(e) => handleAnomalyToggle(anomalyKey, "enabled", e.target.checked)}
                      disabled={disabled}
                    />
                    <label htmlFor={`${anomalyKey}-enabled`}>Force Enable</label>
                  </div>

                  <div className="probability-control">
                    <label>Probability: {Math.round(anomaly.probability * 100)}%</label>
                    <input
                      type="range"
                      min="0"
                      max="1"
                      step="0.01"
                      value={anomaly.probability}
                      onChange={(e) =>
                        handleAnomalyToggle(anomalyKey, "probability", Number.parseFloat(e.target.value))
                      }
                      disabled={disabled || anomaly.enabled}
                    />
                  </div>
                </div>

                <div className="anomaly-status">
                  {anomaly.enabled ? (
                    <span className="badge badge-error">Forced</span>
                  ) : anomaly.probability > 0 ? (
                    <span className="badge badge-warning">Random ({Math.round(anomaly.probability * 100)}%)</span>
                  ) : (
                    <span className="badge badge-secondary">Disabled</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Timescale */}
        <div className="parameter-section">
          <h3>🔘 Time Scale</h3>
          <div className="parameter-item">
            <label>Binary Flag</label>
            <button
              type="button"
              onClick={() => handleInputChange("binaryFlag", parameters.binaryFlag === 1 ? 0 : 1)}
              disabled={disabled}
            >
              {parameters.timeScale === 1 ? "REALTIME (1)" : "SIMTIME (0)"}
            </button>
          </div>
        </div>

      </div>
    </div>
  )
}

export default ParameterSettings

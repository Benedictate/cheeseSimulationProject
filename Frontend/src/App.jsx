"use client";

import { useState, useEffect } from "react";
import PasteurizerControls from "./components/PasteurizerControls";
import ParameterSettings from "./components/ParameterSettings";
import SimulationResults from "./components/SimulationResults";
import "./App.css";

function App() {
  const [simulationRunning, setSimulationRunning] = useState(false);
  const [simulationResults, setSimulationResults] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState("checking");
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const backendUrl =
    process.env.REACT_APP_BACKEND_URL || "http://localhost:3001";

  // Default pasteurizer parameters based on your Python file
  const [parameters, setParameters] = useState({
    // Temperature settings (°C)
    tempMinOperating: 68,
    tempOptimalMin: 70,
    tempOptimal: 72,
    tempOptimalMax: 74,
    tempBurnThreshold: 77,

    // Timing settings
    stepDurationSec: 15,
    startupDuration: 20,
    cooldownDuration: 8,

    // Flow and processing
    flowRate: 41.7,
    totalMilk: 1000,
    tempDropPerStep: 1,
    tempRiseWhenCold: 1.5,

    // Anomaly settings
    anomalies: {
      tempVariation: { enabled: false, probability: 0.1 },
      equipmentFailure: { enabled: false, probability: 0.05 },
      flowRateIssue: { enabled: false, probability: 0.08 },
    },

    timeScale: 0,
  });

  // Check backend connection
  const checkConnection = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/health`);
      if (response.ok) {
        setConnectionStatus("connected");
        setError(null);
      } else {
        setConnectionStatus("error");
      }
    } catch (err) {
      setConnectionStatus("disconnected");
      setError("Cannot connect to backend server");
    }
  };

  // Poll simulation status
  const pollSimulationStatus = async () => {
    if (!simulationRunning) return;

    try {
      const response = await fetch(`${backendUrl}/api/simulation-status`);
      if (response.ok) {
        const data = await response.json();
        setSimulationRunning(data.running);
        setSimulationResults(data.results);

        if (data.results?.completed) {
          setSimulationRunning(false);
        }
      }
    } catch (err) {
      console.error("Error polling simulation status:", err);
    }
  };

  useEffect(() => {
    checkConnection();
    const connectionInterval = setInterval(checkConnection, 10000); // Check every 10 seconds

    return () => clearInterval(connectionInterval);
  }, []);

  useEffect(() => {
    let statusInterval;
    if (simulationRunning) {
      statusInterval = setInterval(pollSimulationStatus, 2000); // Poll every 2 seconds
    }

    return () => {
      if (statusInterval) clearInterval(statusInterval);
    };
  }, [simulationRunning]);

  const startSimulation = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${backendUrl}/api/start-simulation`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(parameters),
      });

      const data = await response.json();

      if (data.success) {
        setSimulationRunning(true);
        setSimulationResults(null);
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError(`Failed to start simulation: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const stopSimulation = async () => {
    setIsLoading(true);

    try {
      const response = await fetch(`${backendUrl}/api/stop-simulation`, {
        method: "POST",
      });

      if (response.ok) {
        setSimulationRunning(false);
      }
    } catch (err) {
      setError(`Failed to stop simulation: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleParameterChange = (key, value) => {
    setParameters((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const handleAnomalyChange = (anomalyKey, field, value) => {
    setParameters((prev) => ({
      ...prev,
      anomalies: {
        ...prev.anomalies,
        [anomalyKey]: {
          ...prev.anomalies[anomalyKey],
          [field]: value,
        },
      },
    }));
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🧀 Manufacturing Simulation Control</h1>
        <p>Real-time control and monitoring of the Manufacturing process</p>

        <div className="connection-status">
          <div className={`status-indicator ${connectionStatus}`}>
            <div className="status-dot"></div>
            <span>
              {connectionStatus === "connected"
                ? "🟢 Backend Connected"
                : connectionStatus === "disconnected"
                ? "🔴 Backend Disconnected"
                : connectionStatus === "error"
                ? "🟡 Backend Error"
                : "⏳ Checking..."}
            </span>
          </div>
        </div>
      </header>

      <main className="app-main">
        {error && <div className="error-banner">❌ {error}</div>}

        <PasteurizerControls
          simulationRunning={simulationRunning}
          onStart={startSimulation}
          onStop={stopSimulation}
          isLoading={isLoading}
          connectionStatus={connectionStatus}
        />

        <ParameterSettings
          parameters={parameters}
          onParameterChange={handleParameterChange}
          onAnomalyChange={handleAnomalyChange}
          disabled={simulationRunning}
        />

        <SimulationResults
          results={simulationResults}
          isRunning={simulationRunning}
        />
      </main>
    </div>
  );
}

export default App;

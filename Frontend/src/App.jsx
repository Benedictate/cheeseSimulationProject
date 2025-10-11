"use client";

import { useState, useEffect } from "react";
import mqtt from "mqtt";
import useMqttResults from "./components/useMqttResults";
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

  useMqttResults(setSimulationResults);

  // Default parameters
  const [parameters, setParameters] = useState({
    global: {
      time_mode: 0,
      simulation_time: 6000,
    },
    machines: {
      pasteuriser: {
        temp_optimal: 72,
        flow_rate: 41.7,
      },
      cheese_vat: {
        vat_batch_size: 10000,
        anomaly_probability: 10,
        optimal_ph: 6.55,
        milk_flow_rate: 5,
      },
      curd_cutter: {
        blade_wear_rate: 0.1,
        auger_speed: 50,
      },
      whey_drainer: {
        target_mass: 1000,
        target_moisture: 58.0,
      },
      cheddaring: {},
      salting_machine: {
        mellowing_time: 10,
        salt_recipe: 0.033,
        flow_rate: 50.0,
      },
      cheese_presser: {
        block_weight: 27,
        mold_count: 5,
        anomaly_chance: 0.1,
      },
      ripener: {
        initial_temp: 10,
      },
    },
  });

  
   // --- Health check ---
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

  // --- Poll simulation status ---
  const pollSimulationStatus = async () => {
    if (!simulationRunning) return;

    try {
      const response = await fetch(`${backendUrl}/api/simulation-status`);
      if (response.ok) {
        const data = await response.json();
        setSimulationRunning(data.running);

        if (data.results?.completed) {
          setSimulationRunning(false);
        }
      }
    } catch (err) {
      console.error("Error polling simulation status:", err);
    }
  }; 

  
  useEffect(() => {
    console.log("Connecting to MQTT...");
    const client = mqtt.connect("ws://localhost:9001");

    client.on("connect", () => console.log("✅ MQTT connected"));
    client.on("error", (err) => console.error("❌ MQTT error:", err));

    return () => client.end();
  }, []);

  useEffect(() => {
    checkConnection();
    const connectionInterval = setInterval(checkConnection, 10000);
    return () => clearInterval(connectionInterval);
  }, []);

  useEffect(() => {
    let statusInterval;
    if (simulationRunning) {
      statusInterval = setInterval(pollSimulationStatus, 2000);
    }
    return () => {
      if (statusInterval) clearInterval(statusInterval);
    };
  }, [simulationRunning]);

  // --- Start simulation ---
  const startSimulation = async () => {
    setIsLoading(true);
    setError(null);
    setSimulationResults(null);
    setSimulationRunning(true);

    try {
      const response = await fetch(`${backendUrl}/api/start-simulation`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(parameters),
      });

      if (!response.ok)
        throw new Error(`Backend error: ${response.statusText}`);

      if (!response.body) throw new Error("ReadableStream not supported");

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        const lines = buffer.split("\n");
        buffer = lines.pop();
        for (const line of lines) {
          try {
            const parsed = JSON.parse(line);
            setSimulationResults((prev) => [...(prev || []), parsed]);
          } catch {
            console.warn("Skipping non-JSON line:", line);
          }
        }
      }

      if (buffer.trim()) {
        try {
          const parsed = JSON.parse(buffer.trim());
          setSimulationResults((prev) => [...(prev || []), parsed]);
        } catch {
          console.warn("Skipping final non-JSON:", buffer);
        }
      }
    } catch (err) {
      setError(`Failed to start simulation: ${err.message}`);
      setSimulationRunning(false);
    } finally {
      setIsLoading(false);
    }
  };

  // --- Stop simulation ---
  const stopSimulation = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${backendUrl}/api/stop-simulation`, {
        method: "POST",
      });
      if (response.ok) setSimulationRunning(false);
    } catch (err) {
      setError(`Failed to stop simulation: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  // --- Parameter handlers ---
  const handleParameterChange = (key, value) => {
    setParameters((prev) => ({ ...prev, [key]: value }));
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
        <p>Real-time control and monitoring of the manufacturing process</p>

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
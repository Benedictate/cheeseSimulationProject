const express = require("express")
const axios = require("axios")
const cors = require("cors")
const mqtt = require("mqtt")
const { Server } = require("socket.io")

const app = express()
app.use(express.json())
app.use(cors())

const io = new Server({ cors: { origin: "*" } })

// MQTT Configuration (commented out for now since you don't have Azure setup)
// const mqttClient = mqtt.connect("mqtt://<your-azure-iothub-endpoint>");
// mqttClient.on("connect", () => {
//     console.log("Connected to Azure MQTT");
// });

// API Endpoint for React Frontend to trigger simulation
app.post("/run-simulation", async (req, res) => {
  try {
    console.log("Received request from frontend:", req.body)

    // For now, let's mock the simulation response instead of calling the actual simulator
    // Comment out the axios call until your Python simulator is ready
    /*
        const response = await axios.post("http://127.0.0.1:8000/simulate", req.body);
        const statusUpdate = response.data.status;
        const fullResult = response.data.full;
        */

    // Mock response for testing
    const mockStatusUpdate = "Simulation completed successfully - Mock Response"
    const mockFullResult = {
      simulationId: `sim_${Date.now()}`,
      status: "completed",
      results: {
        totalEvents: 1500,
        successRate: 95.2,
        duration: 30,
      },
      timestamp: new Date().toISOString(),
    }

    // **1️⃣ Send full output to Azure MQTT (commented out for now)**
    // mqttClient.publish("simulation/results", JSON.stringify(mockFullResult));

    // **2️⃣ Send partial output to frontend via WebSocket**
    io.emit("status-update", mockStatusUpdate)

    // Send response back to frontend
    res.json({
      message: "Simulation started successfully! Backend is connected.",
      statusUpdate: mockStatusUpdate,
      data: mockFullResult,
    })
  } catch (error) {
    console.error("Error in /run-simulation:", error.message)
    res.status(500).json({
      error: error.message,
      message: "Backend connected but simulation service unavailable",
    })
  }
})

// Health check endpoint
app.get("/health", (req, res) => {
  res.json({ status: "Backend is running", timestamp: new Date().toISOString() })
})

// WebSocket Server
io.listen(3002)

app.listen(3001, () => {
  console.log("Node.js backend running on port 3001")
  console.log("WebSocket server running on port 3002")
  console.log("Ready to receive requests from frontend!")
})

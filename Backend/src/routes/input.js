javascript
const express = require("express");
const axios = require("axios");
const cors = require("cors");
const mqtt = require("mqtt");
const { Server } = require("socket.io");

const app = express();
app.use(express.json());
app.use(cors());

const io = new Server({ cors: { origin: "*" } });

// MQTT Configuration
const mqttClient = mqtt.connect("mqtt://<your-azure-iothub-endpoint>"); // put MQTT address in this line

mqttClient.on("connect", () => {
    console.log("Connected to Azure MQTT");
});

// API Endpoint for React Frontend to trigger simulation
app.post("/run-simulation", async (req, res) => {
    try {
        const response = await axios.post("http://127.0.0.1:8000/simulate", req.body);
        const statusUpdate = response.data.status;
        const fullResult = response.data.full;

        // **1️⃣ Send full output to Azure MQTT**
        mqttClient.publish("simulation/results", JSON.stringify(fullResult));

        // **2️⃣ Send partial output to frontend via WebSocket**
        io.emit("status-update", statusUpdate);

        res.json({ message: "Simulation started", statusUpdate });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// WebSocket Server
io.listen(3002);

app.listen(3001, () => console.log("Node.js backend running on port 3001"));

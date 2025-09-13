const express = require("express");
const routes = require("./routes");
const { startMqttClient } = require("./mqtt");

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(express.json());

// Routes
app.use("/api", routes);

// Start MQTT client
startMqttClient();

// Start HTTP server
app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`);
});
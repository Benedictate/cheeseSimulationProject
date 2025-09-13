const express = require("express");
const cors = require("cors");  
const routes = require("./routes");
const { startMqttClient } = require("./mqtt");

const app = express();
const PORT = process.env.PORT || 3001;

// --- CORS Setup ---
const allowedOrigins = process.env.CORS_ALLOWED_ORIGINS
  ? process.env.CORS_ALLOWED_ORIGINS.split(",")
  : []; // split by comma if multiple origins

app.use(cors({
  origin: allowedOrigins,
  credentials: true, // allow cookies/auth headers if needed
}));

// Middleware
app.use(express.json());

// Routes
app.use("/api", routes);

// Start MQTT client
startMqttClient();

// Start HTTP server
app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`);
  console.log(`🌐 Allowed origins: ${allowedOrigins.join(", ") || "none"}`);
});
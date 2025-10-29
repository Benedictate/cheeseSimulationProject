const express = require("express");
const cors = require("cors");  
const routes = require("./routes");
const { startMqttClient } = require("./mqtt");

const app = express();
const PORT = process.env.PORT || 3001;

// --- CORS Setup ---
const allowedOrigins = process.env.CORS_ALLOWED_ORIGINS
  ? process.env.CORS_ALLOWED_ORIGINS.split(",")
  : ["http://localhost:3000", "http://localhost:5001"]; // sensible defaults for local dev/docker

app.use(cors({
  origin: function (origin, callback) {
    // allow requests with no origin (like mobile apps, curl)
    if (!origin) return callback(null, true)
    if (allowedOrigins.indexOf(origin) !== -1) {
      return callback(null, true)
    }
    return callback(null, true) // fallback: allow all in dev
  },
  credentials: true,
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
//  console.log(`🌐 Allowed origins: ${allowedOrigins.join(", ") || "none"}`);
});
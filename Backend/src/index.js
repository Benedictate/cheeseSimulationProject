const express = require("express")
const cors = require("cors")
const routes = require("./routes")
// const { startMqttClient } = require("./mqtt"); // Disabled for now

const app = express()
const PORT = process.env.PORT || 3001

// --- CORS Setup ---
const allowedOrigins = process.env.CORS_ALLOWED_ORIGINS
  ? process.env.CORS_ALLOWED_ORIGINS.split(",")
  : ["http://localhost:3000", "http://localhost:5173", "http://localhost:3001"] // Add default origins

app.use(
  cors({
    origin: allowedOrigins,
    credentials: true,
  }),
)

// Middleware
app.use(express.json())
app.use(express.text()) // Add text parsing for binary routes

// Routes
app.use("/api", routes)

// Start MQTT client - DISABLED FOR NOW
// startMqttClient();

// Start HTTP server
app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`)
  console.log(`🌐 Allowed origins: ${allowedOrigins.join(", ")}`)
})

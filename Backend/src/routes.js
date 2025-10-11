const express = require("express")
const { spawn } = require("child_process")
const path = require("path")
const router = express.Router()

// Health check route
router.get("/health", (req, res) => {
  res.removeHeader("ETag")
  res.set("Cache-Control", "no-store, no-cache, must-revalidate, proxy-revalidate")
  res.set("Pragma", "no-cache")
  res.set("Expires", "0")

  res.status(200).json({ status: "ok" })
})

/**
 * Route: Start simulation with full machine settings JSON
 * Receives config from frontend form and passes it directly to Main.py via stdin
 */
router.post("/start-simulation", async (req, res) => {
  try {
    const config = req.body
    console.log("Starting simulation with config from frontend form")
    console.log("Full config object received from frontend:")
    console.log(JSON.stringify(config, null, 2)) // pretty print

    const py = spawn("python3", ["-u", "Main.py"], {
      cwd: path.join(__dirname, ".."), // Run from backend directory where Main.py is located
    })

    let errorOutput = ""

    py.stdout.on("data", (data) => {
      process.stdout.write(data.toString())
    })

    py.stderr.on("data", (data) => {
      errorOutput += data.toString()
      console.error("Python error:", data.toString())
    })

    py.on("close", (code) => {
      console.log(`Python process exited with code ${code}`)
    })

    // Send config to Python via stdin
    if (config && Object.keys(config).length > 0) {
      py.stdin.write(JSON.stringify(config))
    }
    py.stdin.end()

    // Don't wait for completion since simulations can be long-running
    res.json({
      success: true,
      message: "Simulation started successfully with form parameters",
      pid: py.pid,
    })
  } catch (err) {
    console.error("Simulation error:", err)
    res.status(500).json({ success: false, error: err.message })
  }
})

module.exports = router

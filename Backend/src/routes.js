const express = require("express")
const { spawn } = require("child_process")
const path = require("path")
const router = express.Router()

let currentSimulationProcess = null
let machineDataQueue = []
let queueInterval = null

/**
 * Utility function to call Python sim and return a promise
 */
function runPythonSim(inputData) {
  return new Promise((resolve, reject) => {
    // Fix the path to Main.py - it's in the backend directory
    const pythonScriptPath = path.join(__dirname, "..", "Main.py")
    console.log(`🐍 Running Python script at: ${pythonScriptPath}`)

    const py = spawn("python3", [pythonScriptPath, inputData])

    let output = ""
    let errorOutput = ""

    py.stdout.on("data", (data) => {
      output += data.toString()
    })

    py.stderr.on("data", (data) => {
      errorOutput += data.toString()
    })

    py.on("close", (code) => {
      if (code !== 0) {
        reject(new Error(`Python process exited with code ${code}: ${errorOutput}`))
      } else {
        resolve(output.trim())
      }
    })

    // Don't send to stdin, use command line argument instead
    py.stdin.end()
  })
}

function startQueueProcessor(onData) {
  console.log("🕐 Starting queue processor - releasing data every 2 minutes")

  queueInterval = setInterval(() => {
    if (machineDataQueue.length > 0) {
      const dataToSend = machineDataQueue.shift()
      console.log(`📤 Releasing queued data: ${dataToSend.machine_name}`)
      onData(JSON.stringify(dataToSend))
    }
  }, 120000) // 2 minutes = 120,000 milliseconds
}

function stopQueueProcessor() {
  if (queueInterval) {
    clearInterval(queueInterval)
    queueInterval = null
    machineDataQueue = []
    console.log("🛑 Queue processor stopped and cleared")
  }
}

function runPythonSimStreaming(inputData, onData, onComplete, onError) {
  const pythonScriptPath = path.join(__dirname, "..", "Main.py")
  console.log(`🐍 Running Python script with streaming at: ${pythonScriptPath}`)

  const py = spawn("python3", [pythonScriptPath, inputData])
  currentSimulationProcess = py

  let output = ""
  let errorOutput = ""
  let wasStopped = false // Track if simulation was manually stopped

  if (inputData === "1") {
    startQueueProcessor(onData)
  }

  py.stdout.on("data", (data) => {
    const chunk = data.toString()
    output += chunk
    const lines = chunk.split("\n").filter((line) => line.trim())
    lines.forEach((line) => {
      try {
        // Try to parse as JSON first
        const jsonData = JSON.parse(line)

        if (inputData === "1" && jsonData.type === "machine_output") {
          console.log(`📥 Queuing machine data: ${jsonData.machine_name}`)
          machineDataQueue.push(jsonData)
        } else {
          // For simulation mode or non-machine data, send immediately
          onData(JSON.stringify(jsonData))
        }
      } catch (e) {
        // If not JSON, send as plain text for debugging
        if (line.includes("Progress:") || line.includes("Simulation") || line.includes("🧀") || line.includes("⏱️")) {
          onData(line)
        }
      }
    })
  })

  py.stderr.on("data", (data) => {
    errorOutput += data.toString()
    console.error("Python stderr:", data.toString())
  })

  py.on("close", (code) => {
    currentSimulationProcess = null
    console.log(`Python process closed with code: ${code}`)

    stopQueueProcessor()

    if (wasStopped) {
      // Process was manually stopped
      onComplete(JSON.stringify({ status: "stopped", message: "Simulation stopped by user" }))
    } else if (code !== 0 && code !== null) {
      // Process exited with error
      onError(new Error(`Python process exited with code ${code}: ${errorOutput}`))
    } else {
      // Process completed normally
      onComplete(output.trim())
    }
  })

  py.on("error", (error) => {
    console.error("Python process error:", error)
    currentSimulationProcess = null
    stopQueueProcessor()
    onError(error)
  })

  py.wasStopped = () => wasStopped
  py.markAsStopped = () => {
    wasStopped = true
  }

  py.stdin.end()
  return py
}

// Route 0: Health check route
router.get("/health", (req, res) => {
  res.removeHeader("ETag")
  res.set("Cache-Control", "no-store, no-cache, must-revalidate, proxy-revalidate")
  res.set("Pragma", "no-cache")
  res.set("Expires", "0")

  res.status(200).json({ status: "ok" })
})

/**
 * Route 1: Quick Sim - Single binary time-scale value
 * Example: POST body = "1" (raw text)
 */
router.post("/quick", express.text(), async (req, res) => {
  try {
    const rawInput = req.body.trim()

    // Validate input (must be 0 or 1)
    if (!["0", "1"].includes(rawInput)) {
      return res.status(400).json({ error: "Input must be '0' or '1'" })
    }

    console.log(`🚀 Starting quick simulation with timeMode: ${rawInput}`)

    if (rawInput === "1") {
      // Real-time mode - use streaming with queue
      res.writeHead(200, {
        "Content-Type": "text/plain",
        "Transfer-Encoding": "chunked",
        "Cache-Control": "no-cache",
        Connection: "keep-alive",
      })

      res.write(
        `data: ${JSON.stringify({ type: "info", message: "Real-time mode: Machine data will be released every 2 minutes" })}\n\n`,
      )

      runPythonSimStreaming(
        rawInput,
        (data) => {
          // Send each line of data as it comes (now queued for machine data)
          res.write(`data: ${JSON.stringify({ type: "progress", data: data })}\n\n`)
        },
        (finalResult) => {
          // Send completion signal
          res.write(`data: ${JSON.stringify({ type: "complete", result: finalResult })}\n\n`)
          res.end()
        },
        (error) => {
          res.write(`data: ${JSON.stringify({ type: "error", error: error.message })}\n\n`)
          res.end()
        },
      )
    } else {
      // Simulation time mode - use regular approach
      const result = await runPythonSim(rawInput)
      res.json({ success: true, result })
    }
  } catch (err) {
    console.error("Quick sim error:", err)
    res.status(500).json({ success: false, error: err.message })
  }
})

/**
 * Route 2: Single binary value (legacy)
 */
router.post("/binary", express.text(), async (req, res) => {
  try {
    const rawInput = req.body.trim()

    if (!["0", "1"].includes(rawInput)) {
      return res.status(400).json({ error: "Input must be '0' or '1'" })
    }

    const result = await runPythonSim(rawInput)
    res.json({ success: true, result })
  } catch (err) {
    res.status(500).json({ success: false, error: err.message })
  }
})

/**
 * Route 3: Full machine settings JSON
 */
router.post("/settings", async (req, res) => {
  try {
    const settings = req.body

    if (!settings || typeof settings !== "object") {
      return res.status(400).json({ error: "Invalid settings object" })
    }

    const result = await runPythonSim(settings)
    res.json({ success: true, result })
  } catch (err) {
    console.error(err)
    res.status(500).json({ success: false, error: err.message })
  }
})

router.post("/stop-simulation", (req, res) => {
  try {
    if (currentSimulationProcess) {
      console.log("🛑 Stopping simulation process...")
      if (currentSimulationProcess.markAsStopped) {
        currentSimulationProcess.markAsStopped()
      }
      currentSimulationProcess.kill("SIGKILL")
      currentSimulationProcess = null
      stopQueueProcessor()
      res.json({ success: true, message: "Simulation stopped" })
    } else {
      res.json({ success: false, message: "No simulation running" })
    }
  } catch (err) {
    console.error("Error stopping simulation:", err)
    res.status(500).json({ success: false, error: err.message })
  }
})

router.get("/simulation-status", (req, res) => {
  res.json({
    running: currentSimulationProcess !== null,
    pid: currentSimulationProcess ? currentSimulationProcess.pid : null,
  })
})

module.exports = router

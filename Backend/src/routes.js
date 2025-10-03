const express = require("express");
const { spawn } = require("child_process");
const router = express.Router();

/**
 * Utility function to call Python sim and return a promise
 */
function runPythonSim(inputData) {
  return new Promise((resolve, reject) => {
    const py = spawn("python3", ["Main.py"]); // Adjust path if main.py is elsewhere

    let output = "";
    let errorOutput = "";

    py.stdout.on("data", (data) => {
      output += data.toString();
    });

    py.stderr.on("data", (data) => {
      errorOutput += data.toString();
    });

    py.on("close", (code) => {
      if (code !== 0) {
        reject(
          new Error(`Python process exited with code ${code}: ${errorOutput}`)
        );
      } else {
        resolve(output.trim());
      }
    });

    // Send JSON to Python stdin
    py.stdin.write(JSON.stringify(inputData));
    py.stdin.end();
  });
}

// Route 0: Health check route
router.get("/health", (req, res) => {
  res.removeHeader("ETag"); // make sure no ETag is set
  res.set(
    "Cache-Control",
    "no-store, no-cache, must-revalidate, proxy-revalidate"
  );
  res.set("Pragma", "no-cache");
  res.set("Expires", "0");

  res.status(200).json({ status: "ok" });
});

/**
 * Route 1: Single binary value
 * Example: POST body = "1"
 */
router.post("/quick", express.text(), async (req, res) => {
  try {
    const rawInput = req.body;

    // Validate input (must be 0 or 1)
    if (!["0", "1"].includes(rawInput)) {
      return res.status(400).json({ error: "Input must be '0' or '1'" });
    }

    const result = await runPythonSim(rawInput);
    res.json({ success: true, result });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

/**
 * Route 2: full machine settings JSON
 */
router.post("/start-simulation", (req, res) => {
  try {
    if (currentProcess) {
      return res.status(400).json({ error: "Simulation already running" });
    }

    const settings = req.body;
    currentProcess = spawn("python3", ["Main.py"]);

    // pass JSON into stdin
    currentProcess.stdin.write(JSON.stringify(settings));
    currentProcess.stdin.end();

    // handle logs
    currentProcess.stdout.on("data", (data) => {
      console.log("Python:", data.toString());
    });

    currentProcess.stderr.on("data", (data) => {
      console.error("Python error:", data.toString());
    });

    currentProcess.on("close", (code) => {
      console.log("Simulation ended with code", code);
      currentProcess = null;
    });

    res.json({ success: true, message: "Simulation started" });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

/**
 * Route 3: End Python process
 */
router.post("/stop-simulation", (req, res) => {
  try {
    if (!currentProcess) {
      return res.status(400).json({ error: "No simulation is running" });
    }

    currentProcess.kill("SIGINT"); // or "SIGTERM" depending on Python cleanup
    currentProcess = null;

    res.json({ success: true, message: "Simulation stopped" });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

module.exports = router;

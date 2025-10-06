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
router.post("/start-simulation", async (req, res) => {
  if (running) {
    return res.status(400).json({ success: false, message: "Simulation already running" });
  }

  const settings = req.body;

  try {
    simProcess = spawn("python3", ["Main.py"]);

    running = true;
    latestResults = { running: true, progress: [] };

    simProcess.stdout.on("data", (data) => {
      try {
        // Assume Python prints JSON per line
        const parsed = JSON.parse(data.toString().trim());
        latestResults.progress.push(parsed);
      } catch (err) {
        console.error("Failed to parse Python output:", data.toString());
      }
    });

    simProcess.stderr.on("data", (data) => {
      console.error("Python error:", data.toString());
    });

    simProcess.on("close", (code) => {
      running = false;
      if (!latestResults) latestResults = {};
      latestResults.completed = true;
      latestResults.exitCode = code;
    });

    // Send settings to Python stdin
    simProcess.stdin.write(JSON.stringify(settings));
    simProcess.stdin.end();

    res.json({ success: true, message: "Simulation started" });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

/**
 * Route 3: End Python process
 */
router.post("/stop-simulation", (req, res) => {
  if (simProcess) {
    simProcess.kill("SIGINT");
    running = false;
    latestResults = { stopped: true };
    simProcess = null;
    return res.json({ success: true, message: "Simulation stopped" });
  }
  res.status(400).json({ success: false, message: "No simulation running" });
});

/**
 * Route 4: Poll simulation status
 */
router.get("/simulation-status", (req, res) => {
  res.json({
    running,
    results: latestResults,
  });
});

module.exports = router;

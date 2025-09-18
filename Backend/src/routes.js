const express = require("express");
const { spawn } = require("child_process");
const router = express.Router();

/**
 * Utility function to call Python sim and return a promise
 */
function runPythonSim(inputData) {
  return new Promise((resolve, reject) => {
    const py = spawn("python3", ["../Main.py"]); // Adjust path if main.py is elsewhere

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
        reject(new Error(`Python process exited with code ${code}: ${errorOutput}`));
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
  res.set("Cache-Control", "no-store, no-cache, must-revalidate, proxy-revalidate");
  res.set("Pragma", "no-cache");
  res.set("Expires", "0");

  res.status(200).json({ status: "ok" });
});

/**
 * Route 1: Single binary value
 * Example: POST body = "1"
 */
router.post("/binary", express.text(), async (req, res) => {
  try {
    const rawInput = req.body.trim();

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
router.post("/settings", async (req, res) => {
  try {
    const settings = req.body;

    if (!settings || typeof settings !== "object") {
      return res.status(400).json({ error: "Invalid settings object" });
    }

    const result = await runPythonSim(settings);
    res.json({ success: true, result });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, error: err.message });
  }
});

module.exports = router;
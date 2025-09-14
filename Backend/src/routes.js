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

/**
 * Route 1: single binary spec (example: { "spec": 1 })
 */
router.post("/binary", async (req, res) => {
  try {
    const { spec } = req.body;
    if (typeof spec === "undefined") {
      return res.status(400).json({ error: "Missing 'spec' value" });
    }

    const result = await runPythonSim({ spec });
    res.json({ success: true, result });
  } catch (err) {
    console.error(err);
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
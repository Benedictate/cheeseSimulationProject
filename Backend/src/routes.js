const express = require("express");
const { spawn } = require("child_process");
const { startSim, stopSim, getSimState } = require("./pythonHandler");
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
 * Route 1: Single binary value  ---BROKEN---
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
  try {
    const result = await startSim(req.body);
    res.json({ success: true, ...result });
  } catch (err) {
    res.status(400).json({ success: false, error: err.message });
  }
});

/**
 * Route 3: End Python process
 */
router.post("/stop-simulation", async (req, res) => {
  try {
    const result = await stopSim();
    res.json({ success: true, ...result });
  } catch (err) {
    res.status(400).json({ success: false, error: err.message });
  }
});

/**
 * Route 4: Poll simulation status
 */
router.get("/simulation-status", (req, res) => {
  res.json({
    running: getSimState().isRunning,
  });
});

const fs = require("fs");
const path = require("path");

router.get("/results", (req, res) => {
  try {
    const filePath = path.resolve(
      "/app/Backend/data/salting_and_mellowing_data.json"
    );

    if (!fs.existsSync(filePath)) {
      return res
        .status(404)
        .json({ success: false, message: "Results file not found" });
    }

    let data = fs.readFileSync(filePath, "utf8").trim();

    // ✅ Ensure valid JSON: wrap raw comma-separated data in brackets
    if (!data.startsWith("[")) {
      data = `[${data}`;
    }
    if (!data.endsWith("]")) {
      data = `${data}]`;
    }

    const parsed = JSON.parse(data);
    res.json({ success: true, data: parsed });
  } catch (err) {
    console.error("❌ Error reading results:", err);
    res.status(500).json({ success: false, error: err.message });
  }
});
module.exports = router;

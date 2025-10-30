// pythonHandler.js
const { spawn } = require("child_process");
const path = require("path");
const fs = require("fs");

let simProcess = null;
let isRunning = false;

function startSim(inputData) {
  return new Promise((resolve, reject) => {
    if (isRunning) return reject(new Error("Simulation already running"));
    console.log("🐍 Starting Python simulation with input:", inputData) ;
    console.log("🚀 Starting Python simulation...");
    // Use Main.py and unbuffered stdout; run in backend cwd
    simProcess = spawn("python3", ["-u", "Main.py"], { cwd: __dirname + "/.." });
    isRunning = true;

    let buffer = "";

    simProcess.stdout.on("data", (data) => {
      const lines = data.toString().split("\n");
      for (const line of lines) {
        if (!line.trim()) continue;
        try {
          const parsed = JSON.parse(line);
          //console.log("📤 Python Output:", parsed);

          const { publishMessage } = require("./mqtt");

          // Optionally publish updates to MQTT
          publishMessage?.("simulation/results", parsed);
        } catch {
          buffer += line;
        }
      }
    });

    simProcess.stderr.on("data", (data) => {
      console.error("🐍 Python Error:", data.toString());
    });

    simProcess.on("close", (code) => {
      console.log(`✅ Python simulation exited with code ${code}`);
      isRunning = false;
      simProcess = null;
      
      // Define where your final JSON is saved (e.g., "Backend/data/data.json")
      const dataFilePath = path.join(__dirname, "..", "data", "data.json");

      // Wait a moment to ensure Python finishes writing the file
      setTimeout(() => {
        try {
          if (fs.existsSync(dataFilePath)) {
            const jsonData = JSON.parse(fs.readFileSync(dataFilePath, "utf8"));
            console.log("📦 Loaded final simulation data file.");

            const { publishMessage } = require("./mqtt");

            // Publish it to your MQTT topic
            publishMessage("simulation/results", jsonData);
            console.log("📤 Published final JSON to MQTT topic simulation/results");
          } else {
            console.warn("⚠️ Final JSON file not found:", dataFilePath);
          }
        } catch (err) {
          console.error("❌ Error reading or publishing final JSON:", err);
        }
      }, 1000); // 1s delay buffer
    });

    // send initial data (ensure newline to satisfy readline or full read)
    simProcess.stdin.write(JSON.stringify(inputData));
    simProcess.stdin.end();

    resolve({ status: "started" });
  });
}

function stopSim() {
  return new Promise((resolve, reject) => {
    if (!isRunning || !simProcess) {
      return reject(new Error("Simulation not running"));
    }

    console.log("🛑 Stopping Python simulation...");
    simProcess.kill("SIGTERM");
    isRunning = false;
    simProcess = null;
    resolve({ status: "stopped" });
  });
}

function getSimState() {
  return { isRunning };
}

module.exports = { startSim, stopSim, getSimState };

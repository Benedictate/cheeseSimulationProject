// pythonHandler.js
const { spawn } = require("child_process");
const { publishMessage } = require("./mqtt"); // optional, if MQTT is active

let simProcess = null;
let isRunning = false;

function startSim(inputData) {
  return new Promise((resolve, reject) => {
    if (isRunning) return reject(new Error("Simulation already running"));

    console.log("🚀 Starting Python simulation...");
    simProcess = spawn("python3", ["MainTest.py"]); // Adjust path if Main.py is elsewhere
    isRunning = true;

    let buffer = "";

    simProcess.stdout.on("data", (data) => {
      const lines = data.toString().split("\n");
      for (const line of lines) {
        if (!line.trim()) continue;
        try {
          const parsed = JSON.parse(line);
          console.log("📤 Python Output:", parsed);

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
    });

    // send initial data
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

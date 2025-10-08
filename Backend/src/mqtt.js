const mqtt = require("mqtt");
const { startSim, stopSim, publishResult } = require("./pythonHandler");

let client;

function startMqttClient() {
  const brokerUrl = process.env.MQTT_BROKER_URL || "mqtt://localhost:1883";
  client = mqtt.connect(brokerUrl);

  client.on("connect", () => {
    console.log(`✅ Connected to MQTT broker at ${brokerUrl}`);

    // Subscribe to control commands (from Azure or external systems)
    client.subscribe("external/control", (err) => {
      if (err) console.error("❌ Subscription error:", err);
      else console.log("📡 Subscribed to external/control");
    });
  });

  // Handle incoming MQTT messages
  client.on("message", async (topic, message) => {
    try {
      const msgText = message.toString();
      console.log(`📥 MQTT message on ${topic}: ${msgText}`);
      const data = JSON.parse(msgText);

      // Expecting messages like: { "command": "start", "payload": { ...settings } }
      if (topic === "external/control") {
        const { command, payload } = data;

        if (command === "start") {
          console.log("🚀 Starting simulation via MQTT");
          startSim(payload); // start persistent Python process
        } else if (command === "stop") {
          console.log("🛑 Stopping simulation via MQTT");
          stopSim();
        } else {
          console.warn("⚠️ Unknown MQTT command:", command);
        }
      }
    } catch (err) {
      console.error("MQTT message handling error:", err);
    }
  });

  client.on("error", (err) => console.error("MQTT error:", err));
}

// Allows Node to publish simulation updates to MQTT
function publishMessage(topic, data) {
  if (!client) return console.error("MQTT client not initialized");
  client.publish(topic, JSON.stringify(data));
  console.log(`📤 Published to ${topic}`);
}

// Export both
module.exports = { startMqttClient, publishMessage };

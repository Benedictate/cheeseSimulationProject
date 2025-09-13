const mqtt = require("mqtt");

function startMqttClient() {
  const brokerUrl = process.env.MQTT_BROKER_URL || "mqtt://localhost:1883";
  const client = mqtt.connect(brokerUrl);

  client.on("connect", () => {
    console.log(`✅ Connected to MQTT broker at ${brokerUrl}`);
    client.subscribe("test/topic", (err) => {
      if (!err) {
        console.log("📡 Subscribed to test/topic");
      } else {
        console.error("❌ Subscription error:", err);
      }
    });
  });

  client.on("message", (topic, message) => {
    console.log(`📥 Message on ${topic}: ${message.toString()}`);
    // You can add logic here (e.g., save to DB, trigger API response, etc.)
  });

  client.on("error", (err) => {
    console.error("MQTT error:", err);
  });
}

module.exports = { startMqttClient };

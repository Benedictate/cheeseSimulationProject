  "use client"
  import mqtt from "mqtt";

  // --- MQTT for real-time results ---
  function useMqttResults(setSimulationResults) {
  useEffect(() => {
    const client = mqtt.connect("ws://localhost:9001"); // 🔧 change to your broker’s websocket URL

    client.on("connect", () => {
      console.log("📡 Connected to MQTT broker");
      client.subscribe("simulation/results", (err) => {
        if (!err) console.log("✅ Subscribed to simulation/results");
      });
    });

    client.on("message", (topic, message) => {
      if (topic === "simulation/results") {
        try {
          const parsed = JSON.parse(message.toString());
          setSimulationResults((prev) => (prev ? [...prev, parsed] : [parsed]));
        } catch (e) {
          console.warn("Skipping invalid MQTT message:", e);
        }
      }
    });

    return () => {
      client.end();
    };
  }, [setSimulationResults]);
}

export default useMqttResults
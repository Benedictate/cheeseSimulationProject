"use client"

import { useState } from "react"

function SimulationForm() {
  const backendUrl =
    import.meta.env.VITE_BACKEND_URL ||
    `${window.location.protocol}//${window.location.hostname}:3001`
  const [showSuccess, setShowSuccess] = useState(false)
  const [error, setError] = useState(null)
  const [isLoading, setIsLoading] = useState(false)

  const [config, setConfig] = useState({
    time_mode: "0",
    simulation_time: "6000",
    milk_to_process: "50000",
    pasteuriser_temp_optimal: "72",
    pasteuriser_flow_rate: "41.7",
    cheese_vat_vat_batch_size: "10000",
    cheese_vat_anomaly_probability: "10",
    cheese_vat_optimal_ph: "6.55",
    cheese_vat_milk_flow_rate: "5",
    curd_cutter_blade_wear_rate: "0.1",
    curd_cutter_auger_speed: "50",
    whey_drainer_target_mass: "1000",
    whey_drainer_target_moisture: "58.0",
    salting_machine_mellowing_time: "10",
    salting_machine_salt_recipe: "0.033",
    salting_machine_flow_rate: "50.0",
    cheese_presser_block_weight: "27",
    cheese_presser_mold_count: "5",
    cheese_presser_anomaly_chance: "0.1",
    ripener_initial_temp: "10",
  })

  const handleChange = (e) => {
    setConfig({
      ...config,
      [e.target.name]: e.target.value,
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsLoading(true)
    setError(null)
    setShowSuccess(false)

    const formattedConfig = {
      global: {
        time_mode: Number.parseInt(config.time_mode) || 0,
        simulation_time: Number.parseInt(config.simulation_time) || 6000,
        milk_to_process: Number.parseInt(config.milk_to_process) || 50000,
      },
      machines: {
        pasteuriser: {
          temp_optimal: Number.parseFloat(config.pasteuriser_temp_optimal) || 72,
          flow_rate: Number.parseFloat(config.pasteuriser_flow_rate) || 41.7,
        },
        cheese_vat: {
          vat_batch_size: Number.parseInt(config.cheese_vat_vat_batch_size) || 10000,
          anomaly_probability: Number.parseInt(config.cheese_vat_anomaly_probability) || 10,
          optimal_ph: Number.parseFloat(config.cheese_vat_optimal_ph) || 6.55,
          milk_flow_rate: Number.parseInt(config.cheese_vat_milk_flow_rate) || 5,
        },
        curd_cutter: {
          blade_wear_rate: Number.parseFloat(config.curd_cutter_blade_wear_rate) || 0.1,
          auger_speed: Number.parseInt(config.curd_cutter_auger_speed) || 50,
        },
        whey_drainer: {
          target_mass: Number.parseInt(config.whey_drainer_target_mass) || 1000,
          target_moisture: Number.parseFloat(config.whey_drainer_target_moisture) || 58.0,
        },
        cheddaring: {},
        salting_machine: {
          mellowing_time: Number.parseInt(config.salting_machine_mellowing_time) || 10,
          salt_recipe: Number.parseFloat(config.salting_machine_salt_recipe) || 0.033,
          flow_rate: Number.parseFloat(config.salting_machine_flow_rate) || 50.0,
        },
        cheese_presser: {
          block_weight: Number.parseInt(config.cheese_presser_block_weight) || 27,
          mold_count: Number.parseInt(config.cheese_presser_mold_count) || 5,
          anomaly_chance: Number.parseFloat(config.cheese_presser_anomaly_chance) || 0.1,
        },
        ripener: {
          initial_temp: Number.parseInt(config.ripener_initial_temp) || 10,
        },
      },
    }

    try {
      console.log("Starting simulation with form data...")
      console.log("Config:", JSON.stringify(formattedConfig, null, 2))

      const startResponse = await fetch(`${backendUrl}/api/start-simulation`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formattedConfig),
      })

      if (!startResponse.ok) {
        const errorData = await startResponse.json()
        throw new Error(errorData.error || "Failed to start simulation")
      }

      const result = await startResponse.json()
      console.log("Simulation started successfully:", result)

      setShowSuccess(true)
      setTimeout(() => setShowSuccess(false), 5000)
    } catch (err) {
      console.error("Error:", err)
      setError(`Failed to run simulation: ${err.message}`)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="simulation-form-container">
      {showSuccess && <div className="success-banner">Simulation started successfully!</div>}
      {error && <div className="error-banner">{error}</div>}

      <form onSubmit={handleSubmit} className="simulation-form">
        <h2>Simulation Configuration</h2>

        <div className="form-section">
          <h3>Global Settings</h3>

          <div className="form-field">
            <label htmlFor="time_mode">Time Mode:</label>
            <input
              type="number"
              id="time_mode"
              name="time_mode"
              value={config.time_mode}
              onChange={handleChange}
              placeholder="0"
            />
          </div>

          <div className="form-field">
            <label htmlFor="simulation_time">Simulation Time:</label>
            <input
              type="number"
              id="simulation_time"
              name="simulation_time"
              value={config.simulation_time}
              onChange={handleChange}
              placeholder="6000"
            />
          </div>

          <div className="form-field">
            <label htmlFor="milk_to_process">Milk to Process:</label>
            <input
              type="number"
              id="milk_to_process"
              name="milk_to_process"
              value={config.milk_to_process}
              onChange={handleChange}
              placeholder="50000"
            />
          </div>
        </div>

        <div className="form-section">
          <h3>Pasteuriser</h3>

          <div className="form-field">
            <label htmlFor="pasteuriser_temp_optimal">Optimal Temperature:</label>
            <input
              type="number"
              step="0.1"
              id="pasteuriser_temp_optimal"
              name="pasteuriser_temp_optimal"
              value={config.pasteuriser_temp_optimal}
              onChange={handleChange}
              placeholder="72"
            />
          </div>

          <div className="form-field">
            <label htmlFor="pasteuriser_flow_rate">Flow Rate:</label>
            <input
              type="number"
              step="0.1"
              id="pasteuriser_flow_rate"
              name="pasteuriser_flow_rate"
              value={config.pasteuriser_flow_rate}
              onChange={handleChange}
              placeholder="41.7"
            />
          </div>
        </div>

        <div className="form-section">
          <h3>Cheese Vat</h3>

          <div className="form-field">
            <label htmlFor="cheese_vat_vat_batch_size">Vat Batch Size:</label>
            <input
              type="number"
              id="cheese_vat_vat_batch_size"
              name="cheese_vat_vat_batch_size"
              value={config.cheese_vat_vat_batch_size}
              onChange={handleChange}
              placeholder="10000"
            />
          </div>

          <div className="form-field">
            <label htmlFor="cheese_vat_anomaly_probability">Anomaly Probability:</label>
            <input
              type="number"
              id="cheese_vat_anomaly_probability"
              name="cheese_vat_anomaly_probability"
              value={config.cheese_vat_anomaly_probability}
              onChange={handleChange}
              placeholder="10"
            />
          </div>

          <div className="form-field">
            <label htmlFor="cheese_vat_optimal_ph">Optimal pH:</label>
            <input
              type="number"
              step="0.01"
              id="cheese_vat_optimal_ph"
              name="cheese_vat_optimal_ph"
              value={config.cheese_vat_optimal_ph}
              onChange={handleChange}
              placeholder="6.55"
            />
          </div>

          <div className="form-field">
            <label htmlFor="cheese_vat_milk_flow_rate">Milk Flow Rate:</label>
            <input
              type="number"
              id="cheese_vat_milk_flow_rate"
              name="cheese_vat_milk_flow_rate"
              value={config.cheese_vat_milk_flow_rate}
              onChange={handleChange}
              placeholder="5"
            />
          </div>
        </div>

        <div className="form-section">
          <h3>Curd Cutter</h3>

          <div className="form-field">
            <label htmlFor="curd_cutter_blade_wear_rate">Blade Wear Rate:</label>
            <input
              type="number"
              step="0.01"
              id="curd_cutter_blade_wear_rate"
              name="curd_cutter_blade_wear_rate"
              value={config.curd_cutter_blade_wear_rate}
              onChange={handleChange}
              placeholder="0.1"
            />
          </div>

          <div className="form-field">
            <label htmlFor="curd_cutter_auger_speed">Auger Speed:</label>
            <input
              type="number"
              id="curd_cutter_auger_speed"
              name="curd_cutter_auger_speed"
              value={config.curd_cutter_auger_speed}
              onChange={handleChange}
              placeholder="50"
            />
          </div>
        </div>

        <div className="form-section">
          <h3>Whey Drainer</h3>

          <div className="form-field">
            <label htmlFor="whey_drainer_target_mass">Target Mass:</label>
            <input
              type="number"
              id="whey_drainer_target_mass"
              name="whey_drainer_target_mass"
              value={config.whey_drainer_target_mass}
              onChange={handleChange}
              placeholder="1000"
            />
          </div>

          <div className="form-field">
            <label htmlFor="whey_drainer_target_moisture">Target Moisture:</label>
            <input
              type="number"
              step="0.1"
              id="whey_drainer_target_moisture"
              name="whey_drainer_target_moisture"
              value={config.whey_drainer_target_moisture}
              onChange={handleChange}
              placeholder="58.0"
            />
          </div>
        </div>

        <div className="form-section">
          <h3>Salting Machine</h3>

          <div className="form-field">
            <label htmlFor="salting_machine_mellowing_time">Mellowing Time:</label>
            <input
              type="number"
              id="salting_machine_mellowing_time"
              name="salting_machine_mellowing_time"
              value={config.salting_machine_mellowing_time}
              onChange={handleChange}
              placeholder="10"
            />
          </div>

          <div className="form-field">
            <label htmlFor="salting_machine_salt_recipe">Salt Recipe:</label>
            <input
              type="number"
              step="0.001"
              id="salting_machine_salt_recipe"
              name="salting_machine_salt_recipe"
              value={config.salting_machine_salt_recipe}
              onChange={handleChange}
              placeholder="0.033"
            />
          </div>

          <div className="form-field">
            <label htmlFor="salting_machine_flow_rate">Flow Rate:</label>
            <input
              type="number"
              step="0.1"
              id="salting_machine_flow_rate"
              name="salting_machine_flow_rate"
              value={config.salting_machine_flow_rate}
              onChange={handleChange}
              placeholder="50.0"
            />
          </div>
        </div>

        <div className="form-section">
          <h3>Cheese Presser</h3>

          <div className="form-field">
            <label htmlFor="cheese_presser_block_weight">Block Weight:</label>
            <input
              type="number"
              id="cheese_presser_block_weight"
              name="cheese_presser_block_weight"
              value={config.cheese_presser_block_weight}
              onChange={handleChange}
              placeholder="27"
            />
          </div>

          <div className="form-field">
            <label htmlFor="cheese_presser_mold_count">Mold Count:</label>
            <input
              type="number"
              id="cheese_presser_mold_count"
              name="cheese_presser_mold_count"
              value={config.cheese_presser_mold_count}
              onChange={handleChange}
              placeholder="5"
            />
          </div>

          <div className="form-field">
            <label htmlFor="cheese_presser_anomaly_chance">Anomaly Chance:</label>
            <input
              type="number"
              step="0.01"
              id="cheese_presser_anomaly_chance"
              name="cheese_presser_anomaly_chance"
              value={config.cheese_presser_anomaly_chance}
              onChange={handleChange}
              placeholder="0.1"
            />
          </div>
        </div>

        <div className="form-section">
          <h3>Ripener</h3>

          <div className="form-field">
            <label htmlFor="ripener_initial_temp">Initial Temperature:</label>
            <input
              type="number"
              id="ripener_initial_temp"
              name="ripener_initial_temp"
              value={config.ripener_initial_temp}
              onChange={handleChange}
              placeholder="10"
            />
          </div>
        </div>

        <div className="button-group">
          <button type="submit" className="btn btn-save" disabled={isLoading}>
            {isLoading ? "Running Simulation..." : "Start Simulation"}
          </button>
        </div>
      </form>
    </div>
  )
}

export default SimulationForm

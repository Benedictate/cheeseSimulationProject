"use client"

import { useState } from "react"
import "./ConnectionTest.css"

const ConnectionTest = () => {
  const [status, setStatus] = useState("Not tested")
  const [message, setMessage] = useState("")
  const [loading, setLoading] = useState(false)

  const testConnection = async () => {
    setLoading(true)
    setStatus("Testing...")
    setMessage("")

    try {
      const response = await fetch("http://127.0.0.1:3001/run-simulation", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ test: true }),
      })

      if (response.ok) {
        const data = await response.json()
        setStatus("Connected")
        setMessage(data.message || "Backend responded successfully")
      } else {
        setStatus("Cannot connect")
        setMessage(`Server responded with status: ${response.status}`)
      }
    } catch (error) {
      setStatus("Cannot connect")
      setMessage("Failed to reach the server")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="connection-test">
      <h1>Backend Connection Test</h1>

      <div className="test-section">
        <button onClick={testConnection} disabled={loading} className="test-button">
          {loading ? "Testing..." : "Test Connection"}
        </button>

        <div className="status-display">
          <div className={`status ${status.toLowerCase().replace(" ", "-")}`}>Status: {status}</div>

          {message && <div className="message">Message: {message}</div>}
        </div>
      </div>

      <div className="endpoint-info">
        <p>
          Testing endpoint: <code>http://127.0.0.1:3001/run-simulation</code>
        </p>
      </div>
    </div>
  )
}

export default ConnectionTest


"use client"

import { useState } from "react"
import "./ConnectionTest.css"

const ConnectionTest = () => {
  const [status, setStatus] = useState("Not tested")
  const [message, setMessage] = useState("")
  const [loading, setLoading] = useState(false)
  const [responseData, setResponseData] = useState(null)

  const testConnection = async () => {
    setLoading(true)
    setStatus("Testing...")
    setMessage("")
    setResponseData(null)

    try {
      console.log("Attempting to connect to backend...")

      const response = await fetch("http://localhost:3001/run-simulation", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          test: true,
          timestamp: new Date().toISOString(),
          source: "frontend-connection-test",
        }),
      })

      console.log("Response status:", response.status)

      if (response.ok) {
        const data = await response.json()
        console.log("Response data:", data)

        setStatus("Connected")
        setMessage(data.message || "Backend responded successfully")
        setResponseData(data)
      } else {
        setStatus("Cannot connect")
        setMessage(`Server responded with status: ${response.status}`)
      }
    } catch (error) {
      console.error("Connection error:", error)
      setStatus("Cannot connect")
      setMessage(`Failed to reach the server: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const testHealthCheck = async () => {
    setLoading(true)
    setStatus("Testing health...")
    setMessage("")

    try {
      const response = await fetch("http://localhost:3001/health", {
        method: "GET",
      })

      if (response.ok) {
        const data = await response.json()
        setStatus("Connected")
        setMessage(`Health check passed: ${data.status}`)
      } else {
        setStatus("Cannot connect")
        setMessage(`Health check failed with status: ${response.status}`)
      }
    } catch (error) {
      setStatus("Cannot connect")
      setMessage(`Health check failed: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="connection-test">
      <h1>Backend Connection Test</h1>

      <div className="test-section">
        <button onClick={testConnection} disabled={loading} className="test-button">
          {loading ? "Testing..." : "Test Full Connection"}
        </button>

        <button onClick={testHealthCheck} disabled={loading} className="test-button secondary">
          {loading ? "Testing..." : "Test Health Check"}
        </button>

        <div className="status-display">
          <div className={`status ${status.toLowerCase().replace(" ", "-")}`}>Status: {status}</div>

          {message && <div className="message">Message: {message}</div>}

          {responseData && (
            <div className="response-data">
              <h3>Response Data:</h3>
              <pre>{JSON.stringify(responseData, null, 2)}</pre>
            </div>
          )}
        </div>
      </div>

      <div className="endpoint-info">
        <p>Testing endpoints:</p>
        <ul>
          <li>
            <code>POST http://localhost:3001/run-simulation</code>
          </li>
          <li>
            <code>GET http://localhost:3001/health</code>
          </li>
        </ul>
        <p>
          <strong>Make sure your backend is running on port 3001!</strong>
        </p>
      </div>
    </div>
  )
}

export default ConnectionTest

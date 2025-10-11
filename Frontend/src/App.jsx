"use client"

import SimulationForm from "./components/SimulationForm"
import "./App.css"

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>Cheese Manufacturing Simulation</h1>
        <p>Configure simulation parameters</p>
      </header>

      <main className="app-main">
        <SimulationForm />
      </main>
    </div>
  )
}

export default App

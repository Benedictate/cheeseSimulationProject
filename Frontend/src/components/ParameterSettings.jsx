"use client"

function ParameterSettings({ parameters, onParameterChange, disabled }) {
  const handleChange = (section, key, value) => {
    const numericValue = isNaN(value) ? value : Number(value);
    onParameterChange(section, key, numericValue);
  };

  return (
    <div className="card">
      <h2>⚙️ Simulation Parameters</h2>

      {/* GLOBAL SETTINGS */}
      <div className="parameter-section">
        <h3>🌍 Global Settings</h3>
        <div className="parameter-grid">
          <div className="parameter-item">
            <label>Time Mode</label>
            <input
              type="number"
              value={parameters.global.time_mode}
              onChange={(e) => handleChange("global", "time_mode", e.target.value)}
              disabled={disabled}
            />
          </div>

          <div className="parameter-item">
            <label>Simulation Time</label>
            <input
              type="number"
              value={parameters.global.simulation_time}
              onChange={(e) => handleChange("global", "simulation_time", e.target.value)}
              disabled={disabled}
            />
          </div>

          <div className="parameter-item">
            <label>Milk to Process</label>
            <input
              type="number"
              value={parameters.global.milk_to_process}
              onChange={(e) => handleChange("global", "milk_to_process", e.target.value)}
              disabled={disabled}
            />
          </div>
        </div>
      </div>

      {/* MACHINES SECTION */}
      <div className="parameter-section">
        <h3>🏭 Machines</h3>

        {/* Pasteuriser */}
        <MachineSection
          title="Pasteuriser"
          data={parameters.machines.pasteuriser}
          section="pasteuriser"
          onChange={handleChange}
          disabled={disabled}
        />

        {/* Cheese Vat */}
        <MachineSection
          title="Cheese Vat"
          data={parameters.machines.cheese_vat}
          section="cheese_vat"
          onChange={handleChange}
          disabled={disabled}
        />

        {/* Curd Cutter */}
        <MachineSection
          title="Curd Cutter"
          data={parameters.machines.curd_cutter}
          section="curd_cutter"
          onChange={handleChange}
          disabled={disabled}
        />

        {/* Whey Drainer */}
        <MachineSection
          title="Whey Drainer"
          data={parameters.machines.whey_drainer}
          section="whey_drainer"
          onChange={handleChange}
          disabled={disabled}
        />

        {/* Cheddaring */}
        <MachineSection
          title="Cheddaring"
          data={parameters.machines.cheddaring}
          section="cheddaring"
          onChange={handleChange}
          disabled={disabled}
        />

        {/* Salting Machine */}
        <MachineSection
          title="Salting Machine"
          data={parameters.machines.salting_machine}
          section="salting_machine"
          onChange={handleChange}
          disabled={disabled}
        />

        {/* Cheese Presser */}
        <MachineSection
          title="Cheese Presser"
          data={parameters.machines.cheese_presser}
          section="cheese_presser"
          onChange={handleChange}
          disabled={disabled}
        />

        {/* Ripener */}
        <MachineSection
          title="Ripener"
          data={parameters.machines.ripener}
          section="ripener"
          onChange={handleChange}
          disabled={disabled}
        />
      </div>
    </div>
  );
}

/** Generic subcomponent for a machine block **/
function MachineSection({ title, data, section, onChange, disabled }) {
  return (
    <div className="machine-section">
      <h4>{title}</h4>
      <div className="parameter-grid">
        {Object.entries(data).map(([key, value]) => (
          <div className="parameter-item" key={key}>
            <label>{key.replace(/_/g, " ")}</label>
            <input
              type="number"
              value={value}
              onChange={(e) => onChange(section, key, e.target.value)}
              disabled={disabled}
            />
          </div>
        ))}
      </div>
    </div>
  );
}

export default ParameterSettings;

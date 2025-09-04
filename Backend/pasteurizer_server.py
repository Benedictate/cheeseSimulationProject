import simpy
import random
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import threading
import time

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Global variables to store simulation state
simulation_results = {}
simulation_running = False
simulation_thread = None

class Pasteuriser:
    def __init__(self, env, config):
        self.env = env
        
        # Get configuration from frontend
        self.temp_min_operating = config.get('tempMinOperating', 68)
        self.temp_optimal_min = config.get('tempOptimalMin', 70)
        self.temp_optimal = config.get('tempOptimal', 72)
        self.temp_optimal_max = config.get('tempOptimalMax', 74)
        self.temp_burn_threshold = config.get('tempBurnThreshold', 77)
        
        self.step_duration_sec = config.get('stepDurationSec', 15)
        self.startup_duration = config.get('startupDuration', 20)
        self.cooldown_duration = config.get('cooldownDuration', 8)
        
        self.temp_drop_per_step = config.get('tempDropPerStep', 1)
        self.temp_rise_when_cold = config.get('tempRiseWhenCold', 1.5)
        self.flow_rate = config.get('flowRate', 41.7)
        
        self.total_milk = config.get('totalMilk', 1000)
        
        # Anomaly settings
        self.anomalies = config.get('anomalies', {})
        
        # Internal state
        self.temperature = self.temp_optimal
        self.cooling_overheat = False
        self.start_tank = self.total_milk
        self.balance_tank = 0.0
        self.pasteurized_total = 0.0
        self.burnt_total = 0.0
        
        # Data logging
        self.log_data = []
        
        print(f"Pasteurizer initialized with config: {config}")

    def format_time(self):
        total_seconds = self.env.now * self.step_duration_sec
        minutes = int(total_seconds // 60)
        seconds = int(total_seconds % 60)
        return f"{minutes}:{seconds:02d}"

    def log_status(self, status):
        log_entry = {
            'time': self.format_time(),
            'step': self.env.now,
            'start_tank': round(self.start_tank, 2),
            'balance_tank': round(self.balance_tank, 2),
            'pasteurized_total': round(self.pasteurized_total, 2),
            'burnt_total': round(self.burnt_total, 2),
            'temperature': round(self.temperature, 2),
            'status': status,
            'timestamp': datetime.now().isoformat()
        }
        self.log_data.append(log_entry)
        
        print(f"{log_entry['time']:<7} "
              f"{log_entry['start_tank']:>7.2f}        "
              f"{log_entry['balance_tank']:>7.2f}        "
              f"{log_entry['pasteurized_total']:>7.2f}        "
              f"{log_entry['burnt_total']:>7.2f}        "
              f"{log_entry['temperature']:>5.2f}      "
              f"{status}")

    def apply_anomalies(self):
        """Apply anomalies based on frontend configuration"""
        if self.anomalies.get('tempVariation', {}).get('enabled', False):
            # Force temperature variation
            variation = random.uniform(-5, 5)
            self.temperature += variation
            return f"Anomaly: Temperature variation {variation:+.2f}°C"
        
        if self.anomalies.get('equipmentFailure', {}).get('enabled', False):
            # Force equipment failure (reduce flow rate)
            self.flow_rate *= 0.5
            return "Anomaly: Equipment failure - reduced flow rate"
        
        if self.anomalies.get('flowRateIssue', {}).get('enabled', False):
            # Force flow rate issue
            self.flow_rate *= random.uniform(0.3, 0.7)
            return "Anomaly: Flow rate issue"
        
        # Check probability-based anomalies
        if random.random() < self.anomalies.get('tempVariation', {}).get('probability', 0):
            variation = random.uniform(-3, 3)
            self.temperature += variation
            return f"Random anomaly: Temperature variation {variation:+.2f}°C"
        
        return None

    def process(self):
        global simulation_results
        
        print(f"{'Time':<7} {'StartTank':>7} {'BalanceTank':>12} {'Pasteurized':>12} {'Burnt':>7} {'Temp':>7} Status")
        print("-" * 70)
        
        # --- Startup phase ---
        for step in range(self.startup_duration):
            anomaly_msg = self.apply_anomalies()
            status = "Startup / Heating"
            if anomaly_msg:
                status += f" - {anomaly_msg}"
            self.log_status(status)
            yield self.env.timeout(1)

        # --- Processing loop ---
        while self.start_tank > 0 or self.balance_tank > 0:
            # Apply anomalies
            anomaly_msg = self.apply_anomalies()
            
            # Choose source
            if self.start_tank > 0:
                milk_source = "Start Tank"
                milk_available = self.start_tank
            else:
                milk_source = "Balance Tank"
                milk_available = self.balance_tank

            milk_this_step = min(self.flow_rate, milk_available)

            # --- Temperature logic ---
            if self.cooling_overheat:
                self.temperature -= self.temp_drop_per_step
                status = "Cooling after Overheat"
                if self.temperature <= self.temp_optimal:
                    self.cooling_overheat = False
                    status = "Cooled - Resuming"
                if anomaly_msg:
                    status += f" - {anomaly_msg}"
                yield self.env.timeout(1)
                self.log_status(status)
                continue

            if self.temperature >= self.temp_burn_threshold:
                self.burnt_total += milk_this_step
                status = f"Burnt milk! {milk_this_step:.2f}L"
                self.cooling_overheat = True
                if milk_source == "Start Tank":
                    self.start_tank -= milk_this_step
                else:
                    self.balance_tank -= milk_this_step

            elif self.temperature < self.temp_optimal_min:
                self.balance_tank += milk_this_step
                status = f"Too cold - recirculating {milk_this_step:.2f}L and reheating"
                if milk_source == "Start Tank":
                    self.start_tank -= milk_this_step
                else:
                    self.balance_tank -= milk_this_step
                self.temperature += self.temp_rise_when_cold

            elif self.temp_optimal_min <= self.temperature <= self.temp_optimal_max:
                self.pasteurized_total += milk_this_step
                status = f"Pasteurized from {milk_source}"
                if milk_source == "Start Tank":
                    self.start_tank -= milk_this_step
                else:
                    self.balance_tank -= milk_this_step

            else:
                self.balance_tank += milk_this_step
                status = f"Too hot - recirculating {milk_this_step:.2f}L"
                if milk_source == "Start Tank":
                    self.start_tank -= milk_this_step
                else:
                    self.balance_tank -= milk_this_step

            # Random temp fluctuation (unless overridden by anomalies)
            if not anomaly_msg or "Temperature variation" not in anomaly_msg:
                self.temperature += random.uniform(-2, 2)

            if anomaly_msg:
                status += f" - {anomaly_msg}"

            # Log and wait
            self.log_status(status)
            yield self.env.timeout(1)
            
            # Update global results for real-time monitoring
            simulation_results.update({
                'current_step': self.env.now,
                'start_tank': self.start_tank,
                'balance_tank': self.balance_tank,
                'pasteurized_total': self.pasteurized_total,
                'burnt_total': self.burnt_total,
                'temperature': self.temperature,
                'status': status,
                'progress': min(100, (self.pasteurized_total + self.burnt_total) / self.total_milk * 100)
            })

        # --- Cooldown phase ---
        for step in range(self.cooldown_duration):
            self.log_status("Cooldown")
            yield self.env.timeout(1)
        
        # Final results
        simulation_results.update({
            'completed': True,
            'final_results': {
                'total_milk': self.total_milk,
                'pasteurized_total': self.pasteurized_total,
                'burnt_total': self.burnt_total,
                'efficiency': (self.pasteurized_total / self.total_milk) * 100,
                'waste_percentage': (self.burnt_total / self.total_milk) * 100,
                'log_data': self.log_data
            }
        })
        
        global simulation_running
        simulation_running = False
        print(f"\n=== SIMULATION COMPLETE ===")
        print(f"Total Milk: {self.total_milk:.2f}L")
        print(f"Pasteurized: {self.pasteurized_total:.2f}L ({(self.pasteurized_total/self.total_milk)*100:.1f}%)")
        print(f"Burnt: {self.burnt_total:.2f}L ({(self.burnt_total/self.total_milk)*100:.1f}%)")

def run_simulation(config):
    """Run the pasteurizer simulation with given configuration"""
    global simulation_results, simulation_running
    
    simulation_running = True
    simulation_results = {
        'started': True,
        'start_time': datetime.now().isoformat(),
        'config': config
    }
    
    # Create SimPy environment
    env = simpy.Environment()
    
    # Create and run pasteurizer
    pasteurizer = Pasteuriser(env, config)
    env.process(pasteurizer.process())
    
    # Run simulation
    env.run()

# API Endpoints
@app.route('/api/start-simulation', methods=['POST'])
def start_simulation():
    global simulation_thread, simulation_running, simulation_results
    
    if simulation_running:
        return jsonify({
            'success': False,
            'message': 'Simulation already running'
        }), 400
    
    try:
        config = request.json
        print(f"Received configuration: {config}")
        
        # Reset results
        simulation_results = {}
        
        # Start simulation in separate thread
        simulation_thread = threading.Thread(target=run_simulation, args=(config,))
        simulation_thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Simulation started successfully',
            'config': config
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error starting simulation: {str(e)}'
        }), 500

@app.route('/api/simulation-status', methods=['GET'])
def get_simulation_status():
    global simulation_results, simulation_running
    
    return jsonify({
        'running': simulation_running,
        'results': simulation_results
    })

@app.route('/api/stop-simulation', methods=['POST'])
def stop_simulation():
    global simulation_running, simulation_thread
    
    simulation_running = False
    
    return jsonify({
        'success': True,
        'message': 'Simulation stopped'
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'simulation_running': simulation_running
    })

if __name__ == '__main__':
    print("Starting Pasteurizer Simulation Server...")
    print("Server will run on http://127.0.0.1:3001")
    app.run(host='127.0.0.1', port=3001, debug=True)

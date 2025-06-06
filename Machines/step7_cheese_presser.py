import simpy
import random
import json
import pandas as pd  # display results in table and save files
from datetime import datetime

#simulation
#Constants

BASE_MOISTURE_REDUCTION_RATE = 0.05  # how much moisture is reduced by default
MOISTURE_MIN_THRESHOLD = 32.0        # lowest moisture content allowed in the cheese
MAINTENANCE_THRESHOLD = 85           # if machine health drops below this, maintenance is triggered
MAINTENANCE_DURATION = 10            # time (in minutes) needed to perform maintenance
ANOMALY_CHANCE = 0.1                 # 10% chance something goes wrong with a batch

# machine logic
class CheesePressMachine:
    def __init__(self, env, mold_count=5):
        self.env = env  # keeps track of simulation time
        self.mold_count = mold_count
        self.health = 100.0  # machine starts in perfect condition
        self.is_under_maintenance = False
        self.log = []  # this is where we store batch results

    # This function simulates the pressing of one batch
    def press_batch(self, batch):
        start_time = self.env.now  # we log when we start
        anomaly_occurred = False
        maintenance_flag = False

        # Check if the machine needs maintenance before pressing
        if self.health < MAINTENANCE_THRESHOLD:
            self.is_under_maintenance = True
            yield self.env.timeout(MAINTENANCE_DURATION)  # simulate downtime
            self.health = 100.0  # machine is restored
            self.is_under_maintenance = False
            maintenance_flag = True

        # Now simulate the actual pressing time for this batch
        yield self.env.timeout(batch['press_duration_min'])

        # Calculate moisture reduction based on pressure and time
        reduction = BASE_MOISTURE_REDUCTION_RATE * (batch['press_pressure_psi'] / 50) * (batch['press_duration_min'] / 60)
        final_moisture = max(batch['input_moisture_percent'] - reduction * 100, MOISTURE_MIN_THRESHOLD)

        # Calculate how much curd weight is lost as whey during pressing
        weight_loss = batch['input_weight_kg'] * (reduction * 0.9)
        output_weight = batch['input_weight_kg'] - weight_loss

        # Simulate random anomaly (e.g., pressure failure, sensor error)
        if random.random() < ANOMALY_CHANCE:
            anomaly_occurred = True
            final_moisture += 2  # moisture wasn't reduced properly
            output_weight -= 0.1  # slight underperformance

        # Pressing wears the machine down a little bit
        self.health -= random.uniform(1, 3)

        end_time = self.env.now  # log when process is finsihed

        # Save everything in the log
        self.log.append({
            "batch_id": batch['batch_id'],
            "start_minute": round(start_time, 2),
            "end_minute": round(end_time, 2),
            "input_weight_kg": round(batch['input_weight_kg'], 2),
            "output_weight_kg": round(output_weight, 2),
            "input_moisture_percent": round(batch['input_moisture_percent'], 2),
            "output_moisture_percent": round(final_moisture, 2),
            "press_pressure_psi": round(batch['press_pressure_psi'], 2),
            "press_duration_min": batch['press_duration_min'],
            "anomaly": anomaly_occurred,
            "maintenance_flag": maintenance_flag
        })

# this function generates a new batch every 5 minutes
def batch_generator(env, machine):
    batch_id = 1
    while True:
        #makes a batch with random input values
        batch = {
            "batch_id": f"B{batch_id}",
            "input_weight_kg": random.uniform(8, 12),
            "input_moisture_percent": random.uniform(38, 42),
            "press_pressure_psi": random.uniform(30, 60),
            "press_duration_min": random.randint(45, 60)
        }
        # Passing the batch to the machine
        env.process(machine.press_batch(batch))
        batch_id += 1

        # Wait 5 minutes before sarting the next batch
        yield env.timeout(5)

# Run the simulation for 300 minutes (5 hours of production)
env = simpy.Environment()
machine = CheesePressMachine(env)
env.process(batch_generator(env, machine))
env.run(until=300)

#Results

# Convert the logs into a table
df = pd.DataFrame(machine.log)

print("\nCheese Press Log:\n")
print(df.to_string(index=False))

# Saving the log to CSV and JSON so we can analyze or visualize it later for AI implementation
df.to_csv("cheese_press_output.csv", index=False)
df.to_json("cheese_press_output.json", orient="records", indent=2)

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


# machine logic
class CheesePresser:
    def __init__(self, env, input_conveyor, output_conveyor, clock, anomaly_chance, mold_count=None):
        self.env = env
        self.input_conveyor = input_conveyor
        self.output_conveyor = output_conveyor
        self.anomaly_chance = anomaly_chance
        self.clock = clock()
        self.mold_count = mold_count
        self.health = 100.0
        self.is_under_maintenance = False
        self.log = []

    def press_batch(self, batch):
        start_time = self.env.now
        anomaly_occurred = False
        maintenance_flag = False

        if self.health < MAINTENANCE_THRESHOLD:
            self.is_under_maintenance = True
            yield self.env.timeout(MAINTENANCE_DURATION)
            self.health = 100.0
            self.is_under_maintenance = False
            maintenance_flag = True

        yield self.env.timeout(batch['press_duration_min'])

        reduction = BASE_MOISTURE_REDUCTION_RATE * (batch['press_pressure_psi'] / 50) * (batch['press_duration_min'] / 60)
        final_moisture = max(batch['input_moisture_percent'] - reduction * 100, MOISTURE_MIN_THRESHOLD)
        weight_loss = batch['input_weight_kg'] * (reduction * 0.9)
        output_weight = batch['input_weight_kg'] - weight_loss

        if random.random() < self.anomaly_chance:
            anomaly_occurred = True
            final_moisture += 2
            output_weight -= 0.1

        self.health -= random.uniform(1, 3)
        end_time = self.env.now

        # Log results
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
            "maintenance_flag": maintenance_flag,
            "time": self.clock.now()
        })

        # Forward batch to output conveyor
        batch['output_weight_kg'] = output_weight
        batch['output_moisture_percent'] = final_moisture
        yield self.output_conveyor.put(batch)
    
    # #Results
    # # Convert the logs into a table
    # df = pd.DataFrame(machine.log)

    # print("\nCheese Press Log:\n")
    # print(df.to_string(index=False))

    # # Saving the log to CSV and JSON so we can analyze or visualize it later for AI implementation
    # df.to_json("cheese_press_output.json", orient="records", indent=2) 
    
    @staticmethod
    def run(env, input_conveyor, output_conveyor, clock, anomaly_chance, mold_count=None):
        machine = CheesePresser(env, input_conveyor, output_conveyor, clock, anomaly_chance, mold_count)

        def consumer(env, input_conveyor, machine):
            while True:
                batch = yield input_conveyor.get()
                env.process(machine.press_batch(batch))

        env.process(consumer(env, input_conveyor, machine))
        return machine
    
  
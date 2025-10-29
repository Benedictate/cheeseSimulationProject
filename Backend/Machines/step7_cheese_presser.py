import simpy
import random
import json
import os
from datetime import datetime
from helpers.ndjson_logger import build_standard_event

#simulation
#Constants

BASE_MOISTURE_REDUCTION_RATE = 0.05  # how much moisture is reduced by default
MOISTURE_MIN_THRESHOLD = 32.0        # lowest moisture content allowed in the cheese
MAINTENANCE_THRESHOLD = 85           # if machine health drops below this, maintenance is triggered
MAINTENANCE_DURATION = 10            # time (in minutes) needed to perform maintenance


# machine logic
class CheesePresser:
    def __init__(self, env, input_conveyor, output_conveyor, clock, anomaly_chance, mold_count=None, logger=None):
        self.env = env
        self.input_conveyor = input_conveyor
        self.output_conveyor = output_conveyor
        self.anomaly_chance = anomaly_chance
        self.clock = clock()
        self.mold_count = mold_count
        self.health = 100.0
        self.is_under_maintenance = False
        self.observer = []
        self.logger = logger

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

        # Report whole minutes (integer)
        event = {
            "sim_time_min": int(self.env.now),
            "utc_time": self.clock.now(),
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
            "machine": "cheese_presser"
        }
        self.observer.append(event)
        if self.logger:
            self.logger.log_event(
                build_standard_event(
                    machine="cheese_presser",
                    sim_time_min=event["sim_time_min"],
                    utc_time=event["utc_time"],
                    batch_id=event["batch_id"],
                    start_minute=event["start_minute"],
                    end_minute=event["end_minute"],
                    input_weight_kg=event["input_weight_kg"],
                    output_weight_kg=event["output_weight_kg"],
                    input_moisture_percent=event["input_moisture_percent"],
                    output_moisture_percent=event["output_moisture_percent"],
                    press_pressure_psi=event["press_pressure_psi"],
                    press_duration_min=event["press_duration_min"],
                    anomaly=event["anomaly"],
                    maintenance_flag=event["maintenance_flag"],
                )
            )

        # Forward batch to output conveyor
        batch['output_weight_kg'] = output_weight
        batch['output_moisture_percent'] = final_moisture
        yield self.output_conveyor.put(batch)
    
    def save_observations_to_json(self, filename='Backend/data/cheese_presser_data.json'):
        folder = os.path.dirname(filename)
        if folder:
            os.makedirs(folder, exist_ok=True)

        with open(filename, 'w') as f:
            json.dump(self.observer, f, indent=4)

        print(f"Observations saved to {filename}")
    
    @staticmethod
    def run(env, input_conveyor, output_conveyor, clock, anomaly_chance, mold_count=None, logger=None):
        machine = CheesePresser(env, input_conveyor, output_conveyor, clock, anomaly_chance, mold_count, logger)

        def consumer(env, input_conveyor, machine):
            while True:
                batch = yield input_conveyor.get()
                env.process(machine.press_batch(batch))

        env.process(consumer(env, input_conveyor, machine))
        return machine

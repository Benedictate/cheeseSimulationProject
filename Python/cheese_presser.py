import simpy
import random
from datetime import datetime, timezone
import json
import os
import pandas as pd


class CheesePressMachine:
    def __init__(self, env, input_conveyor, output_conveyor, mold_count=5):
        self.env = env
        self.input_conveyor = input_conveyor
        self.output_conveyor = output_conveyor
        self.mold_count = mold_count
        self.health = 100.0
        self.is_under_maintenance = False
        self.log = []

    def press_controller(self):
        while True:
            batch = yield self.input_conveyor.get()
            self.env.process(self.press_batch(batch))

    def press_batch(self, batch):
        start_time = self.env.now
        anomaly_occurred = False
        maintenance_flag = False

        if self.health < 85:
            self.is_under_maintenance = True
            yield self.env.timeout(10)
            self.health = 100.0
            self.is_under_maintenance = False
            maintenance_flag = True

        yield self.env.timeout(batch['press_duration_min'])

        reduction = 0.05 * (batch['press_pressure_psi'] / 50) * (batch['press_duration_min'] / 60)
        final_moisture = max(batch['curd_moisture_pct'] - reduction * 100, 32.0)
        weight_loss = batch['curd_volume_l'] * (reduction * 0.9)
        output_weight = batch['curd_volume_l'] - weight_loss

        if random.random() < 0.1:
            anomaly_occurred = True
            final_moisture += 2
            output_weight -= 0.1

        self.health -= random.uniform(1, 3)
        end_time = self.env.now

        self.log.append({
            "batch_id": batch['batch_id'],
            "start_minute": round(start_time, 2),
            "end_minute": round(end_time, 2),
            "duration_min": batch['press_duration_min'],
            "input_volume_l": round(batch['curd_volume_l'], 2),
            "output_weight_kg": round(output_weight, 2),
            "input_moisture_pct": round(batch['curd_moisture_pct'], 2),
            "output_moisture_pct": round(final_moisture, 2),
            "press_pressure_psi": round(batch['press_pressure_psi'], 2),
            "end_temperature_c": round(batch.get('end_temperature_c', 0), 2),
            "process_time_min": batch.get('process_time_min', 0),
            "anomaly": anomaly_occurred,
            "maintenance_flag": maintenance_flag,
            "machine_health_post": round(self.health, 2),
            "utc_time": datetime.now(timezone.utc).isoformat()
        })

        # Forward the batch to the next machine (if any)
        batch['output_weight_kg'] = round(output_weight, 2)
        batch['output_moisture_pct'] = round(final_moisture, 2)
        yield self.output_conveyor.put(batch)

    def save_logs(self, json_path='data/cheese_press_data.json', csv_path='data/cheese_press_data.csv'):
        folder = os.path.dirname(json_path)
        if folder:
            os.makedirs(folder, exist_ok=True)

        with open(json_path, 'w') as f:
            json.dump(self.log, f, indent=4)

        pd.DataFrame(self.log).to_csv(csv_path, index=False)
        print(f"✅ Logs saved to: {json_path} and {csv_path}")

    @staticmethod
    def run(env, input_conveyor, output_conveyor, mold_count=5):
        machine = CheesePressMachine(env, input_conveyor, output_conveyor, mold_count)
        env.process(machine.press_controller())
        return machine

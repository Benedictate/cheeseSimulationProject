import simpy
import random
import json
import csv
import os
from datetime import datetime, timezone

class CurdCutterMachine:
    def __init__(self, env, input_conveyor, output_conveyor, avg_blade_wear_rate=0.1, base_auger_speed=50):
        self.env = env
        self.input_conveyor = input_conveyor
        self.output_conveyor = output_conveyor
        self.avg_blade_wear_rate = avg_blade_wear_rate
        self.base_auger_speed = base_auger_speed
        self.per_curd_logs = []
        self.batch_logs = []

    def process_batch(self):
        while True:
            batch = yield self.input_conveyor.get()
            print(f"[{self.env.now:.2f}] Starting curd cutting for batch {batch['batch_id']}")

            start_time = self.env.now
            curds = []
            total_mass = batch['total_milk_in']
            num_curds = int(total_mass * 10)  # arbitrary curd density

            total_curd = 0
            total_whey = 0
            anomalies_handled = []

            for i in range(num_curds):
                yield self.env.timeout(0.1)  # small delay per curd

                blade_sharpness = max(100 - self.avg_blade_wear_rate * i, 50)
                auger_speed = self.base_auger_speed + random.uniform(-5, 5)

                curd_mass = total_mass / num_curds * 0.9  # 90% milk to curd
                whey_mass = total_mass / num_curds * 0.1

                total_curd += curd_mass
                total_whey += whey_mass

                curd_data = {
                    'batch_id': batch['batch_id'],
                    'curd_id': f"{batch['batch_id']}_curd_{i}",
                    'blade_sharpness': round(blade_sharpness, 2),
                    'auger_speed': round(auger_speed, 2),
                    'curd_mass': round(curd_mass, 3),
                    'whey_mass': round(whey_mass, 3),
                    'anomaly_response': batch['anomalies']
                }

                self.per_curd_logs.append(self._log_per_curd(curd_data))
                yield self.output_conveyor.put(curd_data)

            end_time = self.env.now

            batch_summary = {
                'batch_id': batch['batch_id'],
                'start_time_min': start_time,
                'end_time_min': end_time,
                'total_milk_in_L': total_mass,
                'curd_yield_L': round(total_curd, 2),
                'curd_yield_%': round((total_curd / total_mass) * 100, 2),
                'whey_yield_L': round(total_whey, 2),
                'whey_yield_%': round((total_whey / total_mass) * 100, 2),
                'avg_temp_C': batch['avg_temperature'],
                'final_pH': batch['final_pH'],
                'anomalies_handled': batch['anomalies'],
                'sim_utc_timestamp': datetime.now(timezone.utc).isoformat()
            }

            self.batch_logs.append(batch_summary)
            print(f"[{self.env.now:.2f}] Finished cutting batch {batch['batch_id']}")

    def _log_per_curd(self, curd):
        return {
            'sim_time_min': self.env.now,
            'curd_id': curd['curd_id'],
            'batch_id': curd['batch_id'],
            'blade_sharpness': curd['blade_sharpness'],
            'auger_speed': curd['auger_speed'],
            'curd_mass': curd['curd_mass'],
            'whey_mass': curd['whey_mass'],
            'anomaly_response': curd['anomaly_response'],
            'utc_time': datetime.now(timezone.utc).isoformat()
        }

    def save_logs(self, folder='data/curd_cutter'):
        os.makedirs(folder, exist_ok=True)

        with open(os.path.join(folder, 'per_curd_log.json'), 'w') as f:
            json.dump(self.per_curd_logs, f, indent=4)

        with open(os.path.join(folder, 'batch_log.json'), 'w') as f:
            json.dump(self.batch_logs, f, indent=4)

        with open(os.path.join(folder, 'batch_log.csv'), 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.batch_logs[0].keys())
            writer.writeheader()
            writer.writerows(self.batch_logs)

        print(f"Logs saved to {folder}")

    @staticmethod
    def run(env, input_conveyor, output_conveyor, avg_blade_wear_rate=0.1, base_auger_speed=50):
        machine = CurdCutterMachine(env, input_conveyor, output_conveyor, avg_blade_wear_rate, base_auger_speed)
        env.process(machine.process_batch())
        return machine

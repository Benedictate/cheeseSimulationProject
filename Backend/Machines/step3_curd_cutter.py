import simpy
import random
import json
import os
from datetime import datetime, timezone
from helpers.ndjson_logger import build_standard_event

class CurdCutter:
    def __init__(self, env, input_conveyor, output_conveyor, avg_blade_wear_rate=None, base_auger_speed=None, clock=None, logger=None):
        self.env = env
        self.input_conveyor = input_conveyor
        self.output_conveyor = output_conveyor
        self.avg_blade_wear_rate = avg_blade_wear_rate
        self.base_auger_speed = base_auger_speed
        self.clock = clock() if clock else None
        self.observer = []
        self.batch_logs = []
        self.logger = logger

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

                utc_time = self.clock.now() if self.clock else datetime.now(timezone.utc).isoformat()

                self.observer.append({
                    'sim_time_min': self.env.now,
                    'utc_time': utc_time,
                    'curd_id': curd_data['curd_id'],
                    'batch_id': curd_data['batch_id'],
                    'blade_sharpness': curd_data['blade_sharpness'],
                    'auger_speed': curd_data['auger_speed'],
                    'curd_mass': curd_data['curd_mass'],
                    'whey_mass': curd_data['whey_mass'],
                    'anomaly_response': curd_data['anomaly_response'],
                    'machine': 'curd_cutter'
                })
                
                yield self.output_conveyor.put(curd_data)

            end_time = self.env.now

            utc_time = self.clock.now() if self.clock else datetime.now(timezone.utc).isoformat()

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
                'sim_utc_timestamp': utc_time
            }

            self.batch_logs.append(batch_summary)
            if self.logger:
                temp_c = batch.get('avg_temp_C', batch.get('avg_temperature', 0))
                self.logger.log_event(
                    build_standard_event(
                        machine='curd_cutter',
                        sim_time_min=self.env.now,
                        utc_time=utc_time,
                        batch_id=batch['batch_id'],
                        milk_L=total_mass,
                        curd_L=round(total_curd, 2),
                        whey_L=round(total_whey, 2),
                        pH=batch.get('final_pH', 0),
                        temperature_C=temp_c,
                        extra={'curd_yield_percent': batch_summary['curd_yield_%']},
                    )
                )
            print(f"[{self.env.now:.2f}] Finished cutting batch {batch['batch_id']}")

    def save_observations_to_json(self, filename='Backend/data/curd_cutter_data.json'):
        folder = os.path.dirname(filename)
        if folder:
            os.makedirs(folder, exist_ok=True)

        with open(filename, 'w') as f:
            json.dump(self.observer, f, indent=4)

        print(f"Observations saved to {filename}")
    
    def save_batch_logs_to_json(self, filename='Backend/data/curd_cutter_batch_data.json'):
        folder = os.path.dirname(filename)
        if folder:
            os.makedirs(folder, exist_ok=True)

        with open(filename, 'w') as f:
            json.dump(self.batch_logs, f, indent=4)

        print(f"Batch logs saved to {filename}")

    @staticmethod
    def run(env, input_conveyor, output_conveyor, clock, avg_blade_wear_rate=0.1, base_auger_speed=50, logger=None):
        machine = CurdCutter(env, input_conveyor, output_conveyor, avg_blade_wear_rate, base_auger_speed, clock, logger)
        env.process(machine.process_batch())
        return machine

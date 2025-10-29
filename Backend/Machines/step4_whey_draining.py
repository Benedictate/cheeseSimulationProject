import random
from datetime import datetime, timedelta, timezone
import simpy
import json
import os
from helpers.ndjson_logger import build_standard_event

class WheyDrainer:
    def __init__(self, env, input_store, output_store, target_moisture=None, clock=None, logger=None):
        self.env = env
        self.input_store = input_store
        self.output_store = output_store
        self.clock = clock() if clock else None
        self.target_moisture = target_moisture
        self.observer = []
        self.logger = logger

    def process(self):
        while True:
            # Get volume from input store
            total_volume = yield self.input_store.get()
            
            # Initialize curd/whey based on input volume
            INITIAL_WHEY = total_volume * 0.65
            INITIAL_CURD = total_volume - INITIAL_WHEY
            INITIAL_MOISTURE = 80.0
            DRAIN_TIME = 60
            TEMP_START = 38.0
            TEMP_END = 32.0

            curd = INITIAL_CURD
            whey_remaining = INITIAL_WHEY
            moisture = INITIAL_MOISTURE
            time_elapsed = 0
            current_time = datetime.now(timezone.utc) if not self.clock else self.clock.now(as_string=False)

            intervals = DRAIN_TIME // 5
            moisture_drop_per_interval = (INITIAL_MOISTURE - self.target_moisture) / intervals
            whey_drained_per_interval = INITIAL_WHEY / intervals

            # Print header
            print("\nWhey Draining Simulation")
            print(f"Initial Mix: {total_volume:.0f}L | Whey: {INITIAL_WHEY:.1f}L | Curd: {INITIAL_CURD:.1f}L")
            print("Time (UTC)          | Time(min) | Temp(C) | Whey Remaining(L) | Curd(L) | Moisture(%)")
            print("----------------------------------------------------------------------------------------")

            while time_elapsed <= DRAIN_TIME and moisture > self.target_moisture + 0.1:
                temp = TEMP_START - ((TEMP_START - TEMP_END) / DRAIN_TIME) * time_elapsed

                drained = min(whey_drained_per_interval * random.uniform(0.95, 1.05), whey_remaining)
                whey_remaining -= drained

                curd_loss = curd * random.uniform(0.002, 0.005)
                curd -= curd_loss

                moisture = max(self.target_moisture, moisture - moisture_drop_per_interval * random.uniform(0.95, 1.05))

                utc_time = self.clock.now() if self.clock else datetime.now(timezone.utc).isoformat()

                # Report whole minutes (integer)
                event = {
                    'sim_time_min': int(self.env.now),
                    'utc_time': utc_time,
                    'time_elapsed_min': time_elapsed,
                    'temperature_C': round(temp, 2),
                    'whey_remaining_L': round(whey_remaining, 2),
                    'curd_L': round(curd, 2),
                    'moisture_percent': round(moisture, 2),
                    'machine': 'whey_drainer'
                }
                self.observer.append(event)
                if self.logger:
                    self.logger.log_event(
                        build_standard_event(
                            machine='whey_drainer',
                            sim_time_min=event['sim_time_min'],
                            utc_time=event['utc_time'],
                            curd_L=event['curd_L'],
                            whey_L=event['whey_remaining_L'],
                            temperature_C=event['temperature_C'],
                            output_moisture_percent=event['moisture_percent'],
                        )
                    )

                # Logging
                print(f"{current_time.now()} | {time_elapsed:03d}       | {temp:7.1f} | "
                      f"{whey_remaining:12.1f}      | {curd:7.1f} | {moisture:9.1f}")

                # Advance SimPy time
                yield self.env.timeout(5)
                time_elapsed += 5

            print("\n--- Process Complete ---")
            print(f"Final Curd: {curd:.1f}L | Moisture: {moisture:.1f}%")
            print(f"Total Time: {time_elapsed-5} minutes\n")

            # Push results to output store
            batch_result = {
                'curd_final': round(curd, 2),
                'moisture_final': round(moisture, 2),
                'whey_drained': round(INITIAL_WHEY - whey_remaining, 2),
                'sim_time_min': self.env.now
            }
            yield self.output_store.put(batch_result)

    def save_observations_to_json(self, filename='Backend/data/whey_draining_data.json'):
        folder = os.path.dirname(filename)
        if folder:
            os.makedirs(folder, exist_ok=True)

        with open(filename, 'w') as f:
            json.dump(self.observer, f, indent=4)

        print(f"Observations saved to {filename}")

    @staticmethod
    def run(env, input_store, output_store, clock, target_moisture, logger=None):
        machine = WheyDrainer(env, input_store, output_store, target_moisture, clock, logger)
        env.process(machine.process())
        return machine

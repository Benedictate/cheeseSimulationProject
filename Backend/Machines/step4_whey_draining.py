import random
from datetime import datetime, timedelta, timezone
import simpy

class WheyDrainer:
    def __init__(self, env, input_store, output_store, clock, target_moisture=None):
        self.env = env
        self.input_store = input_store
        self.output_store = output_store
        self.clock = clock()
        self.target_moisture = target_moisture
        self.per_batch_logs = []

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
            current_time = self.clock.now(as_string=False)

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
            self.per_batch_logs.append(batch_result)
            yield self.output_store.put(batch_result)

    @staticmethod
    def run(env, input_store, output_store, clock, target_moisture):
        machine = WheyDrainer(env, input_store, output_store, clock, target_moisture)
        env.process(machine.process())
        return machine
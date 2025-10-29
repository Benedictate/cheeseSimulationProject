import simpy
import math
import json
import os

class Cheddaring:
    def __init__(self, env, input, output_store, clock, total_time=180, step=15, logger=None):
        self.env = env
        self.initial_curd = input
        self.output_store = output_store
        self.clock = clock()
        self.moisture_diff = 30
        self.moisture_final = 45
        self.decay_pre = -0.02
        self.decay_post = -0.025
        self.mill_start = 90
        self.sigmoid_k = -0.05
        self.texture_max = 10
        self.total_time = total_time
        self.step = step
        
        self.observer = []
        self.logger = logger

    #Moisture function 
    def moisture(self, t):
        if t < self.mill_start:  # If before milling
            return self.moisture_diff * math.exp(self.decay_pre * t) + self.moisture_final
        else:                    # If after milling
            dt = t - self.mill_start
            return self.moisture_diff * math.exp(self.decay_post * dt) + self.moisture_final

    #Texture function
    def texture(self, t):
        #Logistic (sigmoid) curve centered around milling start.
        return self.texture_max / (1 + math.exp(self.sigmoid_k * (t - self.mill_start)))

    #Main SimPy process
    def process(self):
        while True:
            batch = yield self.initial_curd.get()
            # Print initial curd mass
            print(f"Starting curd: {batch:.2f} kg\n")
            # Print table header
            print("-" * 80)
            print(f"{'Time (min)':<12} {'Moisture (%)':<15} {'Whey Lost (kg)':<20} "
                f"{'Texture (0–10)':<18} {'Milled?'}")
            print("-" * 80)

            # Loop over time steps from 0 up to total_time (inclusive)
            for t in range(0, self.total_time + 1, self.step):
                # Compute whether milling has started
                milled = "Yes" if t >= self.mill_start else "No"
                # Calculate moisture at time t
                m = self.moisture(t)
                # Calculate whey lost (kg): portion of curd that is not moisture
                whey_kg = ((100 - m) / 100) * batch
                # Calculate texture at time t
                tx = self.texture(t)

                # Report whole minutes (integer)
                event = {
                    'sim_time_min': int(self.env.now),
                    'utc_time': self.clock.now(),
                    'time_elapsed_min': t,
                    'moisture_percent': round(m, 2),
                    'whey_lost_kg': round(whey_kg, 2),
                    'texture_score': round(tx, 2),
                    'milled': milled,
                    'machine': 'cheddaring_and_milling'
                }
                self.observer.append(event)
                if self.logger:
                    from helpers.ndjson_logger import build_standard_event
                    self.logger.log_event(
                        build_standard_event(
                            machine='cheddaring_and_milling',
                            sim_time_min=event['sim_time_min'],
                            utc_time=event['utc_time'],
                            output_moisture_percent=event['moisture_percent'],
                            extra={'whey_lost_kg': event['whey_lost_kg'], 'texture_score': event['texture_score'], 'milled': milled},
                        )
                    )

                # Print one row of the table
                print(f"{t:<12} {m:<15.2f} {whey_kg:<20.2f} {tx:<18.2f} {milled}")

                # Tell SimPy to wait until the next step (advance time by `step`)
                yield self.env.timeout(self.step)
                yield self.output_store.put(batch)

    def save_observations_to_json(self, filename='Backend/data/cheddaring_and_milling_data.json'):
        folder = os.path.dirname(filename)
        if folder:
            os.makedirs(folder, exist_ok=True)

        with open(filename, 'w') as f:
            json.dump(self.observer, f, indent=4)

        print(f"Observations saved to {filename}")

    @staticmethod
    def run(env, input, output_store, clock, total_time=180, step=15, logger=None):
        machine = Cheddaring(env, input, output_store, clock, total_time, step, logger)
        env.process(machine.process())
        return machine

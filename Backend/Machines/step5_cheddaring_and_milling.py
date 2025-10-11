
import simpy # Import SimPy for discrete-event simulation
import math  # Import math for exponential and sigmoid functions


class Cheddaring:
    def __init__(self, env, input, output_store, clock, total_time=180, step=15):
        self.env = env
        self.initial_curd = input
        self.output_store = output_store
        self.clock = clock
        self.moisture_diff = 30
        self.moisture_final = 45
        self.decay_pre = -0.02
        self.decay_post = -0.025
        self.mill_start = 90
        self.sigmoid_k = -0.05
        self.texture_max = 10
        self.total_time = total_time
        self.step = step


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

                # Print one row of the table
                print(f"{t:<12} {m:<15.2f} {whey_kg:<20.2f} {tx:<18.2f} {milled}")

                # Tell SimPy to wait until the next step (advance time by `step`)
                yield self.env.timeout(self.step)
                yield self.output_store.put(batch)

    @staticmethod
    def run(env, input, output_store, clock,  total_time=180, step=15):
        machine = Cheddaring(env, input, output_store, clock, total_time, step)
        env.process(machine.process())
        return machine
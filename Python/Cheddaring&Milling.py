
import simpy  # Import SimPy for discrete-event simulation
import math  # Import math for exponential and sigmoid functions


class CheddarSim:
    def __init__(self, env):
        # Save the SimPy environment (acts as a simulation clock and scheduler)
        self.env = env

        # --- Parameters of the process ---
        self.initial_curd_kg = 10 # Starting curd mass (kg)
        self.moisture_diff = 30 # Moisture drop: 75% to 45%
        self.moisture_final = 45 # Final moisture target (%)
        self.decay_pre = -0.02 # Moisture decay rate before milling
        self.decay_post = -0.025 # Moisture decay rate after milling
        self.mill_start = 90 # Milling starts at 90 minutes
        self.sigmoid_k = -0.05 # Steepness of texture S-curve
        self.texture_max = 10 # Maximum texture score
        self.total_time = 180 # Total simulation time (minutes)
        self.step = 15 # Step size: print every 15 minutes

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
        # Print initial curd mass
        print(f"Starting curd: {self.initial_curd_kg:.2f} kg\n")
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
            whey_kg = ((100 - m) / 100) * self.initial_curd_kg
            # Calculate texture at time t
            tx = self.texture(t)

            # Print one row of the table
            print(f"{t:<12} {m:<15.2f} {whey_kg:<20.2f} {tx:<18.2f} {milled}")

            # Tell SimPy to wait until the next step (advance time by `step`)
            yield self.env.timeout(self.step)

    def run(self):

        self.env.process(self.process())
        self.env.run(until=self.total_time + self.step)

if __name__ == "__main__":

    env = simpy.Environment()
    sim = CheddarSim(env)
    sim.run()

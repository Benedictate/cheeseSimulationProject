import simpy
from datetime import datetime as dt

class CheeseRipeningSimulation:
    # --- Simulation Constants ---
    TOTAL_CHEESE = 108  # Total cheese to process (kilograms)
    INTAKE_PER_STEP = 27  # Weight of one block

    # --- Temperature Thresholds (°C) ---
    TEMP_MIN_OPERATING = 3     # Lowest temp for intake
    TEMP_OPTIMAL_MIN = 7       # Minimum temp to ripen
    TEMP_OPTIMAL = 10          # Optimal temp to ripen
    TEMP_OPTIMAL_MAX = 13      # Maximum temp to ripen
    TEMP_RUINED_THRESHOLD = 17 # Temp at which cheese is ruined

    # --- Step Calculations ---
    STEP_DURATION_SEC = 15
    STEPS_PER_MIN = 60 // STEP_DURATION_SEC

    # --- Temperature Adjustment ---
    TEMP_DROP_PER_STEP = 1     # Cooling rate per step
    TEMP_RISE_WHEN_COLD = 1.5  # Reheating rate per step

    def __init__(self, incoming_blocks=None, initial_temp=None):
        self.incoming_blocks = incoming_blocks or self.TOTAL_CHEESE
        self.initial_temp = initial_temp or self.TEMP_OPTIMAL
        self.env = simpy.Environment()

    @staticmethod
    def format_sim_time(sim_time):
        """Convert sim time steps to MM:SS format."""
        total_seconds = sim_time * CheeseRipeningSimulation.STEP_DURATION_SEC
        return f"{int(total_seconds // 60)}:{int(total_seconds % 60):02d}"

    def ripening_process(self):
        # Storage state variables
        ripening = 0
        intake = self.incoming_blocks

        # Machine state variables
        temperature = self.initial_temp
        status = "Adding pressed cheeses to shelves..."

        # Header
        print(f"{'Time':<8}                   {'Intake (KG)':<14} {'Ripening (KG)':<14}{'Temp (°C)':<10} Status")
        print("-" * 95)

        # Processing loop
        while (intake > 0) and (ripening < self.TOTAL_CHEESE):
            yield self.env.timeout(self.STEP_DURATION_SEC)

            intake -= self.INTAKE_PER_STEP
            ripening += self.INTAKE_PER_STEP

            print(f"{dt.now()} {intake:<14.2f} {ripening:<14.2f} {temperature:<10.2f} {status}")

        # Final report
        stored_blocks = ripening
        print("\n--- Simulation Complete ---")
        print(f"Remaining - Incoming Block count: {self.incoming_blocks / 27}")
        print(f"Remaining - Stored Blocks count: {stored_blocks / 27} or {stored_blocks}kg")
        if temperature > self.TEMP_OPTIMAL_MAX:
            print("The Cheese did not ripen properly")
        elif temperature > self.TEMP_OPTIMAL_MIN:
            print("The Cheese took 12 months to ripen.")
        elif temperature >= self.TEMP_MIN_OPERATING:
            print("The Cheese took 18 months to ripen.")
        elif temperature < self.TEMP_MIN_OPERATING:
            print("The Cheese took too long to ripen.")

    def run(self, until=500):
        self.env.process(self.ripening_process())
        self.env.run(until=until)


if __name__ == "__main__":
    sim = CheeseRipeningSimulation()
    sim.run()
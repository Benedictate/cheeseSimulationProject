import simpy
import random

class Pasteurisation:
    def __init__(self):
        # --- Simulation Constants ---
        self.TOTAL_MILK = 1000  # Total milk to process (liters)
        self.FLOW_RATE_PER_STEP = 41.7  # Liters per 15 seconds
        self.TEMP_RANGE_VARIATION = (-2, 2)  # Random fluctuation range per step

        # --- Temperature Thresholds (°C) ---
        self.TEMP_MIN_OPERATING = 68 #lowest temperature at which the machine would draw milk in
        self.TEMP_OPTIMAL_MIN = 70 #minimum temp to pasteurise the milk
        self.TEMP_OPTIMAL = 72 #optimal temp to pasteurise milk
        self.TEMP_OPTIMAL_MAX = 74 #maximum temp to pasteurise milk
        self.TEMP_BURN_THRESHOLD = 77 #temp at which milk would be burnt

        # --- Time Durations (minutes) ---
        self.STARTUP_DURATION = 5 #amount of minutes it would take to start the machine up
        self.RUNTIME_LIMIT = 60 #amount of time the machine would run for (65 in total with 5 minute startup)
        self.COOLDOWN_DURATION = 60 #machine would need to cool down for 60
        self.MACHINE_OVERHEAT_COOLING_TIME = 2 #amount of time it would take to cool the machine down after it went above 77 deg

        # --- Step Calculations (each step = 15 seconds) ---
        self.STEP_DURATION_SEC = 15 #set each simulation step to 15 seconds
        self.STEPS_PER_MIN = 60 // self.STEP_DURATION_SEC #how many steps per 1 min (60 sec)
        self.STEPS_STARTUP = self.STARTUP_DURATION * self.STEPS_PER_MIN 
        self.STEPS_RUNTIME_LIMIT = self.RUNTIME_LIMIT * self.STEPS_PER_MIN #How many steps overall
        self.STEPS_COOLDOWN = self.COOLDOWN_DURATION * self.STEPS_PER_MIN 
        self.STEPS_OVERHEAT_COOLING = self.MACHINE_OVERHEAT_COOLING_TIME * self.STEPS_PER_MIN

        # --- Temperature Adjustment ---
        self.TEMP_DROP_PER_STEP = 1  # Machine cools this much each step during cooldown
        self.TEMP_RISE_WHEN_COLD = 1.5  # Increase temp if too cold (reheating simulation)

    def format_sim_time(self, sim_time):
        """Convert sim time to MM:SS format."""
        total_seconds = sim_time * self.STEP_DURATION_SEC
        return f"{int(total_seconds // 60)}:{int(total_seconds % 60):02d}"

    def run(self):
        """Main method that runs the HTST pasteurization simulation (equivalent to original run_htst_sim function)"""
        env = simpy.Environment()
        env.process(self.htst_process(env, self.TOTAL_MILK, self.FLOW_RATE_PER_STEP, self.TEMP_OPTIMAL))
        env.run(until=500)

    def htst_process(self, env, total_milk, flow_per_step, initial_temp):
        """HTST pasteurizer simulation logic."""
        # Tank state variables
        start_tank = total_milk
        balance_tank = 0.0
        pasteurized = 0.0
        burnt = 0.0

        # Machine state variables
        temperature = initial_temp
        run_time_steps = 0
        cooldown_scheduled = False
        cooling_due_to_overheat = False

        # Header
        print(f"{'Time':<8} {'Start Tank (L)':<14} {'Balance Tank (L)':<14} {'Pasteurized (L)':<14} {'Burnt (L)':<14} {'Temp (°C)':<10} Status")
        print("-" * 95)

        # --- Startup Phase ---
        for _ in range(self.STEPS_STARTUP):
            print(f"{self.format_sim_time(env.now):<8} {start_tank:<14.2f} {balance_tank:<14.2f} {pasteurized:<14.2f} {burnt:<14.2f} {temperature:<10.2f} Startup / Heating")
            yield env.timeout(1)

        # --- Processing Loop ---
        while (start_tank + balance_tank > 0) and (pasteurized + burnt < total_milk):

            # Scheduled cooldown
            if cooldown_scheduled:
                print(f"{self.format_sim_time(env.now):<8} {start_tank:<14.2f} {balance_tank:<14.2f} {pasteurized:<14.2f} {burnt:<14.2f} {temperature:<10.2f} Scheduled Cooldown")
                yield env.timeout(self.STEPS_COOLDOWN)
                run_time_steps = 0
                cooldown_scheduled = False
                continue

            if run_time_steps >= self.STEPS_RUNTIME_LIMIT:
                cooldown_scheduled = True
                continue

            # Overheat cooling phase
            if cooling_due_to_overheat:
                temperature -= self.TEMP_DROP_PER_STEP
                print(f"{self.format_sim_time(env.now):<8} {start_tank:<14.2f} {balance_tank:<14.2f} {pasteurized:<14.2f} {burnt:<14.2f} {temperature:<10.2f} Cooling after Overheat")
                yield env.timeout(1)
                run_time_steps += 1

                if temperature <= self.TEMP_OPTIMAL:
                    cooling_due_to_overheat = False
                    print(f"{self.format_sim_time(env.now):<8} {start_tank:<14.2f} {balance_tank:<14.2f} {pasteurized:<14.2f} {burnt:<14.2f} {temperature:<10.2f} Cooled - Resuming")
                continue

            # Choose tank source
            if start_tank > 0:
                source = "Start Tank"
                available = start_tank
            elif balance_tank > 0:
                source = "Balance Tank"
                available = balance_tank
            else:
                break

            milk_this_step = min(flow_per_step, available)

            # --- Milk Processing ---
            if temperature >= self.TEMP_BURN_THRESHOLD:
                # Burnt due to overheat
                if source == "Start Tank":
                    start_tank -= milk_this_step
                else:
                    balance_tank -= milk_this_step

                burnt += milk_this_step
                cooling_due_to_overheat = True
                status = f"Burnt milk! {milk_this_step:.2f}L"
            
            elif temperature < self.TEMP_OPTIMAL_MIN:
                # Too cold — recirculate and reheat
                if source == "Start Tank":
                    start_tank -= milk_this_step
                else:
                    balance_tank -= milk_this_step

                balance_tank += milk_this_step
                temperature += self.TEMP_RISE_WHEN_COLD  # Reheating
                status = f"Too cold - recirculating {milk_this_step:.2f}L and reheating"

            elif self.TEMP_OPTIMAL_MIN <= temperature <= self.TEMP_OPTIMAL_MAX:
                # Optimal range — pasteurize
                if source == "Start Tank":
                    start_tank -= milk_this_step
                else:
                    balance_tank -= milk_this_step

                pasteurized += milk_this_step
                status = f"Pasteurized from {source}"

            else:
                # Slightly hot — recirculate
                if source == "Start Tank":
                    start_tank -= milk_this_step
                else:
                    balance_tank -= milk_this_step

                balance_tank += milk_this_step
                status = f"Too hot - recirculating {milk_this_step:.2f}L"

            print(f"{self.format_sim_time(env.now):<8} {start_tank:<14.2f} {balance_tank:<14.2f} {pasteurized:<14.2f} {burnt:<14.2f} {temperature:<10.2f} {status}")

            # Random temp fluctuation
            temperature += random.uniform(*self.TEMP_RANGE_VARIATION)
            yield env.timeout(1)
            run_time_steps += 1

        # --- Final Report ---
        total_out = pasteurized + burnt
        print("\n--- Simulation Complete ---")
        print(f"Total processed: {total_out:.2f}L")
        print(f"Pasteurized: {pasteurized:.2f}L ({pasteurized/total_milk*100:.1f}%)")
        print(f"Burnt: {burnt:.2f}L ({burnt/total_milk*100:.1f}%)")
        print(f"Remaining - Start Tank: {start_tank:.2f}L")
        print(f"Remaining - Balance Tank: {balance_tank:.2f}L")


# Start of HTST pasteurization simulation
if __name__ == "__main__":
    pasteurizer = Pasteurisation()
    pasteurizer.run()

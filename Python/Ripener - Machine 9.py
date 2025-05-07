import simpy
import random

# --- Simulation Constants ---
TOTAL_MILK = 1000  # Total milk to process (liters)
FLOW_RATE_PER_STEP = 41.7  # Liters per 15 seconds
TEMP_RANGE_VARIATION = (-2, 2)  # Random fluctuation range per step

# --- Temperature Thresholds (°C) ---
TEMP_MIN_OPERATING = 68 #lowest temperature at which the machine would draw milk in
TEMP_OPTIMAL_MIN = 70 #minimum temp to pasteurise the milk
TEMP_OPTIMAL = 72 #optimal temp to pasteurise milk
TEMP_OPTIMAL_MAX = 74 #maximum temp to pasteurise milk
TEMP_BURN_THRESHOLD = 77 #temp at which milk would be burnt

# --- Time Durations (minutes) ---
STARTUP_DURATION = 5 #amount of minutes it would take to start the machine up
RUNTIME_LIMIT = 60 #amount of time the machine would run for (65 in total with 5 minute startup)
COOLDOWN_DURATION = 60 #machine would need to cool down for 60
MACHINE_OVERHEAT_COOLING_TIME = 2 #amount of time it would take to cool the machine down after it went above 77 deg

# --- Step Calculations (each step = 15 seconds) ---
STEP_DURATION_SEC = 15 #set each simulation step to 15 seconds
STEPS_PER_MIN = 60 // STEP_DURATION_SEC #how many steps per 1 min (60 sec)
STEPS_STARTUP = STARTUP_DURATION * STEPS_PER_MIN 
STEPS_RUNTIME_LIMIT = RUNTIME_LIMIT * STEPS_PER_MIN #How many steps overall
STEPS_COOLDOWN = COOLDOWN_DURATION * STEPS_PER_MIN 
STEPS_OVERHEAT_COOLING = MACHINE_OVERHEAT_COOLING_TIME * STEPS_PER_MIN

# --- Temperature Adjustment ---
TEMP_DROP_PER_STEP = 1  # Machine cools this much each step during cooldown
TEMP_RISE_WHEN_COLD = 1.5  # Increase temp if too cold (reheating simulation)


#to return a time value for the amount of time passed per step (in the format of 0:15, 0:30 etc)
def format_sim_time(sim_time):
    """Convert sim time to MM:SS format."""
    total_seconds = sim_time * STEP_DURATION_SEC
    return f"{int(total_seconds // 60)}:{int(total_seconds % 60):02d}"

def ripening_process(env, incoming_blocks, flow_per_step, initial_temp):

    # storage state variables
    stored_blocks = 0
    incoming_blocks = 0

    # Machine state variables
    temperature = initial_temp
    run_time_steps = 0
    cooldown_scheduled = False

    # Header
    print(f"{'Time':<8} {'Start Tank (L)':<14} {'Balance Tank (L)':<14} {'Pasteurized (L)':<14} {'Burnt (L)':<14} {'Temp (°C)':<10} Status")
    print("-" * 95)

    # --- Startup Phase ---
    for _ in range(STEPS_STARTUP):
        print(f"{format_sim_time(env.now):<8} {start_tank:<14.2f} {balance_tank:<14.2f} {pasteurized:<14.2f} {burnt:<14.2f} {temperature:<10.2f} Startup / Heating")
        yield env.timeout(1)

    # --- Processing Loop ---
    while (start_tank + balance_tank > 0) and (pasteurized + burnt < total_milk):

        # Scheduled cooldown
        if cooldown_scheduled:
            print(f"{format_sim_time(env.now):<8} {start_tank:<14.2f} {balance_tank:<14.2f} {pasteurized:<14.2f} {burnt:<14.2f} {temperature:<10.2f} Scheduled Cooldown")
            yield env.timeout(STEPS_COOLDOWN)
            run_time_steps = 0
            cooldown_scheduled = False
            continue

        if run_time_steps >= STEPS_RUNTIME_LIMIT:
            cooldown_scheduled = True
            continue

        # Overheat cooling phase
        if cooling_due_to_overheat:
            temperature -= TEMP_DROP_PER_STEP
            print(f"{format_sim_time(env.now):<8} {start_tank:<14.2f} {balance_tank:<14.2f} {pasteurized:<14.2f} {burnt:<14.2f} {temperature:<10.2f} Cooling after Overheat")
            yield env.timeout(1)
            run_time_steps += 1

            if temperature <= TEMP_OPTIMAL:
                cooling_due_to_overheat = False
                print(f"{format_sim_time(env.now):<8} {start_tank:<14.2f} {balance_tank:<14.2f} {pasteurized:<14.2f} {burnt:<14.2f} {temperature:<10.2f} Cooled - Resuming")
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
        if temperature >= TEMP_BURN_THRESHOLD:
            # Burnt due to overheat
            if source == "Start Tank":
                start_tank -= milk_this_step
            else:
                balance_tank -= milk_this_step

            burnt += milk_this_step
            cooling_due_to_overheat = True
            status = f"Burnt milk! {milk_this_step:.2f}L"
        
        elif temperature < TEMP_OPTIMAL_MIN:
            # Too cold — recirculate and reheat
            if source == "Start Tank":
                start_tank -= milk_this_step
            else:
                balance_tank -= milk_this_step

            balance_tank += milk_this_step
            temperature += TEMP_RISE_WHEN_COLD  # Reheating
            status = f"Too cold - recirculating {milk_this_step:.2f}L and reheating"

        elif TEMP_OPTIMAL_MIN <= temperature <= TEMP_OPTIMAL_MAX:
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

        print(f"{format_sim_time(env.now):<8} {start_tank:<14.2f} {balance_tank:<14.2f} {pasteurized:<14.2f} {burnt:<14.2f} {temperature:<10.2f} {status}")

        # Random temp fluctuation
        temperature += random.uniform(*TEMP_RANGE_VARIATION)
        yield env.timeout(1)
        run_time_steps += 1

    # --- Final Report ---
    total_out = pasteurized + burnt
    print("\n--- Simulation Complete ---")
    print(f"Remaining - Incoming Block count: {incoming_blocks}")
    print(f"Remaining - Stored Blocks count: {stored_blocks}")

def run_htst_sim():
    """Initialize and run the simulation."""
    env = simpy.Environment()
    env.process(htst_process(env, TOTAL_MILK, FLOW_RATE_PER_STEP, TEMP_OPTIMAL))
    env.run(until=500)

if __name__ == "__main__":
    run_htst_sim()

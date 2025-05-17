import simpy
import random

# --- Simulation Constants ---
TOTAL_CHEESE = 108  # Total cheese to process (kilograms)
INTAKE_PER_STEP = 27  # Weight of one block

# --- Temperature Thresholds (°C) ---
TEMP_MIN_OPERATING = 3 #lowest temperature at which the machine would intake cheese blocks in
TEMP_OPTIMAL_MIN = 7 #minimum temp to ripen the cheese
TEMP_OPTIMAL = 10 #optimal temp to ripen cheese
TEMP_OPTIMAL_MAX = 13 #maximum temp to ripen cheese
TEMP_RUNIED_THRESHOLD = 17 #temp at which cheese would be burnt

# --- Step Calculations (each step = 15 seconds) ---
STEP_DURATION_SEC = 15 #set each simulation step to 15 seconds
STEPS_PER_MIN = 60 // STEP_DURATION_SEC #how many steps per 1 min (60 sec)

# --- Temperature Adjustment ---
TEMP_DROP_PER_STEP = 1  # Machine cools this much each step during cooldown
TEMP_RISE_WHEN_COLD = 1.5  # Increase temp if too cold (reheating simulation)


#to return a time value for the amount of time passed per step (in the format of 0:15, 0:30 etc)
def format_sim_time(sim_time):
    """Convert sim time to MM:SS format."""
    total_seconds = sim_time * STEP_DURATION_SEC
    return f"{int(total_seconds // 60)}:{int(total_seconds % 60):02d}"

def ripening_process(env, incoming_blocks, initial_temp):

    # storage state variables
    ripening = 0
    intake = incoming_blocks

    # Machine state variables
    temperature = initial_temp
    status = "Adding pressed cheeses to shelves..."

    # Header
    print(f"{'Time':<8} {'Intake (KG)':<14} {'Ripening (KG)':<14}{'Temp (°C)':<10} Status")
    print("-" * 65)

    # --- Processing Loop ---
    while (intake > 0) and (ripening < TOTAL_CHEESE):

        yield env.timeout(STEP_DURATION_SEC)

        intake -= INTAKE_PER_STEP
        ripening += INTAKE_PER_STEP


        print(f"{format_sim_time(env.now):<8} {intake:<14.2f} {ripening:<14.2f} {temperature:<10.2f} {status}")


    # --- Final Report ---
    stored_blocks = ripening
    print("\n--- Simulation Complete ---")
    print(f"Remaining - Incoming Block count: {incoming_blocks / 27}")
    print(f"Remaining - Stored Blocks count: {stored_blocks / 27} or {stored_blocks}kg")
    if temperature > TEMP_OPTIMAL_MAX:
        print ("The Cheese did not ripen properly")
    elif temperature > TEMP_OPTIMAL_MIN:
        print ("The Cheese took 12 months to ripen.")
    elif temperature >= TEMP_MIN_OPERATING:
        print ("The Cheese took 18 months to ripen.")
    elif temperature < TEMP_MIN_OPERATING:
        print ("The Cheese took too long to ripen.")


    

def run_htst_sim():
    """Initialize and run the simulation."""
    env = simpy.Environment()
    env.process(ripening_process(env, TOTAL_CHEESE, TEMP_OPTIMAL))
    env.run(until=500)

if __name__ == "__main__":
    run_htst_sim()

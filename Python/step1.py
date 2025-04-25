import simpy
import random

# Constants
TOTAL_MILK_LITERS = 1000
FLOW_PER_15_SEC = 41.7  # Liters per 15 seconds at optimal temperature
OPTIMAL_TEMP_MIN = 70  # Minimum acceptable temperature
OPTIMAL_TEMP = 72      # Target temperature
OPTIMAL_TEMP_MAX = 74  # Maximum acceptable temperature
TEMP_VARIATION_RANGE = (-3, 3)
BURN_TEMP = 77
MIN_TEMP = 68
STARTUP_TIME_MINUTES = 5
RUNTIME_LIMIT_MINUTES = 240
COOLDOWN_DURATION_MINUTES = 60
MACHINE_COOLING_MINUTES = 3  # Time for machine to cool down after overheating
COOLING_RATE_PER_STEP = 0.5  # Temperature reduction per 15-second step during cooling

# Convert all timing to 15-second steps
SECONDS_PER_STEP = 15
STEPS_PER_MINUTE = 60 // SECONDS_PER_STEP
STARTUP_STEPS = STARTUP_TIME_MINUTES * STEPS_PER_MINUTE
RUNTIME_LIMIT_STEPS = RUNTIME_LIMIT_MINUTES * STEPS_PER_MINUTE
COOLDOWN_DURATION_STEPS = COOLDOWN_DURATION_MINUTES * STEPS_PER_MINUTE
MACHINE_COOLING_STEPS = MACHINE_COOLING_MINUTES * STEPS_PER_MINUTE


def format_time(sim_time):
    """Convert simulation time steps to minutes:seconds format."""
    total_seconds = sim_time * SECONDS_PER_STEP
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{int(minutes)}:{int(seconds):02d}"


def htst_pasteurizer(env, total_milk_liters, flow_per_step, temperature):
    """
    Simulate a High-Temperature Short-Time (HTST) pasteurizer with multiple tanks.
    
    Args:
        env: SimPy environment
        total_milk_liters: Initial amount of milk in the start tank
        flow_per_step: Flow rate per 15-second step at optimal temperature
        temperature: Initial temperature
    """
    # Tank levels
    milk_in_start_tank = total_milk_liters
    milk_in_balance_tank = 0.0
    pasteurized_milk = 0.0
    burnt_milk = 0.0
    
    # Machine state
    machine_cooling = False
    current_temp = temperature
    runtime_counter = 0
    cooldown = False

    # Print header
    print(f"{'Time':<8} {'Start Tank (L)':<15} {'Balance Tank (L)':<15} {'Pasteurised (L)':<15} {'Burnt (L)':<15} {'Temp (°C)':<10} {'Status'}")
    print("-" * 110)

    # Startup Phase
    for step in range(STARTUP_STEPS):
        print(f"{format_time(env.now):<8} {milk_in_start_tank:<15.2f} {milk_in_balance_tank:<15.2f} {pasteurized_milk:<15.2f} {burnt_milk:<15.2f} {current_temp:<10.2f} Startup / Heating")
        yield env.timeout(1)

    # Main processing loop
    while (milk_in_start_tank + milk_in_balance_tank > 0) and (pasteurized_milk + burnt_milk < total_milk_liters):
        # Check if we need a scheduled cooldown
        if cooldown:
            print(f"{format_time(env.now):<8} {milk_in_start_tank:<15.2f} {milk_in_balance_tank:<15.2f} {pasteurized_milk:<15.2f} {burnt_milk:<15.2f} {current_temp:<10.2f} Scheduled Cooling Down")
            yield env.timeout(COOLDOWN_DURATION_STEPS)
            runtime_counter = 0
            cooldown = False
            continue

        if runtime_counter >= RUNTIME_LIMIT_STEPS:
            cooldown = True
            continue

        # Handle machine cooling after overheating
        if machine_cooling:
            current_temp -= COOLING_RATE_PER_STEP
            cooling_status = f"Machine cooling down - Temp: {current_temp:.2f}°C"
            print(f"{format_time(env.now):<8} {milk_in_start_tank:<15.2f} {milk_in_balance_tank:<15.2f} {pasteurized_milk:<15.2f} {burnt_milk:<15.2f} {current_temp:<10.2f} {cooling_status}")
            
            yield env.timeout(1)
            runtime_counter += 1
            
            # Check if machine has cooled down enough to resume operation
            if current_temp <= OPTIMAL_TEMP:
                machine_cooling = False
                print(f"{format_time(env.now):<8} {milk_in_start_tank:<15.2f} {milk_in_balance_tank:<15.2f} {pasteurized_milk:<15.2f} {burnt_milk:<15.2f} {current_temp:<10.2f} Machine cooled down - resuming operation")
            continue

        # Determine which tank to draw milk from
        if milk_in_start_tank > 0:
            source_tank = "Start Tank"
            available_milk = milk_in_start_tank
        elif milk_in_balance_tank > 0:
            source_tank = "Balance Tank"
            available_milk = milk_in_balance_tank
        else:
            break  # No more milk to process

        # Calculate how much milk to process in this step
        milk_to_process = min(flow_per_step, available_milk)
        
        # Process the milk based on temperature
        if current_temp >= BURN_TEMP:
            # Temperature too high - milk gets burnt
            if source_tank == "Start Tank":
                milk_in_start_tank -= milk_to_process
            else:
                milk_in_balance_tank -= milk_to_process
                
            burnt_milk += milk_to_process
            machine_cooling = True
            status = f"TEMP {current_temp:.2f}°C — Milk burnt! Adding {milk_to_process:.2f}L to burnt milk tank"
            
        elif current_temp < MIN_TEMP or current_temp < OPTIMAL_TEMP_MIN:
            # Temperature too low - recirculate to balance tank
            if source_tank == "Start Tank":
                milk_in_start_tank -= milk_to_process
            else:
                milk_in_balance_tank -= milk_to_process
                
            milk_in_balance_tank += milk_to_process  # Add to balance tank
            status = f"TEMP {current_temp:.2f}°C — Too cold, recirculating to balance tank"
            
        elif OPTIMAL_TEMP_MIN <= current_temp <= OPTIMAL_TEMP_MAX:
            # Temperature optimal - pasteurize the milk
            if source_tank == "Start Tank":
                milk_in_start_tank -= milk_to_process
            else:
                milk_in_balance_tank -= milk_to_process
                
            pasteurized_milk += milk_to_process
            status = f"Optimal temperature - Pasteurizing from {source_tank}"
            
        else:  # Temperature too high but below burn temp
            # Temperature too high - recirculate to balance tank
            if source_tank == "Start Tank":
                milk_in_start_tank -= milk_to_process
            else:
                milk_in_balance_tank -= milk_to_process
                
            milk_in_balance_tank += milk_to_process  # Add to balance tank
            status = f"TEMP {current_temp:.2f}°C — Too high, recirculating to balance tank"

        # Print current status
        print(f"{format_time(env.now):<8} {milk_in_start_tank:<15.2f} {milk_in_balance_tank:<15.2f} {pasteurized_milk:<15.2f} {burnt_milk:<15.2f} {current_temp:<10.2f} {status}")

        # Temperature fluctuation
        temp_variation = random.uniform(*TEMP_VARIATION_RANGE)
        current_temp += temp_variation

        yield env.timeout(1)
        runtime_counter += 1

    # Final summary
    total_processed = pasteurized_milk + burnt_milk
    print("\nSimulation Complete - Final Results:")
    print(f"Total milk processed: {total_processed:.2f} liters")
    print(f"Successfully pasteurized: {pasteurized_milk:.2f} liters ({pasteurized_milk/total_milk_liters*100:.1f}%)")
    print(f"Burnt: {burnt_milk:.2f} liters ({burnt_milk/total_milk_liters*100:.1f}%)")
    print(f"Remaining in start tank: {milk_in_start_tank:.2f} liters")
    print(f"Remaining in balance tank: {milk_in_balance_tank:.2f} liters")


# Run the simulation
def run_simulation():
    """Run the HTST pasteurizer simulation."""
    env = simpy.Environment()
    env.process(htst_pasteurizer(env, TOTAL_MILK_LITERS, FLOW_PER_15_SEC, OPTIMAL_TEMP))
    env.run(until=500)  # Run for longer to ensure all milk is processed


if __name__ == "__main__":
    run_simulation()

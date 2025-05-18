import sympy as sp 

time = sp.Symbol('time')

#Constants
INITIAL_CURD_KG = 10
MOISTURE_DIFFERENCE = 30
FINAL_MOISTURE = 45 #normally cheese is left with 45% moisture and starts with 75% moisture
DECAY_RATE_PRE_MILL = -0.02
DECAY_RATE_POST_MILL = -0.025
MILLING_START_TIME =90
SIGMOID_STEEPNESS =-0.05 #affects how fast cheese goes from soft to firm
MAX_TEXTURE =10


#Moisture decay formulas(one for rate before milling and one for after)
MOISTURE_BEFORE = MOISTURE_DIFFERENCE * sp.exp(DECAY_RATE_PRE_MILL * time) + FINAL_MOISTURE
MOISTURE_AFTER = MOISTURE_DIFFERENCE * sp.exp(DECAY_RATE_POST_MILL = -0.025
 * (time - MILLING_START_TIME)) + FINAL_MOISTURE

#Texture formula (sigmoid function centered at 90)
TEXTURE_EXPR = MAX_TEXTURE / (1 + sp.exp(SIGMOID_STEEPNESS * (time - MILLING_START_TIME)))

#Time points from 0 to 180 in 15-min steps as the cheese is normally checked every 15 minutes
TIME_POINTS = list(range(0, 181, 15))

def cheddaring_process(env, curd_input, flow_per_step, initial_temp):
    """HTST pasteurizer simulation logic."""
  

    # Machine state variables
    curd_to_process = curd_input
    temperature = initial_temp
   
    # Header
    print(f"Starting curd: {curd_input:.2f} kg\n")
    print("-" * 80)
    print(f"{'Time (min)':<12} {'Moisture (%)':<15} {'Whey Lost (kg)':<20} {'Texture (0–10)':<18} {'Milled?'}")
    print("-" * 80)

    # --- Startup Phase ---
    for _ in range(STEPS_STARTUP):
        print(f"{format_sim_time(env.now):<8} {start_tank:<14.2f} {balance_tank:<14.2f} {pasteurized:<14.2f} {burnt:<14.2f} {temperature:<10.2f} Startup / Heating")
        yield env.timeout(1)

    # --- Processing Loop ---
    while (start_tank + balance_tank > 0) and (pasteurized + burnt < total_milk):

        # Loop through 15 min timestamps
        for t in TIME_POINTS:
            milled = t >= MILLING_START_TIME
            if not milled:
                moisture = MOISTURE_BEFORE.subs(time, t)
            else:
                moisture = MOISTURE_AFTER.subs(time, t)

            moisture = float(moisture.evalf())

            #calculating wheylost based on moisture
            whey_kg = ((100 - moisture) / 100) * INITIAL_CURD_KG

            #calculating texture
            texture = float(texture_expr.subs(time, t).evalf())

            print(f"{t:<12} {moisture:<15.2f} {whey_kg:<20.2f} {texture:<18.2f} {'Yes' if milled else 'No'}")



    # --- Final Report ---
    total_out = pasteurized + burnt
    print("\n--- Simulation Complete ---")
    print(f"Total processed: {total_out:.2f}L")
    print(f"Pasteurized: {pasteurized:.2f}L ({pasteurized/total_milk*100:.1f}%)")
    print(f"Burnt: {burnt:.2f}L ({burnt/total_milk*100:.1f}%)")
    print(f"Remaining - Start Tank: {start_tank:.2f}L")
    print(f"Remaining - Balance Tank: {balance_tank:.2f}L")

def run_cheddaring_sim():
    """Initialize and run the simulation."""
    env = simpy.Environment()
    env.process(cheddaring_process(env, INITIAL_CURD_KG, FLOW_RATE_PER_STEP, TEMP_OPTIMAL))
    env.run(until=500)

if __name__ == "__main__":
    run_cheddaring_sim()




# Loop through 15 min timestamps
for t in TIME_POINTS:
    milled = t >= MILLING_START_TIME
    if not milled:
        moisture = MOISTURE_BEFORE.subs(time, t)
    else:
        moisture = MOISTURE_AFTER.subs(time, t)

    moisture = float(moisture.evalf())

    #calculating wheylost based on moisture
    whey_kg = ((100 - moisture) / 100) * INITIAL_CURD_KG

    #calculating texture
    texture = float(texture_expr.subs(time, t).evalf())

    print(f"{t:<12} {moisture:<15.2f} {whey_kg:<20.2f} {texture:<18.2f} {'Yes' if milled else 'No'}")


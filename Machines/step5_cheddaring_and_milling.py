import simpy
import math

# Constants
INITIAL_CURD_KG = 10
MOISTURE_DIFFERENCE = 30
MOISTURE_FINAL = 45  # from 75% to 45%
DECAY_RATE_PRE_MILL = -0.02
DECAY_RATE_POST_MILL = -0.025
MILL_START_TIME = 90
SIGMOID_STEEPNESS = -0.05
MAXIMUM_TEXTURE = 10
TOTAL_PROCESS_TIME=180

# Functions for moisture and texture
def calculate_moisture(t):
    if t < MILL_START_TIME:
        return MOISTURE_DIFFERENCE * math.exp(DECAY_RATE_PRE_MILL * t) + MOISTURE_FINAL
    else:
        return MOISTURE_DIFFERENCE * math.exp(DECAY_RATE_POST_MILL * (t - MILL_START_TIME)) + MOISTURE_FINAL

def calculate_texture(t):
    return MAXIMUM_TEXTURE / (1 + math.exp(SIGMOID_STEEPNESS * (t - MILL_START_TIME)))

def cheddaring_process(env, initial_curd_amount, milling_startup, process_time):
    print(f"Starting curd: {initial_curd_amount:.2f} kg\n")
    print("-" * 80)
    print(f"{'Time (min)':<12} {'Moisture (%)':<15} {'Whey Lost (kg)':<20} {'Texture (0–10)':<18} {'Milled?'}")
    print("-" * 80)

    while env.now <= process_time:
        t = env.now
        milled = t >= milling_startup

        moisture = calculate_moisture(t)
        whey_kg = ((100 - moisture) / 100) * initial_curd_amount
        texture = calculate_texture(t)

        print(f"{t:<12} {moisture:<15.2f} {whey_kg:<20.2f} {texture:<18.2f} {'Yes' if milled else 'No'}")

        yield env.timeout(15)  # 15-minute intervals

# Run simulation
env = simpy.Environment()
env.process(cheddaring_process(env, INITIAL_CURD_KG, MILL_START_TIME, TOTAL_PROCESS_TIME))
env.run()
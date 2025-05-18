import simpy
import math

# Constants
initial_curd_kg = 10
moisture_difference = 30
final_moisture = 45  # from 75% to 45%
decay_rate_before_milling = -0.02
decay_rate_after_milling = -0.025
milling_start_time = 90
steepness_of_sigmoid = -0.05
max_texture_value = 10
total_time_of_process=180

# Functions for moisture and texture
def calculate_moisture(t):
    if t < milling_start_time:
        return moisture_difference * math.exp(decay_rate_before_milling * t) + final_moisture
    else:
        return moisture_difference * math.exp(decay_rate_after_milling * (t - milling_start_time)) + final_moisture

def calculate_texture(t):
    return max_texture_value / (1 + math.exp(steepness_of_sigmoid * (t - milling_start_time)))

def cheddaring_process(env):
    print(f"Starting curd: {initial_curd_kg:.2f} kg\n")
    print("-" * 80)
    print(f"{'Time (min)':<12} {'Moisture (%)':<15} {'Whey Lost (kg)':<20} {'Texture (0–10)':<18} {'Milled?'}")
    print("-" * 80)

    while env.now <= total_time_of_process:
        t = env.now
        milled = t >= milling_start_time

        moisture = calculate_moisture(t)
        whey_kg = ((100 - moisture) / 100) * initial_curd_kg
        texture = calculate_texture(t)

        print(f"{t:<12} {moisture:<15.2f} {whey_kg:<20.2f} {texture:<18.2f} {'Yes' if milled else 'No'}")

        yield env.timeout(15)  # 15-minute intervals

# Run simulation
env = simpy.Environment()
env.process(cheddaring_process(env))
env.run()

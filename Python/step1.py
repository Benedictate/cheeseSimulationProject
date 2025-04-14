import simpy
import random

# Global Variables
TotalStartingMilk = 1000
BaseFlowRate = 15
Temperature = 72

def pasteurization_process(env, total_milk_liters, base_rate, temperature):
    pasteurized = 0.0
    current_temp = temperature  # Initial base temperature

    print(f"{'Minute':<6} {'Start Milk (L)':<18} {'Pasteurised (L)':<18} {'Variance/Anomalies'}")
    print("-" * 80)

    # Minute 0
    variance_msg = ""
    if current_temp < 70:
        variance_msg = f"Low temp ({current_temp:.1f}°C) → slower pasteurization"
    elif current_temp > 74:
        variance_msg = f"High temp ({current_temp:.1f}°C) → faster pasteurization"
    else:
        variance_msg = "Temperature optimal"

    print(f"{0:<6} {total_milk_liters:<18.2f} {pasteurized:<18.2f} {variance_msg}")

    while pasteurized < total_milk_liters and env.now < 59:
        # Calculate pasteurization rate based on temperature from previous minute
        if current_temp < 70:
            rate = base_rate * 0.6
        elif current_temp > 74:
            rate = base_rate * 1.2
        else:
            rate = base_rate

        pasteurized_now = min(rate, total_milk_liters - pasteurized)
        pasteurized += pasteurized_now

        # Apply new temp variation for *next* calculation
        temp_variation = random.uniform(-3, 3)
        current_temp = temperature + temp_variation

        # Determine current variance message (to be shown with current minute)
        if current_temp < 70:
            variance_msg = f"Low temp ({current_temp:.1f}°C) → slower pasteurization"
        elif current_temp > 74:
            variance_msg = f"High temp ({current_temp:.1f}°C) → faster pasteurization"
        else:
            variance_msg = "Temperature optimal"

        print(f"{int(env.now)+1:<6} {total_milk_liters:<18.2f} {pasteurized:<18.2f} {variance_msg}")

        yield env.timeout(1)

env = simpy.Environment()
env.process(pasteurization_process(env, TotalStartingMilk, BaseFlowRate, Temperature))
env.run(until=60)

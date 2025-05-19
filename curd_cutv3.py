
import simpy
import random
import pandas as pd
from datetime import datetime, timedelta, timezone
import uuid

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 200)
pd.set_option('display.max_colwidth', None)

# Simulate incoming data from the pasteurization stage
# This is fake data that pretends to come from the machine before the curd cutter
# Each "minute" has a random volume and a quality indicator called "variance"
preprocessing_data = [
    {
        "minute": i,
        "start_milk_l": 1000,
        "pasteurized_l": random.randint(80, 120),
        "variance": random.choice(["none", "low_temp", "temp_spike"])
    }
    for i in range(0, 30)
]

# Deciding if a batch should be processed or skipped
# Based on the variance (quality indicator)
def interpret_variance(variance):
    if variance == "low_temp":
        return True, "soft"  # We skip soft curds as they're not ready
    elif variance == "temp_spike":
        return False, "firm"  # Temp spike gives us firm curd — we process it
    else:
        return False, "medium"  # Normal condition

# STEP 3: we can set the auger speed based on the curd consistency
# This simulates how fast the curd moves through the machine
def get_auger_speed(consistency):
    if consistency == 'firm':
        return random.randint(60, 70)
    elif consistency == 'soft':
        return random.randint(80, 90)
    else:
        return random.randint(70, 80)

# STEP 4: curd cutting simulation logic
# This is where we model the machine behavior, blade wear, maintenance, etc.
def curd_cutting_machine(env, name, output_list, data_source):
    blade_sharpness = 100         # Machine starts fully sharp
    maintenance_time = 7          # Time it takes to perform maintenance
    blade_cycles = 0              # How many batches this blade has cut
    data_index = 0

    while data_index < len(data_source):
        entry = data_source[data_index]
        data_index += 1

        # Pull input values from preprocessing
        minute = entry["minute"]
        pasteurized = entry["pasteurized_l"]
        variance = entry["variance"]

        # Determine if batch is skippable and get consistency
        skip_batch, consistency = interpret_variance(variance)
        anomalies = []
        machine_status = "ok"

        # If the batch has to be skipped, log it and move on
        if skip_batch:
            anomalies.append(variance)
            yield env.timeout(2)  # Simulates time wasted on skipped batch
            output_list.append({
                "batch_id": str(uuid.uuid4()),
                "machine": name,
                "status": "Batch skipped - not processable",
                "anomalies_detected": anomalies,
                "variance": variance,
                "volume_litres": pasteurized,
                "source_minute": minute,
                "timestamp": (datetime.now(timezone.utc) + timedelta(minutes=env.now)).isoformat(),
                "start_minute": env.now,
                "end_minute": env.now + 2,
                "blade_sharpness": blade_sharpness,
                "blade_cycles": blade_cycles,
                "processing_time_sec": 0,
                "slice_thickness_mm": "N/A",
                "auger_speed_rpm": "N/A",
                "curd_weight_kg": "N/A",
                "machine_status": "warning"
            })
            continue

        # If batch is good, simulate cutting process
        volume = pasteurized
        base_time = volume / 60  # Basic time based on batch size

        # Adjust based on consistency of curd
        if consistency == "soft":
            base_time *= 1.2
        elif consistency == "firm":
            base_time *= 0.8

        # If blade is worn, processing takes longer
        wear_factor = (100 - blade_sharpness) / 100
        adjusted_time = round(base_time + base_time * wear_factor, 2)

        # Machine parameters
        auger_speed_rpm = get_auger_speed(consistency)
        slice_thickness_mm = random.randint(8, 12)
        curd_weight_kg = round(volume * 1.03, 2)  # Simulated yield

        # Simulate cutting time
        start = env.now
        yield env.timeout(adjusted_time)
        end = env.now
        blade_cycles += 1

        # Log completed batch
        output_list.append({
            "batch_id": str(uuid.uuid4()),
            "machine": name,
            "start_minute": start,
            "end_minute": end,
            "processing_time_sec": adjusted_time * 60,
            "volume_litres": volume,
            "curd_weight_kg": curd_weight_kg,
            "consistency": consistency,
            "blade_sharpness": blade_sharpness,
            "blade_cycles": blade_cycles,
            "slice_thickness_mm": slice_thickness_mm,
            "auger_speed_rpm": auger_speed_rpm,
            "status": "Cutting complete",
            "machine_status": machine_status,
            "anomalies_detected": anomalies,
            "variance": variance,
            "source_minute": minute,
            "timestamp": (datetime.now(timezone.utc) + timedelta(minutes=env.now)).isoformat()
        })

        # Reduce blade sharpness after every batch
        blade_sharpness -= 10

        # Simulate automatic maintenance if blade gets too dull
        if blade_sharpness <= 40:
            start_maint = env.now
            yield env.timeout(maintenance_time)
            blade_sharpness = 100
            output_list.append({
                "batch_id": str(uuid.uuid4()),
                "machine": name,
                "start_minute": start_maint,
                "end_minute": env.now,
                "processing_time_sec": maintenance_time * 60,
                "blade_sharpness": blade_sharpness,
                "blade_cycles": blade_cycles,
                "status": "Maintenance performed",
                "machine_status": "maintenance",
                "timestamp": (datetime.now(timezone.utc) + timedelta(minutes=env.now)).isoformat(),
                "anomalies_detected": [],
                "source_minute": "N/A"
            })

        # Idle time between batches
        yield env.timeout(random.randint(1, 3))

def run_simulation():
    output = []
    env = simpy.Environment()

    # We have 3 machines running in parallel
    env.process(curd_cutting_machine(env, "Machine A", output, preprocessing_data))
    env.process(curd_cutting_machine(env, "Machine B", output, preprocessing_data))
    env.process(curd_cutting_machine(env, "Machine C", output, preprocessing_data))

    # Run the simulation for 30 minutes
    env.run(until=30)

    df = pd.DataFrame(output)

    float_cols = [
        "start_minute", "end_minute", "processing_time_sec",
        "volume_litres", "curd_weight_kg", "slice_thickness_mm", "auger_speed_rpm"
    ]
    for col in float_cols:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: round(x, 3) if pd.notnull(x) and isinstance(x, (float, int)) else x)

    # Save the final output to CSV and JSON
    df.to_csv(r"C:\Users\ahmed\OneDrive - Swinburne University\final year project\machines_code\curd_cutting_output_updated.csv", index=False)
    df.to_json(r"C:\Users\ahmed\OneDrive - Swinburne University\final year project\machines_code\curd_cutting_output_updated.json", orient="records", indent=2)

    # Print table to terminal
    print(df)
    return df

df_result = run_simulation()

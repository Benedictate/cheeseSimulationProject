# Cheese factory Salting & Mellowing
import simpy
import json
import os
from datetime import datetime, timezone

# Define Constants
FLOW_RATE = 50.0                    # kg/min (represents continuous flow of curds)
MAX_FLOW_RATE = 181.5               # kg/min max that the machine can handle
MELLOWING_TIME = 10                 # mellowing time in mins, represents how long it takes for curd to pass through the mellower
SALT_RECIPE = 0.033                 # amount of salt % 
SIMULATION_TIME = 60    

# Derived Constants
MAX_SLICES = int((MAX_FLOW_RATE * MELLOWING_TIME) / (FLOW_RATE * (MELLOWING_TIME / int((MAX_FLOW_RATE * MELLOWING_TIME) / FLOW_RATE))))         # max number of slices that can fit in the machine
GENERATION_INTERVAL = MELLOWING_TIME / MAX_SLICES                                                                                               # how often a slice is generated
SLICE_MASS = FLOW_RATE * GENERATION_INTERVAL                                                                                                    # mass per generated slice

# Observer to capture data
observer = []

def curd_generator(env, output_conveyor):
    """Represents output from curd mill"""
    slice_id = 0
    while True:
        slice_id += 1
        curd_slice = {
            'id': slice_id,
            'mass': SLICE_MASS,
            'salt': 0.0
        }
        print(f"[{env.now:.2f}] Generated curd slice {slice_id}")
        yield output_conveyor.put(curd_slice)
        yield env.timeout(GENERATION_INTERVAL)

def salt_dispenser(env, input_conveyor, mellowing_conveyor, mellowing_output_conveyor):
    """Adds salt to curd slices and places them on the mellowing conveyor."""
    while True:
        curd_slice = yield input_conveyor.get()
        salt_amount = SALT_RECIPE * curd_slice['mass']
        curd_slice['salt'] += salt_amount

        observer.append({
            'sim_time_min': env.now,
            'utc_time': datetime.now(timezone.utc).isoformat(),
            'curd_id': curd_slice['id'],
            'mass': curd_slice['mass'],
            'salt': curd_slice['salt'],
            'machine': 'salt_dispenser'
        })
        print(f"[{env.now:.2f}] Salted curd slice {curd_slice['id']} with {salt_amount:.2f} kg salt")

        # Put on mellowing conveyor
        yield mellowing_conveyor.put(curd_slice)

        # Start mellowing in parallel
        env.process(mellowing_delay(env, curd_slice, mellowing_conveyor, mellowing_output_conveyor))

def mellowing_delay(env, curd_slice, mellowing_conveyor, mellowing_output_conveyor):
    """Waits for mellowing time, then removes from conveyor and outputs it."""

    

    observer.append({
        'sim_time_min': env.now,
        'utc_time': datetime.now(timezone.utc).isoformat(),
        'curd_id': curd_slice['id'],
        'mass': curd_slice['mass'],
        'salt': curd_slice['salt'],
        'machine': 'mellowing_start'
    })
    print(f"[{env.now:.2f}] Starting mellowing for curd slice {curd_slice['id']}")

    yield env.timeout(MELLOWING_TIME)

    yield mellowing_conveyor.get()

    observer.append({
        'sim_time_min': env.now,
        'utc_time': datetime.now(timezone.utc).isoformat(),
        'curd_id': curd_slice['id'],
        'mass': curd_slice['mass'],
        'salt': curd_slice['salt'],
        'machine': 'mellowing_end'
    })
    print(f"[{env.now:.2f}] Finished mellowing for curd slice {curd_slice['id']}")

    # Optionally put into final output
    yield mellowing_output_conveyor.put(curd_slice)

def save_observations_to_json(filename='data/salting & mellowing data.json'):
    """Saves all collected observations to a json file. Creates the dir and file if they don't exist."""
    
    folder = os.path.dirname(filename)
    if folder:
        os.makedirs(folder, exist_ok=True)

    # Write observations to JSON file.
    with open(filename, 'w') as f:
        json.dump(observer, f, indent=4)

    print(f"Observations saved to {filename}")

def main():
    env = simpy.Environment()

    # Conveyor stores
    curd_conveyor = simpy.Store(env, capacity=MAX_SLICES)
    mellowing_conveyor = simpy.Store(env, capacity=MAX_SLICES)
    mellowing_output_conveyor = simpy.Store(env)

     # Start processes
    env.process(curd_generator(env, curd_conveyor))
    env.process(salt_dispenser(env, curd_conveyor, mellowing_conveyor, mellowing_output_conveyor))

    # Run simulation
    env.run(until=SIMULATION_TIME)

    # Save data
    save_observations_to_json()

if __name__ == "__main__":
    main()
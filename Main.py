import simpy
from Machines.step6_salting_and_mellowing import SaltingMachine

# Constants
FLOW_RATE = 50.0
MAX_FLOW_RATE = 181.5
MELLOWING_TIME = 10
SALT_RECIPE = 0.033
SIMULATION_TIME = 60

# Derived values
MAX_SLICES = int((MAX_FLOW_RATE * MELLOWING_TIME) / (FLOW_RATE * (MELLOWING_TIME / int((MAX_FLOW_RATE * MELLOWING_TIME) / FLOW_RATE))))
GENERATION_INTERVAL = MELLOWING_TIME / MAX_SLICES
SLICE_MASS = FLOW_RATE * GENERATION_INTERVAL

def curd_generator(env, output_conveyor):
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

def main():
    env = simpy.Environment()

    # Create conveyors
    generator_output = simpy.Store(env, capacity=MAX_SLICES)
    salting_output = simpy.Store(env)

    # Start generator
    env.process(curd_generator(env, generator_output))

    # Run the salting machine
    salting_machine = SaltingMachine.run(env, generator_output, salting_output, mellowing_time=MELLOWING_TIME, salt_recipe=SALT_RECIPE)

    # Run simulation
    env.run(until=SIMULATION_TIME)

    # Save logs
    salting_machine.save_observations_to_json()

if __name__ == "__main__":
    main()

import simpy
from machines import *
from helpers import *
import sys

# Open a file for writing
log_file = open("cheese_sim_log.txt", "w")

# Redirect stdout to the file
sys.stdout = log_file

# Constants
FLOW_RATE = 50.0
MAX_FLOW_RATE = 181.5
MELLOWING_TIME = 10
SALT_RECIPE = 0.033
SIMULATION_TIME = 6000
TIMEMODE = TimeMode.ST
BLOCK_WEIGHT = 27
VAT_BATCH_SIZE = 10000
BALDE_WEAR_RATE = 0.1
AUGER_SPEED = 50

# Derived values
MAX_SLICES = int((MAX_FLOW_RATE * MELLOWING_TIME) / (FLOW_RATE * (MELLOWING_TIME / int((MAX_FLOW_RATE * MELLOWING_TIME) / FLOW_RATE))))
GENERATION_INTERVAL = MELLOWING_TIME / MAX_SLICES
SLICE_MASS = FLOW_RATE * GENERATION_INTERVAL

def curd_generator(env, output_conveyor):
    slice_id = 0
    while slice_id<100:
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
    waste_store = simpy.Store(env)
    pasteuriser_input = simpy.Store(env)
    pasteuriser_output = simpy.Store(env)
    vat_input = simpy.Store(env)
    vat_output = simpy.Store(env)
    cutter_input = simpy.Store(env)
    cutter_output = simpy.Store(env)
    whey_input = simpy.Store(env)
    whey_output = simpy.Store(env)
    cheddaring_input = simpy.Store(env)
    cheddaring_output = simpy.Store(env)
    salting_input = simpy.Store(env, capacity=MAX_SLICES)
    salting_output = simpy.Store(env)
    presser_input = simpy.Store(env)
    presser_output = simpy.Store(env)
    ripener_input = simpy.Store(env)

    pasteuriser_input.items = [50000]
    '''
    machines running in sequence with their respective helper functions
    '''
    # Run pasteuriser
    pasteuriser = Pasteuriser.run(env, pasteuriser_input, pasteuriser_output, waste_store)
    
    # Convert pasteuriser output to cheesevat input
    env.process(pasteuriser_to_vat(env, pasteuriser_output, vat_input, VAT_BATCH_SIZE))

    # Run cheese vat
    cheese_vat = CheeseVat.run(env, vat_input, vat_output, anomaly_probability=10)

    # Convert vat output to cutter input
    env.process(vat_to_cutter(env, vat_output, cutter_input))

    # Run curd cutter
    curd_cutter = CurdCutter.run(env, cutter_input, cutter_output, BALDE_WEAR_RATE, AUGER_SPEED)

    # Convert cutter output to whey input
    env.process(cutter_to_whey(env, cutter_output, whey_input, 1000))

    # Run whey drainer
    whey_drainer = WheyDrainer.run(env, whey_input, whey_output)

    # Convert whe output to cheddaring input
    env.process(whey_to_cheddaring(env, whey_output, cheddaring_input))

    # Run cheddaring machine
    cheddaring_machine = Cheddaring.run(env, cheddaring_input, cheddaring_output)
    
    # Convert cheddaring output to salting input
    env.process(cheddaring_to_salting(env, cheddaring_output, salting_input, SLICE_MASS, GENERATION_INTERVAL))

    # Run the salting machine
    salting_machine = SaltingMachine.run(env, salting_input, salting_output, mellowing_time=MELLOWING_TIME, salt_recipe=SALT_RECIPE)

    # Convert salting output to presser input
    env.process(salting_to_presser(env, salting_output, presser_input, BLOCK_WEIGHT))

    # Run Presser
    cheese_presser = CheesePresser.run(env, presser_input, presser_output)

    # Convert presser output to ripener input
    env.process(presser_to_ripener(env, presser_output, ripener_input))

    # Run ripener
    ripener = Ripener.run(env, ripener_input)

    # Run sim
    env.run(until=SIMULATION_TIME)

    # Save logs
    salting_machine.save_observations_to_json()
    curd_cutter.save_logs("data")
if __name__ == "__main__":
    main()
    

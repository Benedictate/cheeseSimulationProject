import simpy
import json
import os
from machines import *
from helpers import *
import sys

# Open a file for writing
log_file = open("cheese_sim_log.txt", "w")

# Redirect stdout to the file
sys.stdout = log_file

def load_defaults(filename="args.json"):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_dir, filename)
    with open(path) as f:
        return json.load(f)
    

# Constants
MAX_FLOW_RATE = 181.5

def main(args=None):

    defaults = load_defaults()

    if args is None:
        args = defaults

    env = create_env(args["global"]["time_mode"], 60, True)

    # Derived values
    MAX_SLICES = int((MAX_FLOW_RATE * args["machines"]["salting_machine"]["mellowing_time"]) / (args["machines"]["salting_machine"]["flow_rate"] * (args["machines"]["salting_machine"]["mellowing_time"] / int((MAX_FLOW_RATE * args["machines"]["salting_machine"]["mellowing_time"]) / args["machines"]["salting_machine"]["flow_rate"]))))
    GENERATION_INTERVAL = args["machines"]["salting_machine"]["mellowing_time"] / MAX_SLICES
    SLICE_MASS = args["machines"]["salting_machine"]["flow_rate"] * GENERATION_INTERVAL

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

    pasteuriser_input.items = [args["global"]["milk_to_process"]]
    '''
    machines running in sequence with their respective helper functions
    '''
    # Run pasteuriser
    pasteuriser = Pasteuriser.run(env, pasteuriser_input, pasteuriser_output, args["machines"]["pasteuriser"]["temp_optimal"], waste_store, args["machines"]["pasteuriser"]["flow_rate"])
    
    # Convert pasteuriser output to cheesevat input
    env.process(pasteuriser_to_vat(env, pasteuriser_output, vat_input, args["machines"]["cheese_vat"]["vat_batch_size"]))

    # Run cheese vat
    cheese_vat = CheeseVat.run(env, vat_input, vat_output, args["machines"]["cheese_vat"]["optimal_ph"], args["machines"]["cheese_vat"]["milk_flow_rate"], args["machines"]["cheese_vat"]["anomaly_probability"])

    # Convert vat output to cutter input
    env.process(vat_to_cutter(env, vat_output, cutter_input))

    # Run curd cutter
    curd_cutter = CurdCutter.run(env, cutter_input, cutter_output, Clock, args["machines"]["curd_cutter"]["blade_wear_rate"], args["machines"]["curd_cutter"]["auger_speed"])

    # Convert cutter output to whey input
    env.process(cutter_to_whey(env, cutter_output, whey_input, args["machines"]["whey_drainer"]["target_mass"]))

    # Run whey drainer
    whey_drainer = WheyDrainer.run(env, whey_input, whey_output, Clock, args["machines"]["whey_drainer"]["target_moisture"] )

    # Convert whe output to cheddaring input
    env.process(whey_to_cheddaring(env, whey_output, cheddaring_input))

    # Run cheddaring machine
    cheddaring_machine = Cheddaring.run(env, cheddaring_input, cheddaring_output, Clock)
    
    # Convert cheddaring output to salting input
    env.process(cheddaring_to_salting(env, cheddaring_output, salting_input, SLICE_MASS, GENERATION_INTERVAL))

    # Run the salting machine
    salting_machine = SaltingMachine.run(env, salting_input, salting_output, Clock, mellowing_time=args["machines"]["salting_machine"]["mellowing_time"], salt_recipe=args["machines"]["salting_machine"]["salt_recipe"])

    # Convert salting output to presser input
    env.process(salting_to_presser(env, salting_output, presser_input, args["machines"]["cheese_presser"]["block_weight"]))

    # Run Presser
    cheese_presser = CheesePresser.run(env, presser_input, presser_output, Clock, args["machines"]["cheese_presser"]["anomaly_chance"], args["machines"]["cheese_presser"]["mold_count"])

    # Convert presser output to ripener input
    env.process(presser_to_ripener(env, presser_output, ripener_input))

    # Run ripener
    ripener = Ripener.run(env, ripener_input, Clock, args["machines"]["ripener"]["initial_temp"])

    # Simple json data test
    def write_test_json(env):
        count = 1
        filename = "Backend/data/test.ndjson"

        # Ensure the folder exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        while True:
            # Append a new JSON object as a line
            with open(filename, "a") as f:
                json.dump({"count": count}, f)
                f.write("\n")
                f.flush()                  # flush OS buffer
                os.fsync(f.fileno())       # ensure it's immediately visible

            count += 1
            yield env.timeout(1)           # 1 simulated minute

    # Start the writer process
    env.process(write_test_json(env))

    # Run sim
    env.run(until=args["global"]["simulation_time"])

    # Save logs
    salting_machine.save_observations_to_json()
    curd_cutter.save_logs("data")

  # Convert NDJSON to proper JSON array at the end
    with open("Backend/data/test.ndjson") as f:
        array = [json.loads(line) for line in f if line.strip()]

    with open("Backend/data/test_final.json", "w") as f:
        json.dump(array, f, indent=4)

if __name__ == "__main__":
    args = load_defaults("args.json")
    main(args)
    

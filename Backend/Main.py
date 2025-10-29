import simpy
import json
import os
from Machines import *
from helpers import *
import sys
import logging


log_file_path = "cheese_sim_log.txt"

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),             # Console output
        logging.FileHandler(log_file_path, mode="w")  # File output
    ]
)

logging.info("This will print to console and also be saved in cheese_sim_log.txt")


def load_defaults(filename="args.json"):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base_dir, filename)) as f:
        return json.load(f)
    

# Constants
MAX_FLOW_RATE = 181.5

def main(args=None):
    if args is None:
        args = load_defaults()
        print("Using default args.json")
    else:
        print("Using config from frontend")
        print(json.dumps(args, indent=2))

    env = create_env(args["global"]["time_mode"], 1, True)
    # Resolve data directory absolute path so it works no matter the cwd
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    nd_path = os.path.join(data_dir, "data.ndjson")
    final_json_path = os.path.join(data_dir, "data.json")
    # time_mode: 0 -> batch mode (no streaming), 1 -> streaming NDJSON
    stream = True if args["global"].get("time_mode", 1) == 1 else False
    logger = NdjsonLogger(ndjson_path=nd_path, final_json_path=final_json_path, stream=stream)

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
    pasteuriser = Pasteuriser.run(env, pasteuriser_input, pasteuriser_output, args["machines"]["pasteuriser"]["temp_optimal"], waste_store, args["machines"]["pasteuriser"]["flow_rate"], Clock, logger)
    
    # Convert pasteuriser output to cheesevat input
    env.process(pasteuriser_to_vat(env, pasteuriser_output, vat_input, args["machines"]["cheese_vat"]["vat_batch_size"]))

    # Run cheese vat
    cheese_vat = CheeseVat.run(env, vat_input, vat_output, args["machines"]["cheese_vat"]["optimal_ph"], args["machines"]["cheese_vat"]["milk_flow_rate"], args["machines"]["cheese_vat"]["anomaly_probability"], Clock, logger)

    # Convert vat output to cutter input
    env.process(vat_to_cutter(env, vat_output, cutter_input))

    # Run curd cutter
    curd_cutter = CurdCutter.run(env, cutter_input, cutter_output, Clock, args["machines"]["curd_cutter"]["blade_wear_rate"], args["machines"]["curd_cutter"]["auger_speed"], logger)

    # Convert cutter output to whey input
    env.process(cutter_to_whey(env, cutter_output, whey_input, args["machines"]["whey_drainer"]["target_mass"]))

    # Run whey drainer
    whey_drainer = WheyDrainer.run(env, whey_input, whey_output, Clock, args["machines"]["whey_drainer"]["target_moisture"], logger)

    # Convert whe output to cheddaring input
    env.process(whey_to_cheddaring(env, whey_output, cheddaring_input))

    # Run cheddaring machine
    cheddaring_machine = Cheddaring.run(env, cheddaring_input, cheddaring_output, Clock, logger=logger)
    
    # Convert cheddaring output to salting input
    env.process(cheddaring_to_salting(env, cheddaring_output, salting_input, SLICE_MASS, GENERATION_INTERVAL))

    # Run the salting machine
    salting_machine = SaltingMachine.run(env, salting_input, salting_output, Clock, mellowing_time=args["machines"]["salting_machine"]["mellowing_time"], salt_recipe=args["machines"]["salting_machine"]["salt_recipe"], logger=logger)

    # Convert salting output to presser input
    env.process(salting_to_presser(env, salting_output, presser_input, args["machines"]["cheese_presser"]["block_weight"]))

    # Run Presser
    cheese_presser = CheesePresser.run(env, presser_input, presser_output, Clock, args["machines"]["cheese_presser"]["anomaly_chance"], args["machines"]["cheese_presser"]["mold_count"], logger)

    # Convert presser output to ripener input
    env.process(presser_to_ripener(env, presser_output, ripener_input))

    # Run ripener
    ripener = Ripener.run(env, ripener_input, Clock, args["machines"]["ripener"]["initial_temp"], logger)

    # Centralized NDJSON logging is handled per machine; no test writer needed

    # Run sim
    env.run(until=args["global"]["simulation_time"])

    # Save logs
    pasteuriser.save_observations_to_json()
    cheese_vat.save_observations_to_json()
    curd_cutter.save_observations_to_json()
    whey_drainer.save_observations_to_json()
    cheddaring_machine.save_observations_to_json()
    salting_machine.save_observations_to_json()
    cheese_presser.save_observations_to_json()
    ripener.save_observations_to_json()


    # Convert NDJSON stream to final JSON array
    logger.finalize_json()

if __name__ == "__main__":
    import sys, json

    args = None
    try:
        # Read entire stdin payload; Node closes stdin after writing JSON
        stdin_data = sys.stdin.read()
        if stdin_data and stdin_data.strip():
            args = json.loads(stdin_data)
            print("✅ Using config from frontend")
            print(json.dumps(args, indent=2))
        else:
            print("ℹ️ No stdin config supplied, using defaults")
    except json.JSONDecodeError as e:
        print(f"⚠️ Failed to parse stdin JSON ({e}), falling back to defaults")

    main(args)

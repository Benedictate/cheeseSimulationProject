import simpy
from Machines import *
from helpers import *
import sys
import json
import time

# Constants
FLOW_RATE = 50.0
MAX_FLOW_RATE = 181.5
MELLOWING_TIME = 10
SALT_RECIPE = 0.033
SIMULATION_TIME = 6000
BLOCK_WEIGHT = 27
VAT_BATCH_SIZE = 10000
BALDE_WEAR_RATE = 0.1
AUGER_SPEED = 50

# Derived values
MAX_SLICES = int((MAX_FLOW_RATE * MELLOWING_TIME) / (FLOW_RATE * (MELLOWING_TIME / int((MAX_FLOW_RATE * MELLOWING_TIME) / FLOW_RATE))))
GENERATION_INTERVAL = MELLOWING_TIME / MAX_SLICES
SLICE_MASS = FLOW_RATE * GENERATION_INTERVAL

def main(TIMEMODE):
    print(f"🧀 Starting cheese simulation with TIMEMODE: {TIMEMODE}")
    print(f"📊 TIMEMODE {TIMEMODE}: {'Real-time' if TIMEMODE == 1 else 'Simulation-time'}")
    
    env = create_env(TIMEMODE, 60, True)

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

    def progress_reporter():
        """Report simulation progress periodically for real-time mode"""
        while env.now < SIMULATION_TIME:
            yield env.timeout(100)  # Report every 100 time units
            progress = (env.now / SIMULATION_TIME) * 100
            
            progress_data = {
                "timestamp": time.time(),
                "simulation_time": env.now,
                "progress_percent": round(progress, 1),
                "max_time": SIMULATION_TIME,
                "machine_states": {
                    "pasteuriser_output": len(pasteuriser_output.items),
                    "vat_output": len(vat_output.items),
                    "cutter_output": len(cutter_output.items),
                    "salting_input": f"{len(salting_input.items)}/{salting_input.capacity}",
                    "salting_output": len(salting_output.items),
                    "presser_output": len(presser_output.items)
                }
            }
            
            print(json.dumps(progress_data))
            
            # Also print human-readable format for debugging
            print(f"⏱️ Simulation Progress: {progress:.1f}% (Time: {env.now}/{SIMULATION_TIME})")

    # Start progress reporter for real-time mode
    if TIMEMODE == 1:
        env.process(progress_reporter())

    # Run sim
    print(f"🏃 Running simulation for {SIMULATION_TIME} time units...")
    env.run(until=SIMULATION_TIME)

    # Save logs
    salting_machine.save_observations_to_json()
    curd_cutter.save_logs("data")
    
    final_results = {
        "status": "completed",
        "timestamp": time.time(),
        "simulation_time": SIMULATION_TIME,
        "timemode": TIMEMODE,
        "final_machine_states": {
            "pasteuriser_output": len(pasteuriser_output.items),
            "vat_output": len(vat_output.items),
            "cutter_output": len(cutter_output.items),
            "salting_output": len(salting_output.items),
            "presser_output": len(presser_output.items),
            "ripener_input": len(ripener_input.items)
        }
    }
    
    print("✅ Simulation completed successfully!")
    print(f"📈 Results saved to data files")
    print(json.dumps(final_results))

if __name__ == "__main__":
    # Get TIMEMODE from command line argument, default to 0
    timemode = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    main(timemode)

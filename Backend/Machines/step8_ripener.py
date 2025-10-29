import simpy
import json
import os
from helpers.ndjson_logger import build_standard_event
from datetime import datetime, timezone

class Ripener:

    # --- Temperature Thresholds (°C) ---
    TEMP_MIN_OPERATING = 3     # Lowest temp for intake
    TEMP_OPTIMAL_MIN = 7       # Minimum temp to ripen
    TEMP_OPTIMAL_MAX = 13      # Maximum temp to ripen
    TEMP_RUINED_THRESHOLD = 17 # Temp at which cheese is ruined

    # --- Step Calculations ---
    STEP_DURATION_SEC = 15
    STEPS_PER_MIN = 60 // STEP_DURATION_SEC

    # --- Temperature Adjustment ---
    TEMP_DROP_PER_STEP = 1     # Cooling rate per step
    TEMP_RISE_WHEN_COLD = 1.5  # Reheating rate per step

    def __init__(self, env, input_blocks, clock, initial_temp=None, logger=None):
        self.incoming_blocks = input_blocks
        self.clock = clock()
        self.initial_temp = initial_temp
        self.env = env
        self.observer = []
        self.logger = logger

    @staticmethod
    def format_sim_time(sim_time):
        """Convert sim time steps to MM:SS format."""
        total_seconds = sim_time * Ripener.STEP_DURATION_SEC
        return f"{int(total_seconds // 60)}:{int(total_seconds % 60):02d}"

    def ripening_process(self):
        # Storage state variables
        ripening = 0
        intake = yield self.incoming_blocks.get()
        step_weight = intake
        

        # Machine state variables
        temperature = self.initial_temp
        status = "Adding pressed cheeses to shelves..."

        # Header
        print("-" * 95)

        # Emit an immediate intake event so ripener appears even if the sim ends soon after handoff
        first_event = {
            'sim_time_min': int(self.env.now // self.STEPS_PER_MIN),
            'utc_time': self.clock.now(),
            'intake_kg': round(intake, 2),
            'total_ripening_kg': round(ripening, 2),
            'temperature_C': round(temperature, 2),
            'status': status,
            'machine': 'ripener'
        }
        self.observer.append(first_event)
        if self.logger:
            self.logger.log_event(
                build_standard_event(
                    machine='ripener',
                    sim_time_min=first_event['sim_time_min'],
                    utc_time=first_event['utc_time'],
                    temperature_C=first_event['temperature_C'],
                    output_weight_kg=first_event['total_ripening_kg'],
                    extra={
                        'intake_kg': first_event['intake_kg'],
                        'status': status,
                    },
                )
            )

        # Processing loop
        while True:
            yield self.env.timeout(1)

            ripening += step_weight

            event = {
                'sim_time_min': int(self.env.now // self.STEPS_PER_MIN),
                'utc_time': self.clock.now(),
                'intake_kg': round(intake, 2),
                'total_ripening_kg': round(ripening, 2),
                'temperature_C': round(temperature, 2),
                'status': status,
                'machine': 'ripener'
            }
            self.observer.append(event)
            if self.logger:
                self.logger.log_event(
                    build_standard_event(
                        machine='ripener',
                        sim_time_min=event['sim_time_min'],
                        utc_time=event['utc_time'],
                        temperature_C=event['temperature_C'],
                        output_weight_kg=event['total_ripening_kg'],
                        extra={
                            'intake_kg': event['intake_kg'],
                            'status': status,
                        },
                    )
                )

            print(f"{self.clock.now()} {intake:<14.2f} {ripening:<14.2f} {temperature:<10.2f} {status}")

            # Final report
            stored_blocks = ripening
            print("\n--- Storage Update ---")
            print(f"Total Mass Stored: {stored_blocks} or {stored_blocks}kg")
            if temperature > self.TEMP_OPTIMAL_MAX:
                print("The Cheese did not ripen properly")
            elif temperature > self.TEMP_OPTIMAL_MIN:
                print("The Cheese took 12 months to ripen.")
            elif temperature >= self.TEMP_MIN_OPERATING:
                print("The Cheese took 18 months to ripen.")
            elif temperature < self.TEMP_MIN_OPERATING:
                print("The Cheese took too long to ripen.")

    def save_observations_to_json(self, filename='Backend/data/ripener_data.json'):
        folder = os.path.dirname(filename)
        if folder:
            os.makedirs(folder, exist_ok=True)

        with open(filename, 'w') as f:
            json.dump(self.observer, f, indent=4)

        print(f"Observations saved to {filename}")

    @staticmethod
    def run(env, input_blocks, clock, initial_temp=None, logger=None):
       
        machine = Ripener(env, input_blocks, clock, initial_temp, logger)
        env.process(machine.ripening_process())
        return machine

import simpy
from datetime import datetime, timezone
import json
import os

class SaltingMachine:
    def __init__(self, env, input_conveyor, mellowing_conveyor, mellowing_output_conveyor, mellowing_time=10, salt_recipe=0.033):
        self.env = env
        self.input_conveyor = input_conveyor
        self.mellowing_conveyor = mellowing_conveyor
        self.mellowing_output_conveyor = mellowing_output_conveyor
        self.mellowing_time = mellowing_time
        self.salt_recipe = salt_recipe
        self.observer = []

    def salt_dispenser(self):
        while True:
            curd_slice = yield self.input_conveyor.get()
            salt_amount = self.salt_recipe * curd_slice['mass']
            curd_slice['salt'] += salt_amount

            self.log(curd_slice, 'salt_dispenser')
            print(f"[{self.env.now:.2f}] Salted curd slice {curd_slice['id']} with {salt_amount:.2f} kg salt")

            yield self.mellowing_conveyor.put(curd_slice)
            self.env.process(self.mellowing_delay(curd_slice))

    def mellowing_delay(self, curd_slice):
        self.log(curd_slice, 'mellowing_start')
        print(f"[{self.env.now:.2f}] Starting mellowing for curd slice {curd_slice['id']}")

        yield self.env.timeout(self.mellowing_time)
        yield self.mellowing_conveyor.get()

        self.log(curd_slice, 'mellowing_end')
        print(f"[{self.env.now:.2f}] Finished mellowing for curd slice {curd_slice['id']}")

        yield self.mellowing_output_conveyor.put(curd_slice)

    def log(self, curd_slice, machine_stage):
        self.observer.append({
            'sim_time_min': self.env.now,
            'utc_time': datetime.now(timezone.utc).isoformat(),
            'curd_id': curd_slice['id'],
            'mass': curd_slice['mass'],
            'salt': curd_slice['salt'],
            'machine': machine_stage
        })

    def save_observations_to_json(self, filename='data/salting & mellowing data.json'):
        folder = os.path.dirname(filename)
        if folder:
            os.makedirs(folder, exist_ok=True)

        with open(filename, 'w') as f:
            json.dump(self.observer, f, indent=4)

        print(f"Observations saved to {filename}")

    @staticmethod
    def run(env, generator_output, salting_output, mellowing_time=10, salt_recipe=0.033):
        mellowing_conveyor = simpy.Store(env)

        machine = SaltingMachine(env, generator_output, mellowing_conveyor, salting_output,
                                 mellowing_time=mellowing_time, salt_recipe=salt_recipe)

        env.process(machine.salt_dispenser())
        return machine  # return instance in case you want to inspect `.observer` or save logs

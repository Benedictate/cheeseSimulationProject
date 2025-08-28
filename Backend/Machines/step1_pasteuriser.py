import simpy
import random

# --- Temperature thresholds (°C) ---
TEMP_MIN_OPERATING = 68
TEMP_OPTIMAL_MIN = 70
TEMP_OPTIMAL = 72
TEMP_OPTIMAL_MAX = 74
TEMP_BURN_THRESHOLD = 77

# --- Timings (seconds per step) ---
STEP_DURATION_SEC = 15
STEPS_PER_MIN = 60 // STEP_DURATION_SEC
STARTUP_DURATION = 20   # 5 min / 15 sec
COOLDOWN_DURATION = 8   # 2 min / 15 sec

# --- Dynamics ---
TEMP_DROP_PER_STEP = 1
TEMP_RISE_WHEN_COLD = 1.5
TEMP_RANGE_VARIATION = (-2, 2)
FLOW_RATE = 41.7  # L per step

class Pasteuriser:
    def __init__(self, env, input_store, output_store, waste_store, flow_rate=FLOW_RATE):
        self.env = env
        self.input_store = input_store
        self.output_store = output_store
        self.waste_store = waste_store
        self.flow_rate = flow_rate

        # Internal state
        self.temperature = TEMP_OPTIMAL
        self.cooling_overheat = False
        self.start_tank = sum(input_store.items)
        self.balance_tank = 0.0
        self.pasteurized_total = 0.0
        self.burnt_total = 0.0

        # Print header once
        print(f"{'Time':<7} {'StartTank':>7} {'BalanceTank':>12} {'Pasteurized':>12} {'Burnt':>7} {'Temp':>7} Status")
        print("-" * 70)

    def format_time(self):
        total_seconds = self.env.now * STEP_DURATION_SEC
        minutes = int(total_seconds // 60)
        seconds = int(total_seconds % 60)
        return f"{minutes}:{seconds:02d}"

    def log_status(self, status):
        print(f"{self.format_time():<7} "
              f"{self.start_tank:>7.2f}        "
              f"{self.balance_tank:>7.2f}        "
              f"{self.pasteurized_total:>7.2f}        "
              f"{self.burnt_total:>7.2f}        "
              f"{self.temperature:>5.2f}      "
              f"{status}")

    def process(self):
        # --- Startup phase ---
        for _ in range(STARTUP_DURATION):
            self.log_status("Startup / Heating")
            yield self.env.timeout(1)

        # --- Processing loop ---
        while self.start_tank > 0 or self.balance_tank > 0:
            # Choose source
            if self.start_tank > 0:
                milk_source = "Start Tank"
                milk_available = self.start_tank
            else:
                milk_source = "Balance Tank"
                milk_available = self.balance_tank

            milk_this_step = min(self.flow_rate, milk_available)

            # --- Temperature logic ---
            if self.cooling_overheat:
                self.temperature -= TEMP_DROP_PER_STEP
                status = "Cooling after Overheat"
                if self.temperature <= TEMP_OPTIMAL:
                    self.cooling_overheat = False
                    status = "Cooled - Resuming"
                yield self.env.timeout(1)
                self.log_status(status)
                continue

            if self.temperature >= TEMP_BURN_THRESHOLD:
                self.burnt_total += milk_this_step
                status = f"Burnt milk! {milk_this_step:.2f}L"
                self.cooling_overheat = True
                if milk_source == "Start Tank":
                    self.start_tank -= milk_this_step
                else:
                    self.balance_tank -= milk_this_step

            elif self.temperature < TEMP_OPTIMAL_MIN:
                self.balance_tank += milk_this_step
                status = f"Too cold - recirculating {milk_this_step:.2f}L and reheating"
                if milk_source == "Start Tank":
                    self.start_tank -= milk_this_step
                else:
                    self.balance_tank -= milk_this_step
                self.temperature += TEMP_RISE_WHEN_COLD

            elif TEMP_OPTIMAL_MIN <= self.temperature <= TEMP_OPTIMAL_MAX:
                self.pasteurized_total += milk_this_step
                self.output_store.put(milk_this_step)
                status = f"Pasteurized from {milk_source}"
                if milk_source == "Start Tank":
                    self.start_tank -= milk_this_step
                else:
                    self.balance_tank -= milk_this_step

            else:
                self.balance_tank += milk_this_step
                status = f"Too hot - recirculating {milk_this_step:.2f}L"
                if milk_source == "Start Tank":
                    self.start_tank -= milk_this_step
                else:
                    self.balance_tank -= milk_this_step

            # Random temp fluctuation
            self.temperature += random.uniform(*TEMP_RANGE_VARIATION)

            # Log and wait
            self.log_status(status)
            yield self.env.timeout(1)

    @staticmethod
    def run(env, input_store, output_store, waste_store, flow_rate=FLOW_RATE):
        machine = Pasteuriser(env, input_store, output_store, waste_store, flow_rate)
        env.process(machine.process())
        return machine

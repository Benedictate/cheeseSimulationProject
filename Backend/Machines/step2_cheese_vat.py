import simpy
import random
env = simpy.Environment()
input = simpy.Store(env)
output = simpy.Store(env)
class CheeseVat:
    def __init__(self, input_store, output_store, optimal_ph, milk_flow_rate, anolamy_probability):
        self.input = input_store
        self.output = output_store
        self.STEP_DURATION_SEC = 15
        self.MILK_FLOW_RATE = milk_flow_rate
        self.MILK_PER_STEP = self.MILK_FLOW_RATE * self.STEP_DURATION_SEC
        self.INITIAL_TEMP = 20.0
        self.TEMP_OPTIMAL_MIN = 31.0
        self.TEMP_OPTIMAL_MAX = 33.0
        self.TEMP_COOKING = 39.0
        self.INITIAL_PH = 6.70
        self.OPTIMAL_PH = optimal_ph
        self.BASE_MILK_CONVERSION_RATE = 0.02
        self.BASE_WHEY_RELEASE_RATE = 0.02  
        self.BASE_WHEY_DRAIN_RATE = 0.05 
        self.MILK_TO_CURD_NORMAL = 0.12
        self.MILK_TO_WHEY_NORMAL = 0.88
        self.DEFAULT_ANOMALY_PROBABILITY = 10
        self.ANOMALY_WEIGHTS = {
            "temperature": 3, "rennet": 3, "ph": 1,
            "cutting": 2, "stirring": 2, "whey_release": 2
        }
        self.MAX_STEPS_PER_PHASE = 1000
    def format_sim_time(self, sim_time):
        """Convert simulation time to HH:MM:SS format."""
        total_seconds = sim_time * self.STEP_DURATION_SEC
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"


    def cheese_vat_process(self, env, anomaly_probability):
        """Cheese vat simulation for cheddar production."""
        while True:
            self.TOTAL_MILK = yield self.input.get()
            # State variables
            milk_amount = 0.00
            whey_amount = 0.00
            curd_amount = 0.00
            temperature = self.INITIAL_TEMP
            pH = self.INITIAL_PH
            anomalies = []
            
            # Pending changes to apply at the next step
            pending_changes = {
                "milk": 0.00,
                "whey": 0.00,
                "curd": 0.00,
                "temp": 0.00,
                "ph": 0.00
            }
            
            # Anomaly effect tracking
            anomaly_effects = {
                "small_curds": False,
                "weak_curds": False,
                "uneven_curds": False,
                "rubbery_curds": False,
                "high_moisture": False
            }
            
            # Helper function to check for anomalies with weighted selection
            def check_anomaly(stage):
                if random.random() < (anomaly_probability / 100):
                    # Get all possible anomaly types for this stage
                    possible_anomalies = []
                    weights = []
                    
                    if stage == "heating":
                        possible_anomalies = ["temperature_low", "temperature_high"]
                        weights = [self.ANOMALY_WEIGHTS["temperature"], self.ANOMALY_WEIGHTS["temperature"]]
                    elif stage == "rennet":
                        possible_anomalies = ["rennet_low", "rennet_high", "ph_off"]
                        weights = [self.ANOMALY_WEIGHTS["rennet"], self.ANOMALY_WEIGHTS["rennet"], self.ANOMALY_WEIGHTS["ph"]]
                    elif stage == "cutting":
                        possible_anomalies = ["cutting_uneven", "cutting_mechanical"]
                        weights = [self.ANOMALY_WEIGHTS["cutting"], self.ANOMALY_WEIGHTS["cutting"]]
                    elif stage == "stirring":
                        possible_anomalies = ["stirring_excessive", "stirring_uneven"]
                        weights = [self.ANOMALY_WEIGHTS["stirring"], self.ANOMALY_WEIGHTS["stirring"]]
                    elif stage == "whey_release":
                        possible_anomalies = ["drain_clogged", "drain_too_fast"]
                        weights = [self.ANOMALY_WEIGHTS["whey_release"], self.ANOMALY_WEIGHTS["whey_release"]]
                    
                    if possible_anomalies:
                        return random.choices(possible_anomalies, weights=weights, k=1)[0]
                return None
            
            # Print header with wide column widths
            print(f"{'Time':<15} {'Phase':<50} {'Milk (L)':<20} {'Whey (L)':<20} {'Curd (L)':<20} {'Temp (°C)':<15} {'pH':<10} {'Anomalies':<100}")
            print("-" * 250)
            
            # --- Step 1: Fill the vat ---
            # Start with empty vat
            print(f"{self.format_sim_time(env.now):<15} {'Filling Vat':<50} {milk_amount:<20.2f} {whey_amount:<20.2f} {curd_amount:<20.2f} {temperature:<15.1f} {pH:<10.2f}")
            
            # Calculate first milk addition
            pending_changes["milk"] = self.MILK_PER_STEP
            
            # Simulate filling - continue until vat is full
            while milk_amount < self.TOTAL_MILK:
                # Apply pending changes from previous step
                milk_amount += pending_changes["milk"]
                pending_changes["milk"] = 0
                
                # Calculate next milk addition
                fill_amount = min(self.MILK_PER_STEP, self.TOTAL_MILK - milk_amount)
                if fill_amount > 0:
                    pending_changes["milk"] = fill_amount
                
                yield env.timeout(1)  # Each step is 1 unit in simulation time
                
                if milk_amount < self.TOTAL_MILK:
                    print(f"{self.format_sim_time(env.now):<15} {'Filling Vat':<50} {milk_amount:<20.2f} {whey_amount:<20.2f} {curd_amount:<20.2f} {temperature:<15.1f} {pH:<10.2f}")
            
            # --- Step 2: Set temperature ---    
            # Temperature anomaly check with improved selection
            temp_anomaly = check_anomaly("heating")
            
            # Determine target temperature based on anomaly
            if temp_anomaly == "temperature_low":
                target_temp = round(random.uniform(28.0, 30.0), 1)
                anomalies.append(f"Underheated milk ({target_temp}°C)")
                anomaly_effects["weak_curds"] = True
                anomaly_effects["high_moisture"] = True
            elif temp_anomaly == "temperature_high":
                target_temp = round(random.uniform(34.0, 40.0), 1)
                anomalies.append(f"Overheated milk ({target_temp}°C)")
                anomaly_effects["weak_curds"] = True
            else:
                # Normal temperature range
                target_temp = round(random.uniform(self.TEMP_OPTIMAL_MIN, self.TEMP_OPTIMAL_MAX), 1)
            
            # Simulate heating - continue until target temperature is reached
            temp_step = (target_temp - temperature) / 60  # Aim to reach target in ~15 minutes
            
            while abs(temperature - target_temp) > 0.1:  # Continue until we're very close to target
                # Apply pending changes from previous step
                temperature += pending_changes["temp"]
                pending_changes["temp"] = 0
                
                # Calculate next temperature change
                if temperature < target_temp:
                    pending_changes["temp"] = min(temp_step, target_temp - temperature)
                else:
                    pending_changes["temp"] = max(-temp_step, target_temp - temperature)
                
                print(f"{self.format_sim_time(env.now):<15} {'Heating Milk':<50} {milk_amount:<20.2f} {whey_amount:<20.2f} {curd_amount:<20.2f} {temperature:<15.1f} {pH:<10.2f} {', '.join(anomalies):<100}")
                yield env.timeout(1)
            
            # Ensure we hit the exact target
            temperature = round(target_temp, 1)
            
            # [Rest of the simulation logic remains exactly the same - continuing with rennet dosing, coagulation, cutting, stirring, whey release, and final report]
            
            # --- Step 3: Rennet dosing and stirring ---
            # Rennet anomaly check with improved selection
            rennet_anomaly = check_anomaly("rennet")
            
            if rennet_anomaly == "rennet_low":
                anomalies.append("Too little rennet added")
                anomaly_effects["small_curds"] = True
                anomaly_effects["weak_curds"] = True
            elif rennet_anomaly == "rennet_high":
                anomalies.append("Too much rennet added")
                anomaly_effects["rubbery_curds"] = True
            elif rennet_anomaly == "ph_off":
                pending_changes["ph"] = round(random.uniform(6.3, 6.8), 2) - pH
                anomalies.append(f"pH not optimal ({pH + pending_changes['ph']})")
                anomaly_effects["weak_curds"] = True
            
            # Rennet dosing (fixed time - 2 minutes)
            for step in range(8):  # 2 minutes = 8 steps
                # Apply pending changes
                pH += pending_changes["ph"]
                pending_changes["ph"] = 0
                
                print(f"{self.format_sim_time(env.now):<15} {'Rennet Dosing':<50} {milk_amount:<20.2f} {whey_amount:<20.2f} {curd_amount:<20.2f} {temperature:<15.1f} {pH:<10.2f} {', '.join(anomalies):<100}")
                yield env.timeout(1)
            
            # Gentle stirring (fixed time - 5 minutes)
            for step in range(20):  # 5 minutes = 20 steps
                print(f"{self.format_sim_time(env.now):<15} {'Gentle Stirring (for rennet)':<50} {milk_amount:<20.2f} {whey_amount:<20.2f} {curd_amount:<20.2f} {temperature:<15.1f} {pH:<10.2f} {', '.join(anomalies):<100}")
                yield env.timeout(1)
            
            # --- Step 4: Coagulation ---
            # Calculate conversion rates based on anomalies
            if anomaly_effects["weak_curds"]:
                curd_factor = 0.09  # 9% yield with weak curds
                conversion_rate = 0.7  # 70% normal speed
            elif anomaly_effects["rubbery_curds"]:
                curd_factor = 0.1  # 10% yield with rubbery curds
                conversion_rate = 1.2  # 120% normal speed (faster)
            else:
                curd_factor = self.MILK_TO_CURD_NORMAL
                conversion_rate = 1.0
            
            # Calculate milk conversion per step
            milk_per_step = milk_amount * self.BASE_MILK_CONVERSION_RATE * conversion_rate
            
            # Generate appropriate descriptions based on anomalies
            coagulation_descriptions = []
            
            if anomaly_effects["weak_curds"]:
                # Checks whether the word "Under" is present in the list of logged anomalies
                if "Under" in ", ".join(anomalies):
                    coagulation_descriptions.append("Weak gel structure forming")
                    coagulation_descriptions.append("Delayed coagulation observed")
                else:
                    coagulation_descriptions.append("Weak curd set forming")
            
            if anomaly_effects["small_curds"]:
                coagulation_descriptions.append("Incomplete gelation, soft curd forming")
            
            if anomaly_effects["rubbery_curds"]:
                coagulation_descriptions.append("Fast set, rubbery curd forming")
            
            # Ensure we have at least one description
            if not coagulation_descriptions:
                coagulation_descriptions = ["Normal coagulation in progress"]
            
            # Simulate coagulation - continue until all milk is converted
            step_count = 0
            while milk_amount > 0.1 and step_count < self.MAX_STEPS_PER_PHASE:  # Continue until milk is essentially gone
                # Apply pending changes
                milk_amount -= pending_changes["milk"]
                curd_amount += pending_changes["curd"]
                whey_amount += pending_changes["whey"]
                pending_changes["milk"] = 0
                pending_changes["curd"] = 0
                pending_changes["whey"] = 0
                
                # Cycle through descriptions
                description_idx = step_count % len(coagulation_descriptions)
                description = f"Coagulation: {coagulation_descriptions[description_idx]}"
                
                # Calculate next conversion
                if milk_amount > 0:
                    milk_converted = min(milk_per_step, milk_amount)
                    pending_changes["milk"] = milk_converted
                    pending_changes["curd"] = milk_converted * curd_factor
                    pending_changes["whey"] = milk_converted * (1 - curd_factor)
                
                print(f"{self.format_sim_time(env.now):<15} {description:<50} {milk_amount:<20.2f} {whey_amount:<20.2f} {curd_amount:<20.2f} {temperature:<15.1f} {pH:<10.2f} {', '.join(anomalies):<100}")
                yield env.timeout(1)
                step_count += 1
            
            # Apply final pending changes
            milk_amount -= pending_changes["milk"]
            curd_amount += pending_changes["curd"]
            whey_amount += pending_changes["whey"]
            pending_changes["milk"] = 0
            pending_changes["curd"] = 0
            pending_changes["whey"] = 0
            
            # Ensure milk is completely gone
            if milk_amount < 0.1:
                milk_amount = 0
            
            # [Continue with all remaining phases: cutting, stirring, whey release, and final report - exact same logic]
            
            # --- Step 5: Cutting phase ---
            # Check for cutting anomaly
            cutting_anomaly = check_anomaly("cutting")
            
            if cutting_anomaly == "cutting_uneven":
                anomalies.append("Inconsistent cutting pattern")
                anomaly_effects["uneven_curds"] = True
            elif cutting_anomaly == "cutting_mechanical":
                anomalies.append("Mechanical fault / dull blade")
                anomaly_effects["uneven_curds"] = True
            
            # Determine cutting parameters based on anomalies
            if anomaly_effects["weak_curds"] or anomaly_effects["small_curds"]:
                cutting_desc = "Cutting (delayed - soft curd)"
                whey_release_rate = self.BASE_WHEY_RELEASE_RATE * 0.7  # Slower release for weak curds
            elif anomaly_effects["rubbery_curds"]:
                cutting_desc = "Cutting (resistance - firm curd)"
                whey_release_rate = self.BASE_WHEY_RELEASE_RATE * 0.8  # Slower release for rubbery curds
            else:
                cutting_desc = "Cutting"
                whey_release_rate = self.BASE_WHEY_RELEASE_RATE
            
            # Target to release 20% of curd as whey during cutting
            target_whey_release = curd_amount * 0.2
            initial_curd = curd_amount
            released_whey = 0
            
            # Simulate cutting - continue until target whey release is achieved
            step_count = 0
            while released_whey < target_whey_release and step_count < self.MAX_STEPS_PER_PHASE:
                # Apply pending changes
                curd_amount -= pending_changes["curd"]
                whey_amount += pending_changes["whey"]
                pending_changes["curd"] = 0
                pending_changes["whey"] = 0
                
                # Calculate next whey release
                whey_released = min(initial_curd * whey_release_rate, curd_amount * 0.01, target_whey_release - released_whey)
                pending_changes["curd"] = whey_released
                pending_changes["whey"] = whey_released
                released_whey += whey_released
                
                # Determine description based on conditions
                if anomaly_effects["uneven_curds"]:
                    desc = f"{cutting_desc} (uneven particle sizes)"
                elif anomaly_effects["weak_curds"] or anomaly_effects["small_curds"]:
                    desc = f"{cutting_desc} (challenging due to curd properties)"
                else:
                    desc = cutting_desc
                
                print(f"{self.format_sim_time(env.now):<15} {desc:<50} {milk_amount:<20.2f} {whey_amount:<20.2f} {curd_amount:<20.2f} {temperature:<15.1f} {pH:<10.2f} {', '.join(anomalies):<100}")
                yield env.timeout(1)
                step_count += 1
            
            # Apply final pending changes
            curd_amount -= pending_changes["curd"]
            whey_amount += pending_changes["whey"]
            pending_changes["curd"] = 0
            pending_changes["whey"] = 0
            
            # --- Step 6: Stirring and cooking ---
            # Check for stirring anomaly with improved selection
            stirring_anomaly = check_anomaly("stirring")
            
            if stirring_anomaly == "stirring_excessive":
                anomalies.append("Over-stirring (high shear)")
                # Over-stirring breaks up curds further
                if anomaly_effects["small_curds"] or anomaly_effects["weak_curds"]:
                    anomaly_effects["small_curds"] = True  # Ensure small curds effect is active
            elif stirring_anomaly == "stirring_uneven":
                anomalies.append("Uneven stirring/heating")
            
            # Calculate whey release based on anomalies
            if stirring_anomaly == "stirring_excessive":
                whey_factor = 0.2  # 20% of curd becomes whey
                curd_loss_factor = 0.025  # 2.5% curd loss due to fines
            elif anomaly_effects["uneven_curds"]:
                whey_factor = 0.15  # 15% of curd becomes whey
                curd_loss_factor = 0.01  # 1% curd loss
            elif anomaly_effects["weak_curds"] or anomaly_effects["small_curds"]:
                whey_factor = 0.20  # 20% of curd becomes whey
                curd_loss_factor = 0.015  # 1.5% curd loss
            else:
                whey_factor = 0.20  # 20% of curd becomes whey
                curd_loss_factor = 0
            
            # First part: Heat to cooking temperature
            temp_step = (self.TEMP_COOKING - temperature) / 60  # Aim to reach target in ~15 minutes
            
            # Continue until target temperature is reached
            while abs(temperature - self.TEMP_COOKING) > 0.1:
                # Apply pending changes
                temperature += pending_changes["temp"]
                curd_amount -= pending_changes["curd"]
                whey_amount += pending_changes["whey"]
                pending_changes["temp"] = 0
                pending_changes["curd"] = 0
                pending_changes["whey"] = 0
                
                # Calculate next temperature change
                if temperature < self.TEMP_COOKING:
                    pending_changes["temp"] = min(temp_step, self.TEMP_COOKING - temperature)
                else:
                    pending_changes["temp"] = max(-temp_step, self.TEMP_COOKING - temperature)
                
                print(f"{self.format_sim_time(env.now):<15} {'Cooking (heating temperature)':<50} {milk_amount:<20.2f} {whey_amount:<20.2f} {curd_amount:<20.2f} {temperature:<15.1f} {pH:<10.2f} {', '.join(anomalies):<100}")
                yield env.timeout(1)
            
            # Ensure we hit the exact target
            temperature = self.TEMP_COOKING
            
            # Second part: Stirring at cooking temperature
            # Target to release specified percentage of curd as whey during stirring
            target_whey_release = curd_amount * whey_factor
            target_curd_loss = curd_amount * curd_loss_factor
            initial_curd = curd_amount
            released_whey = 0
            lost_curd = 0
            
            # Simulate stirring - continue until target whey release is achieved
            step_count = 0
            while (released_whey < target_whey_release or lost_curd < target_curd_loss) and step_count < self.MAX_STEPS_PER_PHASE:
                # Apply pending changes
                curd_amount -= pending_changes["curd"]
                whey_amount += pending_changes["whey"]
                pending_changes["curd"] = 0
                pending_changes["whey"] = 0
                
                # Calculate next whey release and curd loss
                if curd_amount > 0:
                    # Whey release
                    whey_released = min(initial_curd * self.BASE_WHEY_RELEASE_RATE, curd_amount * 0.02, target_whey_release - released_whey)
                    if whey_released > 0:
                        pending_changes["curd"] = whey_released
                        pending_changes["whey"] = whey_released
                        released_whey += whey_released
                    
                    # Curd loss
                    if curd_loss_factor > 0:
                        curd_lost = min(initial_curd * curd_loss_factor / 100, curd_amount * 0.01, target_curd_loss - lost_curd)
                        if curd_lost > 0:
                            pending_changes["curd"] += curd_lost
                            lost_curd += curd_lost
                
                # Description based on conditions
                if stirring_anomaly == "stirring_excessive":
                    desc = "Stirring and Cooking (excessive shear force)"
                elif stirring_anomaly == "stirring_uneven":
                    desc = "Stirring and Cooking (uneven heating)"
                elif anomaly_effects["weak_curds"] or anomaly_effects["small_curds"]:
                    desc = "Stirring and Cooking (curd breaking apart)"
                else:
                    desc = "Stirring and Cooking"
                
                print(f"{self.format_sim_time(env.now):<15} {desc:<50} {milk_amount:<20.2f} {whey_amount:<20.2f} {curd_amount:<20.2f} {temperature:<15.1f} {pH:<10.2f} {', '.join(anomalies):<100}")
                yield env.timeout(1)
                step_count += 1
            
            # Apply final pending changes
            curd_amount -= pending_changes["curd"]
            whey_amount += pending_changes["whey"]
            pending_changes["curd"] = 0
            pending_changes["whey"] = 0
            
            # --- Step 7: Whey release ---
            # Check for whey release anomaly with improved selection
            whey_anomaly = check_anomaly("whey_release")
            
            if whey_anomaly == "drain_clogged":
                drain_factor = 0.5  # 50% normal rate
                anomalies.append("Drain valve jammed/clogged")
            elif whey_anomaly == "drain_too_fast":
                drain_factor = 2.0  # 200% normal rate
                anomalies.append("Drain too fast")
            else:
                drain_factor = 1.0    
            
            # Calculate curd loss factor based on propagated anomalies
            curd_loss_factor = 0.0
            
            # Small curds are more likely to be lost during draining
            if anomaly_effects["small_curds"]:
                curd_loss_factor += 0.01  # 1% base loss for small curds
            
            # Weak curds break apart more easily
            if anomaly_effects["weak_curds"]:
                curd_loss_factor += 0.01  # 1% additional loss for weak curds
            
            # Fast draining increases curd loss, especially with small/weak curds
            if whey_anomaly == "drain_too_fast":
                curd_loss_factor *= 2.0  # Double the loss with fast drain
                curd_loss_factor += 0.01  # Additional 1% base loss
            
            # Calculate drain rate
            whey_drain_rate = self.BASE_WHEY_DRAIN_RATE * drain_factor
            
            # Simulate whey release - continue until all whey is drained
            step_count = 0
            while whey_amount > 0.1 and step_count < self.MAX_STEPS_PER_PHASE:
                # Apply pending changes
                whey_amount -= pending_changes["whey"]
                curd_amount -= pending_changes["curd"]
                pending_changes["whey"] = 0
                pending_changes["curd"] = 0
                
                # Calculate next whey drain
                whey_to_drain = min(whey_amount * whey_drain_rate, whey_amount)
                pending_changes["whey"] = whey_to_drain
                
                # Curd loss calculation - more pronounced as draining progresses
                if curd_amount > 0 and curd_loss_factor > 0:
                    # Progressive loss - more pronounced in middle of draining
                    drain_progress = 1 - (whey_amount / (whey_amount + pending_changes["whey"]))
                    # Bell curve effect - peak loss in middle of draining
                    progress_factor = 4 * drain_progress * (1 - drain_progress)
                    curd_loss = curd_amount * curd_loss_factor * progress_factor * whey_drain_rate
                    pending_changes["curd"] = curd_loss
                
                # Description based on conditions
                if whey_anomaly == "drain_clogged":
                    desc = "Whey Release (slow due to clogged valve)"
                elif whey_anomaly == "drain_too_fast":
                    if curd_loss_factor > 0.05:
                        desc = "Whey Release (too fast, significant curd loss)"
                    else:
                        desc = "Whey Release (too fast, some curd loss)"
                elif anomaly_effects["small_curds"] or anomaly_effects["weak_curds"]:
                    desc = "Whey Release (curd particles passing through)"
                else:
                    desc = "Whey Release"
                
                print(f"{self.format_sim_time(env.now):<15} {desc:<50} {milk_amount:<20.2f} {whey_amount:<20.2f} {curd_amount:<20.2f} {temperature:<15.1f} {pH:<10.2f} {', '.join(anomalies):<100}")
                yield env.timeout(1)
                step_count += 1
            
            # Apply final pending changes
            whey_amount -= pending_changes["whey"]
            curd_amount -= pending_changes["curd"]
            pending_changes["whey"] = 0
            pending_changes["curd"] = 0
            
            # Ensure whey is completely gone
            if whey_amount < 0.1:
                whey_amount = 0
            
            # --- Step 8: Curd storage ---
            print(f"{self.format_sim_time(env.now):<15} {'Curd Stored for Processing':<50} {milk_amount:<20.2f} {whey_amount:<20.2f} {curd_amount:<20.2f} {temperature:<15.1f} {pH:<10.2f} {', '.join(anomalies):<100}")
            
            # --- Final Report ---
            print("\n" + "=" * 150)
            print("SIMULATION COMPLETE".center(150))
            print("=" * 150)
            print(f"Total milk processed: {self.TOTAL_MILK:.2f}L")
            print(f"Final curd amount: {curd_amount:.2f}L ({curd_amount/self.TOTAL_MILK*100:.1f}%)")
            print(f"Final whey amount: {whey_amount:.2f}L ({whey_amount/self.TOTAL_MILK*100:.1f}%)")
            print(f"Remaining milk: {milk_amount:.2f}L ({milk_amount/self.TOTAL_MILK*100:.1f}%)")
            
            # Report anomaly effects
            active_effects = [effect.replace("_", " ").title() for effect, active in anomaly_effects.items() if active]
            if active_effects:
                print(f"Anomaly effects: {', '.join(active_effects)}")
            
            print(f"Anomalies detected: {', '.join(anomalies)}")
            
            yield self.output.put(curd_amount)

    @staticmethod
    def run(env, input_store, output_store, optimal_ph, milk_flow_rate, anomaly_probability=None):
        """Create a CheeseVat and start its process in the given environment."""
        vat = CheeseVat(input_store, output_store, optimal_ph, milk_flow_rate, anomaly_probability)
        if anomaly_probability is None:
            anomaly_probability = vat.DEFAULT_ANOMALY_PROBABILITY
        process = env.process(vat.cheese_vat_process(env, anomaly_probability))
        return vat, process


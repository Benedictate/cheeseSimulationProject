import simpy
import random

# --- Simulation Constants ---
STEP_DURATION_SEC = 15  # Each step is 15 seconds
TOTAL_MILK = 10000.00  # Total milk to process (liters)
MILK_FLOW_RATE = 5.00  # Liters per second
MILK_PER_STEP = MILK_FLOW_RATE * STEP_DURATION_SEC  # Liters per step

# --- Temperature Thresholds (°C) ---
INITIAL_TEMP = 20.00  # Starting temperature
TEMP_OPTIMAL_MIN = 31.00  # Minimum optimal temperature
TEMP_OPTIMAL_MAX = 33.00  # Maximum optimal temperature
TEMP_COOKING = 39.00  # Target temperature for cooking

# --- pH Thresholds ---
INITIAL_PH = 6.70  # Starting pH
OPTIMAL_PH = 6.55  # Optimal pH for rennet

# --- Time Durations (minutes) ---
HEATING_DURATION = 60  # 1 hour for heating milk
RENNET_DOSING_DURATION = 2  # 2 minutes for rennet dosing
RENNET_STIRRING_DURATION = 5  # 5 minutes for gentle stirring
COAGULATION_DURATION = 45  # 45 minutes for coagulation
NORMAL_CUTTING_DURATION = 10  # 10 minutes for normal cutting
EXTENDED_CUTTING_DURATION = 20  # Extended cutting time with issues
STIRRING_COOKING_DURATION = 20  # 20 minutes for cooking to reach optimal temperature
STIRRING_STIRING_DURATION = 30  # 30 minutes for stirring at optimal temperature
WHEY_RELEASE_DURATION = 20  # 20 minutes for whey release

# --- Step Calculations ---
STEPS_PER_MIN = 60 // STEP_DURATION_SEC  # Steps per minute
STEPS_HEATING = HEATING_DURATION * STEPS_PER_MIN
STEPS_RENNET_DOSING = RENNET_DOSING_DURATION * STEPS_PER_MIN
STEPS_RENNET_STIRRING = RENNET_STIRRING_DURATION * STEPS_PER_MIN
STEPS_COAGULATION = COAGULATION_DURATION * STEPS_PER_MIN
STEPS_NORMAL_CUTTING = NORMAL_CUTTING_DURATION * STEPS_PER_MIN
STEPS_EXTENDED_CUTTING = EXTENDED_CUTTING_DURATION * STEPS_PER_MIN
STEPS_STIRRING_COOKING = STIRRING_COOKING_DURATION * STEPS_PER_MIN
STEPS_STIRRING = STIRRING_STIRING_DURATION * STEPS_PER_MIN
STEPS_WHEY_RELEASE = WHEY_RELEASE_DURATION * STEPS_PER_MIN

# --- Conversion Rates (Industry Standards) ---
MILK_TO_CURD_NORMAL = 0.12  # 12% milk to curd conversion rate (industry standard)
MILK_TO_WHEY_NORMAL = 0.88  # 88% milk to whey conversion rate

# --- Anomaly Settings ---
DEFAULT_ANOMALY_PROBABILITY = 10  # Default 10% chance of anomaly
# Weights for different anomaly types (higher = more likely)
ANOMALY_WEIGHTS = {
    "temperature": 3,
    "rennet": 3,
    "ph": 1,
    "cutting": 2,
    "stirring": 2,
    "whey_release": 2
}


def format_sim_time(sim_time):
    """Convert simulation time to HH:MM:SS format."""
    total_seconds = sim_time * STEP_DURATION_SEC
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"


def cheese_vat_process(env, anomaly_probability=DEFAULT_ANOMALY_PROBABILITY):
    """Cheese vat simulation for cheddar production."""
    # State variables
    milk_amount = 0.00
    whey_amount = 0.00
    curd_amount = 0.00
    temperature = INITIAL_TEMP
    pH = INITIAL_PH
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
                weights = [ANOMALY_WEIGHTS["temperature"], ANOMALY_WEIGHTS["temperature"]]
            elif stage == "rennet":
                possible_anomalies = ["rennet_low", "rennet_high", "ph_off"]
                weights = [ANOMALY_WEIGHTS["rennet"], ANOMALY_WEIGHTS["rennet"], ANOMALY_WEIGHTS["ph"]]
            elif stage == "cutting":
                possible_anomalies = ["cutting_uneven", "cutting_mechanical"]
                weights = [ANOMALY_WEIGHTS["cutting"], ANOMALY_WEIGHTS["cutting"]]
            elif stage == "stirring":
                possible_anomalies = ["stirring_excessive", "stirring_uneven"]
                weights = [ANOMALY_WEIGHTS["stirring"], ANOMALY_WEIGHTS["stirring"]]
            elif stage == "whey_release":
                possible_anomalies = ["drain_clogged", "drain_too_fast"]
                weights = [ANOMALY_WEIGHTS["whey_release"], ANOMALY_WEIGHTS["whey_release"]]
            
            if possible_anomalies:
                return random.choices(possible_anomalies, weights=weights, k=1)[0]
        return None
    
    # Print header with wide column widths
    print(f"{'Time':<15} {'Phase':<50} {'Milk (L)':<20} {'Whey (L)':<20} {'Curd (L)':<20} {'Temp (°C)':<15} {'pH':<10} {'Anomalies':<100}")
    print("-" * 250)
    
    # --- Step 1: Fill the vat ---
    # Start with empty vat
    print(f"{format_sim_time(env.now):<15} {'Filling Vat':<50} {milk_amount:<20.2f} {whey_amount:<20.2f} {curd_amount:<20.2f} {temperature:<15.1f} {pH:<10.2f}")
    
    # Calculate first milk addition
    pending_changes["milk"] = MILK_PER_STEP
    
    # Simulate filling
    while milk_amount < TOTAL_MILK:
        # Apply pending changes from previous step
        milk_amount += pending_changes["milk"]
        pending_changes["milk"] = 0
        
        # Calculate next milk addition
        fill_amount = min(MILK_PER_STEP, TOTAL_MILK - milk_amount)
        if fill_amount > 0:
            pending_changes["milk"] = fill_amount
        
        yield env.timeout(1)  # Each step is 1 unit in simulation time
        
        if milk_amount < TOTAL_MILK:
            print(f"{format_sim_time(env.now):<15} {'Filling Vat':<50} {milk_amount:<20.2f} {whey_amount:<20.2f} {curd_amount:<20.2f} {temperature:<15.1f} {pH:<10.2f}")
    
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
        target_temp = round(random.uniform(TEMP_OPTIMAL_MIN, TEMP_OPTIMAL_MAX), 1)
    
    # Simulate heating with data at every 15-second interval
    temp_step = (target_temp - temperature) / STEPS_HEATING
    
    for step in range(STEPS_HEATING):
        # Apply pending changes from previous step
        temperature += pending_changes["temp"]
        pending_changes["temp"] = 0
        
        # Calculate next temperature change
        pending_changes["temp"] = temp_step
        
        print(f"{format_sim_time(env.now):<15} {'Heating Milk':<50} {milk_amount:<20.2f} {whey_amount:<20.2f} {curd_amount:<20.2f} {temperature:<15.1f} {pH:<10.2f} {', '.join(anomalies):<100}")
        yield env.timeout(1)
    
    # Apply final temperature change
    temperature += pending_changes["temp"]
    pending_changes["temp"] = 0
    temperature = round(target_temp, 1)  # Ensure we hit the exact target
    
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
    
    # Rennet dosing (2 minutes)
    for step in range(STEPS_RENNET_DOSING):
        # Apply pending changes
        pH += pending_changes["ph"]
        pending_changes["ph"] = 0
        
        print(f"{format_sim_time(env.now):<15} {'Rennet Dosing':<50} {milk_amount:<20.2f} {whey_amount:<20.2f} {curd_amount:<20.2f} {temperature:<15.1f} {pH:<10.2f} {', '.join(anomalies):<100}")
        yield env.timeout(1)
    
    # Gentle stirring (5 minutes)
    for step in range(STEPS_RENNET_STIRRING):
        print(f"{format_sim_time(env.now):<15} {'Gentle Stirring (for rennet)':<50} {milk_amount:<20.2f} {whey_amount:<20.2f} {curd_amount:<20.2f} {temperature:<15.1f} {pH:<10.2f} {', '.join(anomalies):<100}")
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
        curd_factor = MILK_TO_CURD_NORMAL
        conversion_rate = 1.0
    
    # Calculate milk conversion per step
    milk_per_step = milk_amount / STEPS_COAGULATION * conversion_rate
    
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
    
    # Simulate coagulation with data at every 15-second interval
    for step in range(STEPS_COAGULATION):
        # Apply pending changes
        milk_amount -= pending_changes["milk"]
        curd_amount += pending_changes["curd"]
        whey_amount += pending_changes["whey"]
        pending_changes["milk"] = 0
        pending_changes["curd"] = 0
        pending_changes["whey"] = 0
        
        # Cycle through descriptions
        description_idx = step % len(coagulation_descriptions)
        description = f"Coagulation: {coagulation_descriptions[description_idx]}"
        
        # Calculate next conversion
        if milk_amount > 0:
            milk_converted = min(milk_per_step, milk_amount)
            pending_changes["milk"] = milk_converted
            pending_changes["curd"] = milk_converted * curd_factor
            pending_changes["whey"] = milk_converted * (1 - curd_factor)
        
        print(f"{format_sim_time(env.now):<15} {description:<50} {milk_amount:<20.2f} {whey_amount:<20.2f} {curd_amount:<20.2f} {temperature:<15.1f} {pH:<10.2f} {', '.join(anomalies):<100}")
        yield env.timeout(1)
    
    # Apply final pending changes
    milk_amount -= pending_changes["milk"]
    curd_amount += pending_changes["curd"]
    whey_amount += pending_changes["whey"]
    pending_changes["milk"] = 0
    pending_changes["curd"] = 0
    pending_changes["whey"] = 0
    
    # --- Step 5: Cutting phase ---
    # Check for cutting anomaly
    cutting_anomaly = check_anomaly("cutting")
    
    if cutting_anomaly == "cutting_uneven":
        anomalies.append("Inconsistent cutting pattern")
        anomaly_effects["uneven_curds"] = True
    elif cutting_anomaly == "cutting_mechanical":
        anomalies.append("Mechanical fault / dull blade")
        anomaly_effects["uneven_curds"] = True
    
    # Determine cutting time based on anomalies
    if anomaly_effects["weak_curds"] or anomaly_effects["small_curds"]:
        cutting_time = STEPS_EXTENDED_CUTTING
        cutting_desc = "Cutting (delayed - soft curd)"
    elif anomaly_effects["rubbery_curds"]:
        cutting_time = STEPS_NORMAL_CUTTING  # Normal time but with resistance
        cutting_desc = "Cutting (resistance - firm curd)"
    else:
        cutting_time = STEPS_NORMAL_CUTTING
        cutting_desc = "Cutting"
    
    # During cutting, more whey is released from curd
    initial_curd = curd_amount
    whey_release_per_step = initial_curd * 0.2 / cutting_time
    
    for step in range(int(cutting_time)):
        # Apply pending changes
        curd_amount -= pending_changes["curd"]
        whey_amount += pending_changes["whey"]
        pending_changes["curd"] = 0
        pending_changes["whey"] = 0
        
        # Calculate next whey release
        whey_released = min(whey_release_per_step, curd_amount * 0.01)  # Max 1% per step
        pending_changes["curd"] = whey_released
        pending_changes["whey"] = whey_released
        
        # Determine description based on conditions
        if anomaly_effects["uneven_curds"]:
            desc = f"{cutting_desc} (uneven particle sizes)"
        elif anomaly_effects["weak_curds"] or anomaly_effects["small_curds"]:
            desc = f"{cutting_desc} (challenging due to curd properties)"
        else:
            desc = cutting_desc
        
        print(f"{format_sim_time(env.now):<15} {desc:<50} {milk_amount:<20.2f} {whey_amount:<20.2f} {curd_amount:<20.2f} {temperature:<15.1f} {pH:<10.2f} {', '.join(anomalies):<100}")
        yield env.timeout(1)
    
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
        whey_factor = 0.2  # 2% of curd becomes whey
        curd_loss_factor = 0.025  # 2.5% curd loss due to fines (very fine curd, likely going to be washed away)
    elif anomaly_effects["uneven_curds"]:
        whey_factor = 0.15  # 15% of curd becomes whey
        curd_loss_factor = 0.01  # 1% curd loss
    elif anomaly_effects["weak_curds"] or anomaly_effects["small_curds"]:
        whey_factor = 0.20  # 20% of curd becomes whey
        curd_loss_factor = 0.015  # 1.5% curd loss
    else:
        whey_factor = 0.20  # 20% of curd becomes whey
        curd_loss_factor = 0
    
    initial_curd = curd_amount
    whey_release_per_step = initial_curd * whey_factor / STEPS_STIRRING_COOKING
    curd_loss_per_step = initial_curd * curd_loss_factor / STEPS_STIRRING_COOKING
    
    # Gradually increase temperature from current to cooking temp
    temp_step = (TEMP_COOKING - temperature) / STEPS_STIRRING_COOKING
    
    for step in range(STEPS_STIRRING_COOKING):
        # Apply pending changes
        temperature += pending_changes["temp"]
        curd_amount -= pending_changes["curd"]
        whey_amount += pending_changes["whey"]
        pending_changes["temp"] = 0
        pending_changes["curd"] = 0
        pending_changes["whey"] = 0
        
        # Calculate next temperature change
        pending_changes["temp"] = temp_step
        
        print(f"{format_sim_time(env.now):<15} {'Cooking (heating temperature)':<50} {milk_amount:<20.2f} {whey_amount:<20.2f} {curd_amount:<20.2f} {temperature:<15.1f} {pH:<10.2f} {', '.join(anomalies):<100}")
        yield env.timeout(1)
    
    # Apply final temperature change
    temperature += pending_changes["temp"]
    pending_changes["temp"] = 0
    temperature = TEMP_COOKING  # Ensure we hit the exact target
    
    for step in range(STEPS_STIRRING):
        # Apply pending changes
        curd_amount -= pending_changes["curd"]
        whey_amount += pending_changes["whey"]
        pending_changes["curd"] = 0
        pending_changes["whey"] = 0
        
        # Calculate next whey release and curd loss
        if curd_amount > 0:
            whey_released = min(whey_release_per_step, curd_amount * 0.02)  # Max 2% per step
            pending_changes["curd"] = whey_released
            pending_changes["whey"] = whey_released
            
            if curd_loss_factor > 0:
                curd_lost = min(curd_loss_per_step, curd_amount * 0.01)  # Max 1% per step
                pending_changes["curd"] += curd_lost
        
        # Description based on conditions
        if stirring_anomaly == "stirring_excessive":
            desc = "Stirring and Cooking (excessive shear force)"
        elif stirring_anomaly == "stirring_uneven":
            desc = "Stirring and Cooking (uneven heating)"
        elif anomaly_effects["weak_curds"] or anomaly_effects["small_curds"]:
            desc = "Stirring and Cooking (curd breaking apart)"
        else:
            desc = "Stirring and Cooking"
        
        print(f"{format_sim_time(env.now):<15} {desc:<50} {milk_amount:<20.2f} {whey_amount:<20.2f} {curd_amount:<20.2f} {temperature:<15.1f} {pH:<10.2f} {', '.join(anomalies):<100}")
        yield env.timeout(1)
    
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
    
    # Original whey amount
    original_whey = whey_amount
    whey_per_step = original_whey / STEPS_WHEY_RELEASE * drain_factor
    
    for step in range(STEPS_WHEY_RELEASE):
        # Apply pending changes
        whey_amount -= pending_changes["whey"]
        curd_amount -= pending_changes["curd"]
        pending_changes["whey"] = 0
        pending_changes["curd"] = 0
        
        # Calculate next whey drain
        whey_to_drain = min(whey_per_step, whey_amount)
        pending_changes["whey"] = whey_to_drain
        
        # Curd loss calculation - more pronounced as draining progresses
        if curd_amount > 0 and curd_loss_factor > 0:
            # Progressive loss - more pronounced in middle of draining
            drain_progress = step / STEPS_WHEY_RELEASE
            # Bell curve effect - peak loss in middle of draining
            progress_factor = 4 * drain_progress * (1 - drain_progress)
            curd_loss = curd_amount * curd_loss_factor * progress_factor / STEPS_WHEY_RELEASE
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
        
        print(f"{format_sim_time(env.now):<15} {desc:<50} {milk_amount:<20.2f} {whey_amount:<20.2f} {curd_amount:<20.2f} {temperature:<15.1f} {pH:<10.2f} {', '.join(anomalies):<100}")
        yield env.timeout(1)
    
    # Apply final pending changes
    whey_amount -= pending_changes["whey"]
    curd_amount -= pending_changes["curd"]
    pending_changes["whey"] = 0
    pending_changes["curd"] = 0
    
    # --- Step 8: Curd storage ---
    print(f"{format_sim_time(env.now):<15} {'Curd Stored for Processing':<50} {milk_amount:<20.2f} {whey_amount:<20.2f} {curd_amount:<20.2f} {temperature:<15.1f} {pH:<10.2f} {', '.join(anomalies):<100}")
    
    # --- Final Report ---
    print("\n" + "=" * 150)
    print("SIMULATION COMPLETE".center(150))
    print("=" * 150)
    print(f"Total milk processed: {TOTAL_MILK:.2f}L")
    print(f"Final curd amount: {curd_amount:.2f}L ({curd_amount/TOTAL_MILK*100:.1f}%)")
    print(f"Final whey amount: {whey_amount:.2f}L ({whey_amount/TOTAL_MILK*100:.1f}%)")
    print(f"Remaining milk: {milk_amount:.2f}L ({milk_amount/TOTAL_MILK*100:.1f}%)")
    
    # Report anomaly effects
    active_effects = [effect.replace("_", " ").title() for effect, active in anomaly_effects.items() if active]
    if active_effects:
        print(f"Anomaly effects: {', '.join(active_effects)}")
    
    print(f"Anomalies detected: {', '.join(anomalies)}")


def run_cheese_vat_sim(anomaly_probability=DEFAULT_ANOMALY_PROBABILITY):
    """Initialize and run the simulation."""
    print(f"Running cheese vat simulation with {anomaly_probability}% anomaly probability...")
    env = simpy.Environment()
    env.process(cheese_vat_process(env, anomaly_probability))
    env.run(until=10000)  # Run for a long time to ensure completion


if __name__ == "__main__":
    print("Cheese Vat Simulation for Cheddar Production")
    print(f"Anomaly probability: {DEFAULT_ANOMALY_PROBABILITY}%")
    print()
    run_cheese_vat_sim()
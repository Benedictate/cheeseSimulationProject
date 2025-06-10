import random
from datetime import datetime, timedelta, timezone


INPUT_VOLUME = 1500.0       # Total volume of both curd and whey in liters
INITIAL_WHEY = INPUT_VOLUME * 0.65  # 65% of mixture is whey (based on research)
INITIAL_CURD = INPUT_VOLUME - INITIAL_WHEY  # Remaining 35% is curd
INITIAL_MOISTURE = 80.0     # Starting moisture % (liquid-ish state)
TARGET_MOISTURE = 58.0      # Target moisture % in final curd (industry standard)
DRAIN_TIME = 60             # Total draining time in minutes
TEMP_START = 38.0           # Starting temp
TEMP_END = 32.0             # End temp

def whey_draining():

    # Initialize process variables with starting values
    curd = INITIAL_CURD  #Current curd volume will decrease
    whey_remaining = INITIAL_WHEY  # Whey left to drain
    moisture = INITIAL_MOISTURE  #current curd moisture
    temp = TEMP_START
    time_elapsed = 0
    
    # Record start time in UTC
    start_time = datetime.now(timezone.utc)

    # based on industry, draning to be done in about 12 interval
    intervals = DRAIN_TIME // 5
    moisture_drop_per_interval = (INITIAL_MOISTURE - TARGET_MOISTURE) / intervals # moisture drops from 80% to 58% , Total drop = 22%
    whey_drained_per_interval = INITIAL_WHEY / intervals  #975L (65% of 1500L), 12 intervals, 975 / 12, therefore around 81.25L each time 

    #header info
    print("\nWhey Draining Simulation")
    print(f"Initial Mix: {INPUT_VOLUME:.0f}L | Whey: {INITIAL_WHEY:.1f}L | Curd: {INITIAL_CURD:.1f}L")
    print("Time (UTC)          | Time(min) | Temp(C) | Whey Remaining(L) | Curd(L) | Moisture(%)")
    print("----------------------------------------------------------------------------------------")

     #ensure time not over 60 min, add 0.1 variance to end moisture so it doesnt keep looping 
    while time_elapsed <= DRAIN_TIME and moisture > TARGET_MOISTURE + 0.1:
        
        # Calc curr time and temp
        current_time = start_time + timedelta(minutes=time_elapsed)
        temp = TEMP_START - ((TEMP_START - TEMP_END) / DRAIN_TIME) * time_elapsed

        # Simulate whey drainage, drain 5% slower or drain 5% faster, account for randomnness in machine
        drained = min(whey_drained_per_interval * random.uniform(0.95, 1.05), whey_remaining)
        whey_remaining -= drained

        # Calc small curd loss with random variation
        curd_loss = curd * random.uniform(0.002, 0.005)
        curd -= curd_loss

        # Reduce moisture with random variation, but not below target
        moisture = max(TARGET_MOISTURE, moisture - moisture_drop_per_interval * random.uniform(0.95, 1.05))

        # Display current status
        print(f"{current_time.strftime('%Y-%m-%d %H:%M:%S')} | {time_elapsed:03d}       | {temp:7.1f} | {whey_remaining:12.1f}      | {curd:7.1f} | {moisture:9.1f}")

        # Increment time by 5 minutes for next interval
        time_elapsed += 5


    print("\n--- Process Complete ---")
    print(f"Final Curd: {curd:.1f}L | Moisture: {moisture:.1f}%")
    print(f"Total Time: {time_elapsed-5} minutes")

# Start the whey draining simulation
whey_draining()

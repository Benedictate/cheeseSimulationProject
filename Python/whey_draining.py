import random

INPUT_VOLUME = 1500.0 #defined as total volume of both curd and whey 
INITIAL_WHEY = INPUT_VOLUME * 0.65 #based on research 65% of miture is whey 
INITIAL_CURD = INPUT_VOLUME - INITIAL_WHEY #35% whey 
INITIAL_MOISTURE = 80.0   # 80*% starting based on its being liquid-ish state 
TARGET_MOISTURE = 58.0    # moisture % in curd at end of draining acc to industry
DRAIN_TIME = 60           # Total draining time in minutes
TEMP_START = 38.0         # 
TEMP_END = 32.0           # temp change acc to industry 

def whey_draining():
    curd = INITIAL_CURD #Current curd volume will decrease
    whey_remaining = INITIAL_WHEY  ## Whey left to drain 
    moisture = INITIAL_MOISTURE # Current curd moisture
    temp = TEMP_START
    time_elapsed = 0

    print(f"\nWhey Draining Simulation")
    print(f"Initial Mix: {INPUT_VOLUME:.0f}L | Whey: {INITIAL_WHEY:.1f}L | Curd: {INITIAL_CURD:.1f}L")
    print("Time(min)  Temp(C)  Whey Remaining(L)  Curd(L)  Moisture(%)")
    print("------------------------------------------------------------")

    # based on industry, draning to be done in about 12 intervals 
    intervals = DRAIN_TIME // 5
    moisture_drop_per_interval = (INITIAL_MOISTURE - TARGET_MOISTURE) / intervals # moisture drops from 80% to 58% , Total drop = 22%
    whey_drained_per_interval = INITIAL_WHEY / intervals #975L (65% of 1500L), 12 intervals, 975 / 12, therefore around 81.25L each time 

    while time_elapsed <= DRAIN_TIME and moisture > TARGET_MOISTURE + 0.1: #ensure time not over 60 min, add 0.1 variance to end moisture so it doesnt keep looping 
        
        temp = TEMP_START - ((TEMP_START - TEMP_END) / DRAIN_TIME) * time_elapsed #At 60min:  38°C - (0.1 * 60)  = 32°C, linear so end temp = drain_time to simualte end

        # Simulate whey drainage, drain 5% slower or drain 5% faster, account for randomnness in machine
        drained = min(whey_drained_per_interval * random.uniform(0.95, 1.05), whey_remaining)
        whey_remaining -= drained

        # Simulate curd loss in process, 
        curd_loss = curd * random.uniform(0.002, 0.005)
        curd -= curd_loss

        # Simulate moisture drop
        moisture = max(TARGET_MOISTURE, moisture - moisture_drop_per_interval * random.uniform(0.95, 1.05))

        # Print every 5 minutes
        print(f"{time_elapsed:03d}   {temp:7.1f}     {whey_remaining:12.1f}    {curd:7.1f}     {moisture:9.1f}")

        time_elapsed += 5

    print("\n--- Process Complete ---")
    print(f"Final Curd: {curd:.1f}L | Moisture: {moisture:.1f}%")
    print(f"Total Time: {time_elapsed-5} minutes")

whey_draining()


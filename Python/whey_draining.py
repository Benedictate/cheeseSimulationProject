import random
from datetime import datetime, timedelta, timezone

class WheyDrainer:
    def __init__(self):
        #Constants for class attributes
        self.INPUT_VOLUME = 1500.0       #Total volume of both curd and whey in l
        self.INITIAL_WHEY = self.INPUT_VOLUME * 0.65  #65% of mixture is whey (based on research)
        self.INITIAL_CURD = self.INPUT_VOLUME - self.INITIAL_WHEY  #Remaining 35% is curd
        self.INITIAL_MOISTURE = 80.0     #Starting moisture % (liquid-ish state)
        self.TARGET_MOISTURE = 58.0      #Target moisture % in final curd (industry standard)
        self.DRAIN_TIME = 60             #Total draining time in minutes
        self.TEMP_START = 38.0           #Start temp
        self.TEMP_END = 32.0             #End temp
        
        #Process variables of conditions
        self.curd = self.INITIAL_CURD    # Curr curd volume will decrease
        self.whey_remaining = self.INITIAL_WHEY  #Whey left to drain
        self.moisture = self.INITIAL_MOISTURE  #curr curd moisture
        self.temp = self.TEMP_START
        self.time_elapsed = 0
        self.start_time = None  #Will be set when process starts

    def run(self):
        """Main method that runs the whey draining simulation (equivalent to original whey_draining() function)"""
        # Initialize process variables w start values
        self.curd = self.INITIAL_CURD
        self.whey_remaining = self.INITIAL_WHEY
        self.moisture = self.INITIAL_MOISTURE
        self.temp = self.TEMP_START
        self.time_elapsed = 0
        
        # Record start time in UTC
        self.start_time = datetime.now(timezone.utc)

        # based on industry, draining to be done in about 12 intervals
        intervals = self.DRAIN_TIME // 5
        moisture_drop_per_interval = (self.INITIAL_MOISTURE - self.TARGET_MOISTURE) / intervals # moisture drops from 80% to 58%, Total drop = 22%
        whey_drained_per_interval = self.INITIAL_WHEY / intervals  #975L (65% of 1500L), 12 intervals, 975 / 12, therefore around 81.25L each time 

        #header info
        print("\nWhey Draining Simulation")
        print(f"Initial Mix: {self.INPUT_VOLUME:.0f}L | Whey: {self.INITIAL_WHEY:.1f}L | Curd: {self.INITIAL_CURD:.1f}L")
        print("Time (UTC)          | Time(min) | Temp(C) | Whey Remaining(L) | Curd(L) | Moisture(%)")
        print("----------------------------------------------------------------------------------------")

        #ensure time not over 60 min, add 0.1 variance to end moisture so it doesnt keep looping 
        while self.time_elapsed <= self.DRAIN_TIME and self.moisture > self.TARGET_MOISTURE + 0.1:
            
            # Calc curr time and temp
            current_time = self.start_time + timedelta(minutes=self.time_elapsed)
            self.temp = self.TEMP_START - ((self.TEMP_START - self.TEMP_END) / self.DRAIN_TIME) * self.time_elapsed

            # Simulate whey drainage, drain 5% slower or drain 5% faster, account for randomnness in machine
            drained = min(whey_drained_per_interval * random.uniform(0.95, 1.05), self.whey_remaining)
            self.whey_remaining -= drained

            # Calc small curd loss with random variation
            curd_loss = self.curd * random.uniform(0.002, 0.005)
            self.curd -= curd_loss

            # Reduce moisture with random variation, but not below target
            self.moisture = max(self.TARGET_MOISTURE, self.moisture - moisture_drop_per_interval * random.uniform(0.95, 1.05))

            # Display current status
            print(f"{current_time.strftime('%Y-%m-%d %H:%M:%S')} | {self.time_elapsed:03d}       | {self.temp:7.1f} | {self.whey_remaining:12.1f}      | {self.curd:7.1f} | {self.moisture:9.1f}")

            # Increment time by 5 minutes for next interval
            self.time_elapsed += 5

        print("\n--- Process Complete ---")
        print(f"Final Curd: {self.curd:.1f}L | Moisture: {self.moisture:.1f}%")
        print(f"Total Time: {self.time_elapsed-5} minutes")


#Start the whey draining simulation
if __name__ == "__main__":
    drainer = WheyDrainer()  #Create instance of our machine
    drainer.run()  #calling whey_draining

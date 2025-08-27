import simpy
import time
from enum import Enum, auto

class TimeMode(Enum):
    ST = auto()  # Simulation Time
    RT = auto()  # Real Time

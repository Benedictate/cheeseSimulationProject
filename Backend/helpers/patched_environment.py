import simpy
import time
import simpy.rt
from enum import Enum, auto

class TimeMode(Enum):
    ST = auto()  # Simulation Time
    RT = auto()  # Real Time

def create_env(real_time=False, factor=1.0, strict=True):
    # Use a single SimPy environment for the whole pipeline so sim-time flows naturally
    if real_time:
        return simpy.rt.RealtimeEnvironment(factor=factor, strict=strict)
    return simpy.Environment()
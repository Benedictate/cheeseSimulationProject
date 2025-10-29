import json
import os
from typing import Any, Dict, Optional, Union


class NdjsonLogger:
    """Append-only NDJSON logger with a normalized event schema.

    Use log_event to write one JSON object per line to `data.ndjson`.
    Later, call finalize_json to convert the NDJSON stream into an array and
    write it to `data.json`.
    """

    def __init__(self, ndjson_path: str = "Backend/data/data.ndjson", final_json_path: str = "Backend/data/data.json", stream: bool = True):
        self.ndjson_path = ndjson_path
        self.final_json_path = final_json_path
        self.stream = stream
        os.makedirs(os.path.dirname(self.ndjson_path), exist_ok=True)

        # Truncate file at start of run to avoid mixing runs
        open(self.ndjson_path, "w").close()
        # Global, monotonically increasing simulation minute index (1,2,3,...)
        self._sim_minute_sequence = 1
        # Persist the latest known values across events to satisfy carry-forward requirement
        self._last_state: Dict[str, Any] = {}

    def log_event(self, event: Dict[str, Any]) -> None:
        """Write a single normalized event as one NDJSON line.

        Enforces a unique, strictly increasing integer in event['sim_time_min']
        starting at 1. If the caller provided a 'sim_time_min', it will be
        preserved under 'env_time_min' and replaced with the global sequence to
        guarantee no duplicates as requested.
        """
        # Carry forward: merge with last known state so unchanged fields persist
        if self._last_state:
            merged = dict(self._last_state)
            merged.update(event)
        else:
            merged = dict(event)

        # Normalize provided time field and preserve original
        if "sim_time" in merged:
            merged["env_time"] = merged["sim_time"]
        elif "sim_time_min" in merged:
            # Backward-compat for callers still sending sim_time_min
            merged["env_time"] = merged["sim_time_min"]
        # Overwrite with unique global sequence number
        merged["sim_time"] = self._sim_minute_sequence
        # Remove legacy key if present to avoid duplicates in output
        if "sim_time_min" in merged:
            del merged["sim_time_min"]
        self._sim_minute_sequence += 1
        # Update last_state AFTER assigning sequence so it contains latest values
        self._last_state = dict(merged)
        with open(self.ndjson_path, "a") as f:
            json.dump(merged, f)
            f.write("\n")
            if self.stream:
                f.flush()
                os.fsync(f.fileno())

    def finalize_json(self) -> None:
        """Convert NDJSON stream to a JSON array file for convenient reading."""
        if not os.path.exists(self.ndjson_path):
            # Nothing to finalize
            with open(self.final_json_path, "w") as f:
                json.dump([], f, indent=4)
            return

        with open(self.ndjson_path) as f:
            array = [json.loads(line) for line in f if line.strip()]

        # Reorder by machine phases to avoid interleaving, preserving within-machine order
        machine_order = [
            "pasteuriser",
            "cheese_vat",
            "curd_cutter",
            "whey_drainer",
            "cheddaring_and_milling",
            "salting_and_mellowing",
            "cheese_presser",
            "ripener",
        ]

        # Bucket by machine preserving original order
        buckets: Dict[str, list] = {name: [] for name in machine_order}
        others = []
        for ev in array:
            m = ev.get("machine")
            if m in buckets:
                buckets[m].append(ev)
            else:
                others.append(ev)

        ordered: list = []
        for name in machine_order:
            ordered.extend(buckets[name])
        # Append any unknown-machine events at the end in their original order
        ordered.extend(others)

        # Re-sequence sim_time to be strictly increasing in the final output
        for idx, ev in enumerate(ordered, start=1):
            # Preserve any prior value if present
            if "sim_time" in ev and "finalized_prev_sim_time" not in ev:
                ev["finalized_prev_sim_time"] = ev["sim_time"]
            ev["sim_time"] = idx

        with open(self.final_json_path, "w") as f:
            json.dump(ordered, f, indent=4)


def build_standard_event(
    *,
    machine: str,
    sim_time_min: float,
    utc_time: str,
    batch_id: Optional[Union[str, int]] = None,
    start_minute: Optional[float] = None,
    end_minute: Optional[float] = None,
    input_weight_kg: Optional[float] = None,
    output_weight_kg: Optional[float] = None,
    input_moisture_percent: Optional[float] = None,
    output_moisture_percent: Optional[float] = None,
    press_pressure_psi: Optional[float] = None,
    press_duration_min: Optional[float] = None,
    salt_kg: Optional[float] = None,
    temperature_C: Optional[float] = None,
    pH: Optional[float] = None,
    curd_L: Optional[float] = None,
    whey_L: Optional[float] = None,
    milk_L: Optional[float] = None,
    anomaly: Optional[bool] = None,
    maintenance_flag: Optional[bool] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Create a normalized schema object; any missing values default to 0 or None.

    All machines should call this and pass what they know. Unknown numeric fields
    default to 0 to keep structure consistent per requirements.
    """

    def zero_if_none(v):
        return 0 if v is None else v

    event: Dict[str, Any] = {
        "machine": machine,
        # Emit modern key; logger keeps sequence and removes legacy if present
        "sim_time": sim_time_min,
        "utc_time": utc_time,
        "batch_id": batch_id if batch_id is not None else 0,
        "start_minute": zero_if_none(start_minute),
        "end_minute": zero_if_none(end_minute),
        "input_weight_kg": zero_if_none(input_weight_kg),
        "output_weight_kg": zero_if_none(output_weight_kg),
        "input_moisture_percent": zero_if_none(input_moisture_percent),
        "output_moisture_percent": zero_if_none(output_moisture_percent),
        "press_pressure_psi": zero_if_none(press_pressure_psi),
        "press_duration_min": zero_if_none(press_duration_min),
        "salt_kg": zero_if_none(salt_kg),
        "temperature_C": zero_if_none(temperature_C),
        "pH": zero_if_none(pH),
        "curd_L": zero_if_none(curd_L),
        "whey_L": zero_if_none(whey_L),
        "milk_L": zero_if_none(milk_L),
        "anomaly": anomaly if anomaly is not None else False,
        "maintenance_flag": maintenance_flag if maintenance_flag is not None else False,
    }

    if extra:
        event.update(extra)

    return event



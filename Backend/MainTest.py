import json
import sys
import time
import os

def read_input():
    """Reads JSON input from stdin."""
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return {}
        return json.loads(raw)
    except Exception as e:
        print(json.dumps({"error": f"Invalid input JSON: {str(e)}"}))
        sys.exit(1)

# def simulate_full_json():
#     """Outputs one large JSON array."""
#     data = [{"step": i, "value": i * 2} for i in range(5)]
#     print(json.dumps({"mode": "full_json", "data": data}))
#     sys.stdout.flush()

def simulate_ndjson():
    """Outputs JSON objects line-by-line (NDJSON)."""
    for i in range(5000):
        obj = {"mode": "ndjson", "step": i, "value": i * 2}
        print(json.dumps(obj))
        sys.stdout.flush()
        time.sleep(1)  # simulate gradual output

def main():
    args = read_input()
    print(json.dumps({"received_args": args}))
    os.makedirs("Backend/data", exist_ok=True)

    simulate_ndjson()

    # # Toggle between JSON and NDJSON each run
    # toggle_file = "Backend/data/toggle.txt"
    # toggle_mode = "json"

    # if os.path.exists(toggle_file):
    #     with open(toggle_file, "r") as f:
    #         last_mode = f.read().strip()
    #         toggle_mode = "ndjson" if last_mode == "json" else "json"

    # # Save new toggle state
    # with open(toggle_file, "w") as f:
    #     f.write(toggle_mode)

    # # Perform the chosen simulation
    # if toggle_mode == "json":
        
    # else:
    #     simulate_ndjson()

if __name__ == "__main__":
    main()
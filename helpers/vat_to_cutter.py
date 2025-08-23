import simpy

def vat_to_cutter(env, input_store, output_store):
    batch_counter = 0
    while True:
        # wait until vat gives a float (volume)
        volume = yield input_store.get()

        # wrap float into dict with placeholders and batch_id
        batch = {
            "batch_id": f"batch_{batch_counter}",
            "total_milk_in": volume,  # renamed to match CurdCutter
            "avg_temperature": None,   # leave blank for now
            "final_pH": None,          # leave blank for now
            "anomalies": []            # start as empty list
        }

        batch_counter += 1

        # pass it to cutter
        yield output_store.put(batch)

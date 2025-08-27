import simpy

def pasteuriser_to_vat(env, input_store, output_store, target_volume):
    buffer = 0  # accumulated volume
    while True:
        item = yield input_store.get()  # get next input (can vary)
        buffer += item
        
        # Create as many full outputs as possible
        while buffer >= target_volume:
            yield output_store.put(target_volume)
            buffer -= target_volume

def presser_to_ripener(env, presser_output, ripener_input):
    while True:
        # Wait for a batch from the presser
        batch = yield presser_output.get()

        # Convert to ripener input
        block_weight = batch['output_weight_kg']

        # Put into ripener input store
        yield ripener_input.put(block_weight)
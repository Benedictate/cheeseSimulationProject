def cheddaring_to_salting(env, input_store, output_store, slice_mass=0.1, generation_interval=5):
    slice_id = 0  # unique slice ID across all batches
    while True:
        # Get a new batch (plain number, kg)
        batch_mass = yield input_store.get()
        remaining_mass = batch_mass

        while remaining_mass > 0:
            slice_id += 1
            curd_slice = {
                'id': slice_id,
                'mass': min(slice_mass, remaining_mass),
                'salt': 0.0
            }
            remaining_mass -= curd_slice['mass']

            # Put slice into output store
            yield output_store.put(curd_slice)
            # Wait before creating next slice
            yield env.timeout(generation_interval)
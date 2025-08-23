import random

def salting_to_presser(env, input_conveyor, output_conveyor, target_weight_kg):

    batch_id = 1
    temp_slices = []

    while True:
        # Get a new slice from the input conveyor
        slice_ = yield input_conveyor.get()
        # Assign a random moisture if it doesn't exist
        if 'moisture' not in slice_:
            slice_['moisture'] = random.uniform(38, 42)
        temp_slices.append(slice_)

        # DEBUG: print each slice as it comes in
        #print(f"[{env.now:.2f} min] Got slice: mass={slice_['mass']:.2f}, moisture={slice_['moisture']:.2f}")

        # Calculate total mass of current accumulated slices
        total_mass = sum(s['mass'] for s in temp_slices)

        if total_mass >= target_weight_kg:
            # Aggregate slices into a single batch
            aggregated_batch = {
                'batch_id': f"Block{batch_id}",
                'input_weight_kg': total_mass,
                'input_moisture_percent': sum(s['mass'] * s['moisture'] for s in temp_slices) / total_mass,
                'salt': sum(s['salt'] for s in temp_slices),
                'press_duration_min': random.randint(45, 60),
                'press_pressure_psi': random.uniform(30, 60)
            }

            # DEBUG: print block info
            # print(f"[{env.now:.2f} min] Created {aggregated_batch['batch_id']} with "
            #       f"{len(temp_slices)} slices, total_mass={total_mass:.2f}, "
            #       f"avg_moisture={aggregated_batch['input_moisture_percent']:.2f}")

            # Put aggregated batch onto output conveyor
            yield output_conveyor.put(aggregated_batch)

            batch_id += 1
            temp_slices = []  # reset for next block

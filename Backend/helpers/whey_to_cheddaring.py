import simpy

def whey_to_cheddaring(env, input_store, output_store):

    while True:
        batch = yield input_store.get()
        curd_mass = batch['curd_final'] 
        yield output_store.put(curd_mass)
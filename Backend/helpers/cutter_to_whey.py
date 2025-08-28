import simpy

def cutter_to_whey(env, input_store, output_store, target_mass):
    total_milk = 0  
    while True:
        curd = yield input_store.get()  
        total_milk += curd['curd_mass'] + curd['whey_mass']
        
        if total_milk >= target_mass:
            yield output_store.put(total_milk)
            total_milk = 0 
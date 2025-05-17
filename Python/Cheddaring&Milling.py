import sympy as sp 

time = sp.Symbol('time')

#Constants
initial_curd_kg = 10
moisture_difference = 30
final_moisture = 45 #normally cheese is left with 45% moisture and starts with 75% moisture
decay_rate_before_milling = -0.02
decay_rate_after_milling = -0.025
milling_start_time=90
steepness_of_sigmoid=-0.05 #affects how fast cheese goes from soft to firm
max_texture_value=10


#Moisture decay formulas(one for rate before milling and one for after)
moisture_before = moisture_difference * sp.exp(decay_rate_before_milling * time) + final_moisture
moisture_after = moisture_difference * sp.exp(decay_rate_after_milling * (time - milling_start_time)) + final_moisture

#Texture formula (sigmoid function centered at 90)
texture_expr = max_texture_value / (1 + sp.exp(steepness_of_sigmoid * (time - milling_start_time)))

#Time points from 0 to 180 in 15-min steps as the cheese is normally checked every 15 minutes
time_points = list(range(0, 181, 15))

print(f"Starting curd: {initial_curd_kg:.2f} kg\n")
print("-" * 80)
print(f"{'Time (min)':<12} {'Moisture (%)':<15} {'Whey Lost (kg)':<20} {'Texture (0–10)':<18} {'Milled?'}")
print("-" * 80)

# Loop through 15 min timestamps
for t in time_points:
    milled = t >= milling_start_time
    if not milled:
        moisture = moisture_before.subs(time, t)
    else:
        moisture = moisture_after.subs(time, t)

    moisture = float(moisture.evalf())

    #calculating wheylost based on moisture
    whey_kg = ((100 - moisture) / 100) * initial_curd_kg

    #calculating texture
    texture = float(texture_expr.subs(time, t).evalf())

    print(f"{t:<12} {moisture:<15.2f} {whey_kg:<20.2f} {texture:<18.2f} {'Yes' if milled else 'No'}")


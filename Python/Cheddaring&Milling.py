import sympy as sp

# Declare symbols
time = sp.Symbol('time')

# Constants
initial_curd_kg = 10
moisture_difference = 30
final_moisture = 45
decay_rate_before_milling = -0.02
decay_rate_after_milling = -0.025

# Define expressions for moisture
moisture_before = moisture_difference * sp.exp(decay_rate_before_milling * time) + final_moisture
moisture_after = moisture_difference * sp.exp(decay_rate_after_milling * (time - 90)) + final_moisture

# Texture formula (sigmoid centered at 90)
texture_expr = 10 / (1 + sp.exp(-0.05 * (time - 90)))

# Create time points from 0 to 180 in 15-min steps
time_points = list(range(0, 181, 15))

# Print header
print(f"Starting curd: {initial_curd_kg:.2f} kg\n")
print("-" * 95)
print(f"{'Time (min)':<12} {'Moisture (%)':<15} {'Whey Lost (kg)':<20} {'Texture (0–10)':<18} {'Milled?'}")
print("-" * 95)

# Loop through time points
for t in time_points:
    milled = t >= 90
    if not milled:
        moisture = moisture_before.subs(time, t)
    else:
        moisture = moisture_after.subs(time, t)
    
    # Evaluate numerical result
    moisture = float(moisture.evalf())
    whey_kg = ((100 - moisture) / 100) * initial_curd_kg
    texture = float(texture_expr.subs(time, t).evalf())

    print(f"{t:<12} {moisture:<15.2f} {whey_kg:<20.2f} {texture:<18.2f} {'Yes' if milled else 'No'}")

print("-" * 95)

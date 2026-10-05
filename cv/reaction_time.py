# Simple RehabQuest reaction-time test

# Time when target appeared
target_time = 10.00

# Time when user started moving
movement_start_time = 10.72

# Calculate reaction time
reaction_time = movement_start_time - target_time

print("--------------------------------")
print("REHABQUEST REACTION TIME")
print("--------------------------------")

print(f"Target appeared at: {target_time:.2f} seconds")
print(f"Movement started at: {movement_start_time:.2f} seconds")
print(f"Reaction Time: {reaction_time:.2f} seconds")
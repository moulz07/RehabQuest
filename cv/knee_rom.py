import pandas as pd

# Load knee angle data
data = pd.read_csv("knee_angles.csv")

# Calculate minimum and maximum angles
left_min = data["Left_Knee_Angle"].min()
left_max = data["Left_Knee_Angle"].max()

right_min = data["Right_Knee_Angle"].min()
right_max = data["Right_Knee_Angle"].max()

# Calculate Range of Motion (ROM)
left_rom = left_max - left_min
right_rom = right_max - right_min

# Display results
print("Knee Range of Motion (ROM)")
print("--------------------------")

print(f"Left Knee:")
print(f"  Minimum Angle: {left_min:.2f}°")
print(f"  Maximum Angle: {left_max:.2f}°")
print(f"  ROM: {left_rom:.2f}°")

print()

print(f"Right Knee:")
print(f"  Minimum Angle: {right_min:.2f}°")
print(f"  Maximum Angle: {right_max:.2f}°")
print(f"  ROM: {right_rom:.2f}°")
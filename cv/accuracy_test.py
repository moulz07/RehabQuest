import csv
import math

# Target position
target_x = 0.8
target_y = 0.3

# Read movement data
with open("hand_movement.csv", "r") as file:

    reader = csv.DictReader(file)

    last_x = None
    last_y = None

    for row in reader:
        last_x = float(row["Wrist_X"])
        last_y = float(row["Wrist_Y"])


# Make sure we found hand data
if last_x is not None and last_y is not None:

    # Calculate distance between hand and target
    distance = math.sqrt(
        (target_x - last_x) ** 2 +
        (target_y - last_y) ** 2
    )

    # Convert distance into a simple accuracy score
    accuracy = max(0, (1 - distance) * 100)

    print("--------------------------------")
    print("REHABQUEST ACCURACY TEST")
    print("--------------------------------")

    print(f"Target X: {target_x}")
    print(f"Target Y: {target_y}")

    print(f"Hand X: {last_x:.4f}")
    print(f"Hand Y: {last_y:.4f}")

    print(f"Distance From Target: {distance:.4f}")
    print(f"Accuracy Score: {accuracy:.2f}%")

else:
    print("No hand movement data found.")
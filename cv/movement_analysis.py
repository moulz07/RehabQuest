import csv
import math

# Open the movement data
with open("hand_movement.csv", "r") as file:

    reader = csv.DictReader(file)

    previous_x = None
    previous_y = None
    previous_time = None

    total_distance = 0
    total_time = 0

    speeds = []

    for row in reader:

        x = float(row["Wrist_X"])
        y = float(row["Wrist_Y"])
        current_time = float(row["Time"])

        # If this is not the first point
        if previous_x is not None:

            # Calculate distance
            distance = math.sqrt(
                (x - previous_x) ** 2 +
                (y - previous_y) ** 2
            )

            # Calculate time difference
            time_difference = current_time - previous_time

            # Calculate speed
            if time_difference > 0:

                speed = distance / time_difference

                speeds.append(speed)

                total_distance += distance

        previous_x = x
        previous_y = y
        previous_time = current_time

    # Total time
    if previous_time is not None:
        total_time = previous_time

# Calculate average speed
if len(speeds) > 0:
    average_speed = sum(speeds) / len(speeds)
else:
    average_speed = 0

print("--------------------------------")
print("REHABQUEST MOVEMENT ANALYSIS")
print("--------------------------------")

print(f"Total Movement Distance: {total_distance:.4f}")
print(f"Total Movement Time: {total_time:.2f} seconds")
print(f"Average Movement Speed: {average_speed:.4f}")
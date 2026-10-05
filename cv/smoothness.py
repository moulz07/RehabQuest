import csv
import math

# Store movement speeds
speeds = []

# Open movement data
with open("hand_movement.csv", "r") as file:

    reader = csv.DictReader(file)

    previous_x = None
    previous_y = None
    previous_time = None

    for row in reader:

        x = float(row["Wrist_X"])
        y = float(row["Wrist_Y"])
        current_time = float(row["Time"])

        # Calculate speed between two points
        if previous_x is not None:

            distance = math.sqrt(
                (x - previous_x) ** 2 +
                (y - previous_y) ** 2
            )

            time_difference = current_time - previous_time

            if time_difference > 0:

                speed = distance / time_difference

                speeds.append(speed)

        previous_x = x
        previous_y = y
        previous_time = current_time


# Calculate smoothness
if len(speeds) > 1:

    changes = []

    for i in range(1, len(speeds)):

        change = abs(speeds[i] - speeds[i - 1])

        changes.append(change)

    average_speed_change = sum(changes) / len(changes)

    # Convert to a simple smoothness score
    smoothness_score = 100 / (1 + average_speed_change)

    print("--------------------------------")
    print("REHABQUEST MOVEMENT SMOOTHNESS")
    print("--------------------------------")

    print(f"Average Speed Change: {average_speed_change:.4f}")
    print(f"Smoothness Score: {smoothness_score:.2f}")

else:

    print("Not enough movement data.")
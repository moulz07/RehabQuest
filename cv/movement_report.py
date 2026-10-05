import csv
import math

# -----------------------------
# READ MOVEMENT DATA
# -----------------------------

with open("hand_movement.csv", "r") as file:

    reader = csv.DictReader(file)

    previous_x = None
    previous_y = None
    previous_time = None

    total_distance = 0
    speeds = []

    x_values = []
    y_values = []
    times = []

    for row in reader:

        x = float(row["Wrist_X"])
        y = float(row["Wrist_Y"])
        current_time = float(row["Time"])

        x_values.append(x)
        y_values.append(y)
        times.append(current_time)

        # Calculate distance and speed
        if previous_x is not None:

            distance = math.sqrt(
                (x - previous_x) ** 2 +
                (y - previous_y) ** 2
            )

            time_difference = current_time - previous_time

            total_distance += distance

            if time_difference > 0:
                speed = distance / time_difference
                speeds.append(speed)

        previous_x = x
        previous_y = y
        previous_time = current_time


# -----------------------------
# CALCULATE FEATURES
# -----------------------------

if x_values:

    # Speed
    if speeds:
        average_speed = sum(speeds) / len(speeds)
    else:
        average_speed = 0

    # Movement duration
    duration = max(times) - min(times)

    # Range of motion
    x_rom = max(x_values) - min(x_values)
    y_rom = max(y_values) - min(y_values)

    # -----------------------------
    # ACCURACY TEST
    # -----------------------------

    target_x = 0.8
    target_y = 0.3

    last_x = x_values[-1]
    last_y = y_values[-1]

    target_distance = math.sqrt(
        (target_x - last_x) ** 2 +
        (target_y - last_y) ** 2
    )

    accuracy = max(
        0,
        (1 - target_distance) * 100
    )

    # -----------------------------
    # REACTION TIME TEST
    # -----------------------------

    target_appearance_time = 10.00
    movement_start_time = 10.72

    reaction_time = (
        movement_start_time -
        target_appearance_time
    )


    # -----------------------------
    # DISPLAY REPORT
    # -----------------------------

    print()
    print("========================================")
    print("       REHABQUEST MOVEMENT REPORT")
    print("========================================")

    print()
    print(f"Total Movement Distance : {total_distance:.4f}")
    print(f"Average Movement Speed  : {average_speed:.4f}")
    print(f"X Range of Motion       : {x_rom:.4f}")
    print(f"Y Range of Motion       : {y_rom:.4f}")
    print(f"Movement Duration       : {duration:.3f} seconds")
    print(f"Accuracy Score          : {accuracy:.2f}%")
    print(f"Reaction Time           : {reaction_time:.2f} seconds")

    print()
    print("========================================")

else:

    print("No movement data found.")
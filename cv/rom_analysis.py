import csv

# Lists to store all X and Y coordinates
x_values = []
y_values = []

# Open movement data
with open("hand_movement.csv", "r") as file:

    reader = csv.DictReader(file)

    for row in reader:

        x = float(row["Wrist_X"])
        y = float(row["Wrist_Y"])

        x_values.append(x)
        y_values.append(y)


# Make sure data exists
if x_values and y_values:

    # Find minimum and maximum positions
    min_x = min(x_values)
    max_x = max(x_values)

    min_y = min(y_values)
    max_y = max(y_values)

    # Calculate range of motion
    x_rom = max_x - min_x
    y_rom = max_y - min_y

    print("--------------------------------")
    print("REHABQUEST RANGE OF MOTION")
    print("--------------------------------")

    print(f"Minimum X: {min_x:.4f}")
    print(f"Maximum X: {max_x:.4f}")

    print(f"Minimum Y: {min_y:.4f}")
    print(f"Maximum Y: {max_y:.4f}")

    print(f"X Range of Motion: {x_rom:.4f}")
    print(f"Y Range of Motion: {y_rom:.4f}")

else:

    print("No movement data found.")
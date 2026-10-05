import csv
import matplotlib.pyplot as plt

# Lists for coordinates
x_values = []
y_values = []

# Read movement data
with open("hand_movement.csv", "r") as file:

    reader = csv.DictReader(file)

    for row in reader:

        x_values.append(float(row["Wrist_X"]))
        y_values.append(float(row["Wrist_Y"]))


# Check if data exists
if x_values and y_values:

    # Create trajectory graph
    plt.figure(figsize=(8, 6))

    plt.plot(
        x_values,
        y_values,
        marker=".",
        markersize=2
    )

    # Mark starting point
    plt.scatter(
        x_values[0],
        y_values[0],
        label="Start"
    )

    # Mark ending point
    plt.scatter(
        x_values[-1],
        y_values[-1],
        label="End"
    )

    plt.title("RehabQuest Hand Movement Trajectory")
    plt.xlabel("Wrist X")
    plt.ylabel("Wrist Y")

    # Webcam Y coordinates increase downward,
    # so reverse the Y axis for easier visual interpretation.
    plt.gca().invert_yaxis()

    plt.legend()
    plt.grid(True)

    plt.show()

else:

    print("No movement data found.")
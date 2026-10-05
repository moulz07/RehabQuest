import csv

# Open movement data
with open("hand_movement.csv", "r") as file:

    reader = csv.DictReader(file)

    times = []

    for row in reader:
        times.append(float(row["Time"]))


# Check if data exists
if times:

    start_time = min(times)
    end_time = max(times)

    duration = end_time - start_time

    print("--------------------------------")
    print("REHABQUEST MOVEMENT DURATION")
    print("--------------------------------")

    print(f"Start Time: {start_time:.3f} seconds")
    print(f"End Time: {end_time:.3f} seconds")
    print(f"Movement Duration: {duration:.3f} seconds")

else:

    print("No movement data found.")
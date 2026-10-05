import csv

# Store left and right elbow angles
left_angles = []
right_angles = []


# Read the recorded joint-angle data
with open("joint_angles.csv", "r") as file:

    reader = csv.DictReader(file)

    for row in reader:

        left_angle = float(row["Left_Elbow_Angle"])
        right_angle = float(row["Right_Elbow_Angle"])

        left_angles.append(left_angle)
        right_angles.append(right_angle)


# Check whether data exists
if left_angles and right_angles:

    # LEFT ELBOW
    left_min = min(left_angles)
    left_max = max(left_angles)
    left_rom = left_max - left_min

    # RIGHT ELBOW
    right_min = min(right_angles)
    right_max = max(right_angles)
    right_rom = right_max - right_min


    print("----------------------------------------")
    print("REHABQUEST ELBOW RANGE OF MOTION")
    print("----------------------------------------")

    print()
    print("LEFT ELBOW")
    print(f"Minimum Angle : {left_min:.2f} degrees")
    print(f"Maximum Angle : {left_max:.2f} degrees")
    print(f"ROM           : {left_rom:.2f} degrees")

    print()
    print("RIGHT ELBOW")
    print(f"Minimum Angle : {right_min:.2f} degrees")
    print(f"Maximum Angle : {right_max:.2f} degrees")
    print(f"ROM           : {right_rom:.2f} degrees")

    print()
    print("----------------------------------------")

else:

    print("No joint-angle data found.")
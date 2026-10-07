import cv2
import mediapipe as mp
import math
import csv
import time


# ----------------------------------------
# Calculate angle between 3 points
# ----------------------------------------
def calculate_angle(a, b, c):

    angle = math.degrees(
        math.atan2(c[1] - b[1], c[0] - b[0])
        - math.atan2(a[1] - b[1], a[0] - b[0])
    )

    angle = abs(angle)

    if angle > 180:
        angle = 360 - angle

    return angle


# ----------------------------------------
# MediaPipe Pose
# ----------------------------------------
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

pose = mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)


# ----------------------------------------
# Open webcam
# ----------------------------------------
cap = cv2.VideoCapture(0)

# Try to disable autofocus
cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)

# Set a reasonable resolution
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)


# ----------------------------------------
# Create CSV file
# ----------------------------------------
file = open("knee_angles.csv", "w", newline="")

writer = csv.writer(file)

writer.writerow([
    "Time",
    "Left_Knee_Angle",
    "Right_Knee_Angle"
])


start_time = time.time()


print("----------------------------------------")
print("REHABQUEST KNEE ANGLE TRACKING")
print("----------------------------------------")
print("Autofocus disable requested.")
print("Press Q to stop.")
print()


# ----------------------------------------
# Main loop
# ----------------------------------------
while cap.isOpened():

    ret, frame = cap.read()

    if not ret:
        print("Could not access webcam.")
        break

    # Convert BGR → RGB
    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    # Detect pose
    results = pose.process(rgb_frame)


    # ----------------------------------------
    # If body detected
    # ----------------------------------------
    if results.pose_landmarks:

        landmarks = results.pose_landmarks.landmark


        # ----------------------------------------
        # LEFT LEG
        # ----------------------------------------

        left_hip = landmarks[
            mp_pose.PoseLandmark.LEFT_HIP.value
        ]

        left_knee = landmarks[
            mp_pose.PoseLandmark.LEFT_KNEE.value
        ]

        left_ankle = landmarks[
            mp_pose.PoseLandmark.LEFT_ANKLE.value
        ]


        # ----------------------------------------
        # RIGHT LEG
        # ----------------------------------------

        right_hip = landmarks[
            mp_pose.PoseLandmark.RIGHT_HIP.value
        ]

        right_knee = landmarks[
            mp_pose.PoseLandmark.RIGHT_KNEE.value
        ]

        right_ankle = landmarks[
            mp_pose.PoseLandmark.RIGHT_ANKLE.value
        ]


        # ----------------------------------------
        # Frame dimensions
        # ----------------------------------------

        h, w, _ = frame.shape


        # ----------------------------------------
        # Convert coordinates
        # ----------------------------------------

        left_hip_point = (
            int(left_hip.x * w),
            int(left_hip.y * h)
        )

        left_knee_point = (
            int(left_knee.x * w),
            int(left_knee.y * h)
        )

        left_ankle_point = (
            int(left_ankle.x * w),
            int(left_ankle.y * h)
        )


        right_hip_point = (
            int(right_hip.x * w),
            int(right_hip.y * h)
        )

        right_knee_point = (
            int(right_knee.x * w),
            int(right_knee.y * h)
        )

        right_ankle_point = (
            int(right_ankle.x * w),
            int(right_ankle.y * h)
        )


        # ----------------------------------------
        # Calculate knee angles
        # ----------------------------------------

        left_angle = calculate_angle(
            left_hip_point,
            left_knee_point,
            left_ankle_point
        )

        right_angle = calculate_angle(
            right_hip_point,
            right_knee_point,
            right_ankle_point
        )


        # ----------------------------------------
        # Time
        # ----------------------------------------

        elapsed_time = time.time() - start_time


        # ----------------------------------------
        # Save data
        # ----------------------------------------

        writer.writerow([
            round(elapsed_time, 3),
            round(left_angle, 2),
            round(right_angle, 2)
        ])


        # ----------------------------------------
        # Display angles
        # ----------------------------------------

        cv2.putText(
            frame,
            f"Left Knee: {left_angle:.1f} deg",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"Right Knee: {right_angle:.1f} deg",
            (20, 75),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )


        # ----------------------------------------
        # Draw body skeleton
        # ----------------------------------------

        mp_drawing.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS
        )


    # ----------------------------------------
    # Display webcam
    # ----------------------------------------

    cv2.imshow(
        "RehabQuest - Knee Angle Tracking",
        frame
    )


    # ----------------------------------------
    # Press Q to stop
    # ----------------------------------------

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# ----------------------------------------
# Cleanup
# ----------------------------------------

cap.release()
pose.close()
file.close()

cv2.destroyAllWindows()


print()
print("----------------------------------------")
print("Knee angle recording completed.")
print("Data saved to knee_angles.csv")
print("----------------------------------------")
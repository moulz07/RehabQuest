import cv2
import mediapipe as mp
import math
import csv
import time


# -----------------------------
# MediaPipe Pose Setup
# -----------------------------

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

pose = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    smooth_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)


# -----------------------------
# Function to Calculate Angle
# -----------------------------

def calculate_angle(a, b, c):

    angle = math.degrees(
        math.atan2(c[1] - b[1], c[0] - b[0])
        -
        math.atan2(a[1] - b[1], a[0] - b[0])
    )

    angle = abs(angle)

    if angle > 180:
        angle = 360 - angle

    return angle


# -----------------------------
# Open Webcam
# -----------------------------

cap = cv2.VideoCapture(0)

print("RehabQuest Joint Angle Tracking")
print("Move both arms.")
print("Press Q to stop.")


# -----------------------------
# Prepare CSV File
# -----------------------------

csv_file = open(
    "joint_angles.csv",
    "w",
    newline=""
)

writer = csv.writer(csv_file)

writer.writerow([
    "Time",
    "Left_Elbow_Angle",
    "Right_Elbow_Angle"
])


# Start timer
start_time = time.time()


# -----------------------------
# Main Loop
# -----------------------------

while cap.isOpened():

    success, frame = cap.read()

    if not success:
        print("Could not access webcam.")
        break

    frame = cv2.flip(frame, 1)

    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    results = pose.process(rgb_frame)


    # -----------------------------
    # Detect Body
    # -----------------------------

    if results.pose_landmarks:

        landmarks = results.pose_landmarks.landmark


        # -----------------------------
        # LEFT ARM
        # -----------------------------

        left_shoulder = landmarks[
            mp_pose.PoseLandmark.LEFT_SHOULDER
        ]

        left_elbow = landmarks[
            mp_pose.PoseLandmark.LEFT_ELBOW
        ]

        left_wrist = landmarks[
            mp_pose.PoseLandmark.LEFT_WRIST
        ]


        left_shoulder_point = (
            left_shoulder.x,
            left_shoulder.y
        )

        left_elbow_point = (
            left_elbow.x,
            left_elbow.y
        )

        left_wrist_point = (
            left_wrist.x,
            left_wrist.y
        )


        left_angle = calculate_angle(
            left_shoulder_point,
            left_elbow_point,
            left_wrist_point
        )


        # -----------------------------
        # RIGHT ARM
        # -----------------------------

        right_shoulder = landmarks[
            mp_pose.PoseLandmark.RIGHT_SHOULDER
        ]

        right_elbow = landmarks[
            mp_pose.PoseLandmark.RIGHT_ELBOW
        ]

        right_wrist = landmarks[
            mp_pose.PoseLandmark.RIGHT_WRIST
        ]


        right_shoulder_point = (
            right_shoulder.x,
            right_shoulder.y
        )

        right_elbow_point = (
            right_elbow.x,
            right_elbow.y
        )

        right_wrist_point = (
            right_wrist.x,
            right_wrist.y
        )


        right_angle = calculate_angle(
            right_shoulder_point,
            right_elbow_point,
            right_wrist_point
        )


        # -----------------------------
        # Time
        # -----------------------------

        current_time = time.time() - start_time


        # -----------------------------
        # Save Data
        # -----------------------------

        writer.writerow([
            f"{current_time:.3f}",
            f"{left_angle:.2f}",
            f"{right_angle:.2f}"
        ])


        # -----------------------------
        # Terminal Output
        # -----------------------------

        print(
            f"Time: {current_time:.3f}s | "
            f"Left Elbow: {left_angle:.2f}° | "
            f"Right Elbow: {right_angle:.2f}°"
        )


        # -----------------------------
        # Draw Skeleton
        # -----------------------------

        mp_drawing.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS
        )


        # -----------------------------
        # Display Angles
        # -----------------------------

        cv2.putText(
            frame,
            f"Left Elbow: {left_angle:.1f} deg",
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"Right Elbow: {right_angle:.1f} deg",
            (30, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )


    # -----------------------------
    # Show Webcam
    # -----------------------------

    cv2.imshow(
        "RehabQuest - Joint Angles",
        frame
    )


    # -----------------------------
    # Quit
    # -----------------------------

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# -----------------------------
# Close Everything
# -----------------------------

cap.release()
pose.close()
csv_file.close()

cv2.destroyAllWindows()

print()
print("Joint angle data saved to:")
print("joint_angles.csv")
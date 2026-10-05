import cv2
import mediapipe as mp
import math
import csv
import time


# Calculate angle between three points
def calculate_angle(a, b, c):
    angle = math.degrees(
        math.atan2(c[1] - b[1], c[0] - b[0])
        - math.atan2(a[1] - b[1], a[0] - b[0])
    )

    angle = abs(angle)

    if angle > 180:
        angle = 360 - angle

    return angle


# MediaPipe Pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

pose = mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Open webcam
cap = cv2.VideoCapture(0)

# Create CSV file
file = open("shoulder_angles.csv", "w", newline="")
writer = csv.writer(file)

writer.writerow([
    "Time",
    "Left_Shoulder_Angle",
    "Right_Shoulder_Angle"
])

start_time = time.time()

print("----------------------------------------")
print("REHABQUEST SHOULDER ANGLE TRACKING")
print("----------------------------------------")
print("Press Q to stop.")
print()

while cap.isOpened():

    ret, frame = cap.read()

    if not ret:
        print("Could not access webcam.")
        break

    # Convert BGR to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect pose
    results = pose.process(rgb_frame)

    if results.pose_landmarks:

        landmarks = results.pose_landmarks.landmark

        # Left landmarks
        left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        left_elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]

        # Right landmarks
        right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
        right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        right_elbow = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value]

        # Convert to image coordinates
        h, w, _ = frame.shape

        left_hip_point = (
            int(left_hip.x * w),
            int(left_hip.y * h)
        )

        left_shoulder_point = (
            int(left_shoulder.x * w),
            int(left_shoulder.y * h)
        )

        left_elbow_point = (
            int(left_elbow.x * w),
            int(left_elbow.y * h)
        )

        right_hip_point = (
            int(right_hip.x * w),
            int(right_hip.y * h)
        )

        right_shoulder_point = (
            int(right_shoulder.x * w),
            int(right_shoulder.y * h)
        )

        right_elbow_point = (
            int(right_elbow.x * w),
            int(right_elbow.y * h)
        )

        # Calculate shoulder angles
        left_angle = calculate_angle(
            left_hip_point,
            left_shoulder_point,
            left_elbow_point
        )

        right_angle = calculate_angle(
            right_hip_point,
            right_shoulder_point,
            right_elbow_point
        )

        # Current time
        elapsed_time = time.time() - start_time

        # Save to CSV
        writer.writerow([
            round(elapsed_time, 3),
            round(left_angle, 2),
            round(right_angle, 2)
        ])

        # Display angles
        cv2.putText(
            frame,
            f"Left Shoulder: {left_angle:.1f} deg",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"Right Shoulder: {right_angle:.1f} deg",
            (20, 75),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        # Draw pose skeleton
        mp_drawing.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS
        )

    # Show webcam
    cv2.imshow(
        "RehabQuest - Shoulder Angle Tracking",
        frame
    )

    # Press Q to quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# Cleanup
cap.release()
file.close()
cv2.destroyAllWindows()

print()
print("----------------------------------------")
print("Shoulder angle recording completed.")
print("Data saved to shoulder_angles.csv")
print("----------------------------------------")
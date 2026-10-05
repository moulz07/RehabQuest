import cv2
import mediapipe as mp

# MediaPipe Pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

pose = mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Open webcam
cap = cv2.VideoCapture(0)

print("----------------------------------------")
print("REHABQUEST LOWER BODY TRACKING")
print("----------------------------------------")
print("Tracking:")
print("- Left Hip")
print("- Right Hip")
print("- Left Knee")
print("- Right Knee")
print("- Left Ankle")
print("- Right Ankle")
print()
print("Press Q to stop.")
print()

while cap.isOpened():

    ret, frame = cap.read()

    if not ret:
        print("Could not access webcam.")
        break

    # Convert BGR to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect body pose
    results = pose.process(rgb_frame)

    if results.pose_landmarks:

        landmarks = results.pose_landmarks.landmark

        # Lower-body landmarks
        left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
        right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]

        left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
        right_knee = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value]

        left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
        right_ankle = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]

        # Display landmark coordinates
        print(
            f"Left Hip: ({left_hip.x:.2f}, {left_hip.y:.2f}) | "
            f"Right Hip: ({right_hip.x:.2f}, {right_hip.y:.2f})"
        )

        print(
            f"Left Knee: ({left_knee.x:.2f}, {left_knee.y:.2f}) | "
            f"Right Knee: ({right_knee.x:.2f}, {right_knee.y:.2f})"
        )

        print(
            f"Left Ankle: ({left_ankle.x:.2f}, {left_ankle.y:.2f}) | "
            f"Right Ankle: ({right_ankle.x:.2f}, {right_ankle.y:.2f})"
        )

        print("----------------------------------------")

        # Draw complete pose skeleton
        mp_drawing.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS
        )

    # Display webcam
    cv2.imshow(
        "RehabQuest - Lower Body Tracking",
        frame
    )

    # Press Q to stop
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Cleanup
cap.release()
pose.close()
cv2.destroyAllWindows()

print()
print("----------------------------------------")
print("Lower body tracking stopped.")
print("----------------------------------------")
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
print("REHABQUEST FULL BODY TRACKING")
print("----------------------------------------")
print("Tracking:")
print("- Head")
print("- Shoulders")
print("- Elbows")
print("- Wrists")
print("- Hips")
print("- Knees")
print("- Ankles")
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

    # Detect full-body pose
    results = pose.process(rgb_frame)

    if results.pose_landmarks:

        # Draw the complete body skeleton
        mp_drawing.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS
        )

        # Get landmarks
        landmarks = results.pose_landmarks.landmark

        # Important full-body landmarks
        nose = landmarks[mp_pose.PoseLandmark.NOSE.value]

        left_shoulder = landmarks[
            mp_pose.PoseLandmark.LEFT_SHOULDER.value
        ]

        right_shoulder = landmarks[
            mp_pose.PoseLandmark.RIGHT_SHOULDER.value
        ]

        left_elbow = landmarks[
            mp_pose.PoseLandmark.LEFT_ELBOW.value
        ]

        right_elbow = landmarks[
            mp_pose.PoseLandmark.RIGHT_ELBOW.value
        ]

        left_wrist = landmarks[
            mp_pose.PoseLandmark.LEFT_WRIST.value
        ]

        right_wrist = landmarks[
            mp_pose.PoseLandmark.RIGHT_WRIST.value
        ]

        left_hip = landmarks[
            mp_pose.PoseLandmark.LEFT_HIP.value
        ]

        right_hip = landmarks[
            mp_pose.PoseLandmark.RIGHT_HIP.value
        ]

        left_knee = landmarks[
            mp_pose.PoseLandmark.LEFT_KNEE.value
        ]

        right_knee = landmarks[
            mp_pose.PoseLandmark.RIGHT_KNEE.value
        ]

        left_ankle = landmarks[
            mp_pose.PoseLandmark.LEFT_ANKLE.value
        ]

        right_ankle = landmarks[
            mp_pose.PoseLandmark.RIGHT_ANKLE.value
        ]

        # Display a simple status
        cv2.putText(
            frame,
            "FULL BODY TRACKING ACTIVE",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

    # Show webcam
    cv2.imshow(
        "RehabQuest - Full Body Tracking",
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
print("Full body tracking stopped.")
print("----------------------------------------")
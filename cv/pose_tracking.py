import cv2
import mediapipe as mp


# MediaPipe Pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

pose = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    smooth_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Open webcam
cap = cv2.VideoCapture(0)

print("RehabQuest Body Pose Tracking")
print("Press Q to quit.")


while cap.isOpened():

    success, frame = cap.read()

    if not success:
        print("Could not access webcam.")
        break

    # Flip image so it behaves like a mirror
    frame = cv2.flip(frame, 1)

    # Convert BGR → RGB
    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    # Detect body landmarks
    results = pose.process(rgb_frame)

    # Draw body skeleton
    if results.pose_landmarks:

        mp_drawing.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS
        )

        # Important landmarks
        landmarks = results.pose_landmarks.landmark

        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]

        left_elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW]
        right_elbow = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW]

        left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
        right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]

        # Print coordinates
        print(
            f"Left Shoulder: "
            f"({left_shoulder.x:.3f}, {left_shoulder.y:.3f}) | "
            f"Left Elbow: "
            f"({left_elbow.x:.3f}, {left_elbow.y:.3f}) | "
            f"Left Wrist: "
            f"({left_wrist.x:.3f}, {left_wrist.y:.3f})"
        )

        print(
            f"Right Shoulder: "
            f"({right_shoulder.x:.3f}, {right_shoulder.y:.3f}) | "
            f"Right Elbow: "
            f"({right_elbow.x:.3f}, {right_elbow.y:.3f}) | "
            f"Right Wrist: "
            f"({right_wrist.x:.3f}, {right_wrist.y:.3f})"
        )

    # Show webcam
    cv2.imshow(
        "RehabQuest - Body Pose Tracking",
        frame
    )

    # Press Q to quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


cap.release()
pose.close()
cv2.destroyAllWindows()
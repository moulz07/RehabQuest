import cv2
import mediapipe as mp

# MediaPipe modules
mp_pose = mp.solutions.pose
mp_hands = mp.solutions.hands

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Pose model
pose = mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Hand model
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Open webcam
cap = cv2.VideoCapture(0)

print("----------------------------------------")
print("REHABQUEST FULL BODY + HAND TRACKING")
print("----------------------------------------")
print("Tracking:")
print("- Full body")
print("- Left hand")
print("- Right hand")
print("- 21 landmarks per detected hand")
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

    # Detect body
    pose_results = pose.process(rgb_frame)

    # Detect hands
    hand_results = hands.process(rgb_frame)

    # ----------------------------------------
    # DRAW FULL BODY
    # ----------------------------------------

    if pose_results.pose_landmarks:

        mp_drawing.draw_landmarks(
            frame,
            pose_results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS
        )

    # ----------------------------------------
    # DRAW HANDS
    # ----------------------------------------

    if hand_results.multi_hand_landmarks:

        for hand_landmarks in hand_results.multi_hand_landmarks:

            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style()
            )

    # ----------------------------------------
    # STATUS
    # ----------------------------------------

    cv2.putText(
        frame,
        "FULL BODY + HAND TRACKING",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        (0, 255, 0),
        2
    )

    # Show number of detected hands
    hand_count = 0

    if hand_results.multi_hand_landmarks:
        hand_count = len(hand_results.multi_hand_landmarks)

    cv2.putText(
        frame,
        f"Hands detected: {hand_count}",
        (20, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (0, 255, 0),
        2
    )

    # Show webcam
    cv2.imshow(
        "RehabQuest - Full Body + Hand Tracking",
        frame
    )

    # Press Q to stop
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Cleanup
cap.release()
pose.close()
hands.close()
cv2.destroyAllWindows()

print()
print("----------------------------------------")
print("Full body + hand tracking stopped.")
print("----------------------------------------")
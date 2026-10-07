import cv2
import mediapipe as mp
import math
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils
shoulder_movements = []
hip_movements = []
wrist_movements = []

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()

    if not ret:
        break

    frame = cv2.flip(frame, 1)

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = pose.process(rgb_frame)

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark

        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]

        left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
        right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP]
        left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
        right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
        shoulder_y = (left_shoulder.y + right_shoulder.y) / 2
        hip_y = (left_hip.y + right_hip.y) / 2
        wrist_y = (left_wrist.y + right_wrist.y) / 2
        shoulder_movements.append(shoulder_y)
        hip_movements.append(hip_y)
        wrist_movements.append(wrist_y)
        print(
            "Shoulder Y:",
            round(left_shoulder.y, 3),
            round(right_shoulder.y, 3),
            " | Hip Y:",
            round(left_hip.y, 3),
            round(right_hip.y, 3)
        )

    mp_drawing.draw_landmarks(
        frame,
        results.pose_landmarks,
        mp_pose.POSE_CONNECTIONS
    )

    cv2.imshow("Compensatory Movement Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
cap.release()
cv2.destroyAllWindows()

if shoulder_movements and hip_movements and wrist_movements:
    shoulder_movement = max(shoulder_movements) - min(shoulder_movements)
    hip_movement = max(hip_movements) - min(hip_movements)
    wrist_movement = max(wrist_movements) - min(wrist_movements)

    print("\nMovement Analysis")
    print("-----------------")
    print("Shoulder Movement:", round(shoulder_movement, 4))
    print("Hip Movement:", round(hip_movement, 4))
    print("Wrist Movement:", round(wrist_movement, 4))
    compensation_ratio = hip_movement / wrist_movement

    print("Compensation Ratio:", round(compensation_ratio, 4))
    if compensation_ratio > 1.0:
     print("Possible Compensatory Movement Detected")
    else:
     print("No Significant Compensatory Movement Detected")
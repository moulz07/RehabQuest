import cv2
import mediapipe as mp
import csv
import time

# Start MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Start webcam
cap = cv2.VideoCapture(0)

# Create CSV file
file = open("hand_movement.csv", "w", newline="")
writer = csv.writer(file)

# CSV column names
writer.writerow(["Time", "Wrist_X", "Wrist_Y"])

# Start timer
start_time = time.time()

while True:

    ret, frame = cap.read()

    if not ret:
        print("Could not access webcam.")
        break

    # Flip image like a mirror
    frame = cv2.flip(frame, 1)

    # Convert BGR to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect hand
    results = hands.process(rgb_frame)

    # If hand is detected
    if results.multi_hand_landmarks:

        for hand_landmarks in results.multi_hand_landmarks:

            # Draw hand landmarks
            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

            # Get wrist
            wrist = hand_landmarks.landmark[
                mp_hands.HandLandmark.WRIST
            ]

            # Get coordinates
            x = wrist.x
            y = wrist.y

            # Get elapsed time
            current_time = time.time() - start_time

            # Save data
            writer.writerow([
                round(current_time, 3),
                round(x, 4),
                round(y, 4)
            ])

    # Show webcam
    cv2.imshow("RehabQuest - Hand Tracking", frame)

    # Press Q to quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release everything
cap.release()
hands.close()
cv2.destroyAllWindows()

# Close CSV file
file.close()
import cv2
import mediapipe as mp
import socket
import json

# --------------------------------------------------
# MediaPipe Hand Setup
# --------------------------------------------------

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# --------------------------------------------------
# Webcam Setup
# --------------------------------------------------

cap = cv2.VideoCapture(0)

# --------------------------------------------------
# Unity Server Setup
# --------------------------------------------------

HOST = "127.0.0.1"
PORT = 5005

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)

print("----------------------------------------")
print("REHABQUEST MEDIAPIPE → UNITY")
print("----------------------------------------")
print("Waiting for Unity to connect...")

connection, address = server.accept()

print("Unity connected:", address)
print("Starting hand tracking...")
print("Press Q to stop.")
print()

# --------------------------------------------------
# Main Tracking Loop
# --------------------------------------------------

while cap.isOpened():

    ret, frame = cap.read()

    if not ret:
        print("Could not access webcam.")
        break

    # Flip webcam for natural movement
    frame = cv2.flip(frame, 1)

    # Convert BGR → RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect hands
    results = hands.process(rgb_frame)

    # --------------------------------------------------
    # Get Wrist Coordinates
    # --------------------------------------------------

    if results.multi_hand_landmarks:

        # Use the first detected hand
        hand = results.multi_hand_landmarks[0]

        # Get wrist landmark
        wrist = hand.landmark[mp_hands.HandLandmark.WRIST]

        # MediaPipe coordinates are normalized 0–1
        x = wrist.x
        y = wrist.y

        # Display coordinates in terminal
        print(f"Wrist: X={x:.3f}, Y={y:.3f}")

        # --------------------------------------------------
        # Send Coordinates to Unity
        # --------------------------------------------------

        data = {
            "x": x,
            "y": y
        }

        message = json.dumps(data) + "\n"

        try:
            connection.sendall(message.encode("utf-8"))

        except (BrokenPipeError, ConnectionResetError):
            print("Unity disconnected.")
            break

        # --------------------------------------------------
        # Draw Hand
        # --------------------------------------------------

        mp_drawing.draw_landmarks(
            frame,
            hand,
            mp_hands.HAND_CONNECTIONS
        )

        # Display coordinates on webcam
        cv2.putText(
            frame,
            f"Wrist X: {x:.3f}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"Wrist Y: {y:.3f}",
            (20, 75),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

    else:

        cv2.putText(
            frame,
            "No hand detected",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2
        )

    # --------------------------------------------------
    # Show Webcam
    # --------------------------------------------------

    cv2.imshow(
        "RehabQuest - MediaPipe to Unity",
        frame
    )

    # Press Q to stop
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# --------------------------------------------------
# Cleanup
# --------------------------------------------------

cap.release()
hands.close()

connection.close()
server.close()

cv2.destroyAllWindows()

print()
print("----------------------------------------")
print("MediaPipe → Unity connection stopped.")
print("----------------------------------------")
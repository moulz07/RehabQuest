
import cv2
import mediapipe as mp
import socket
import json

# --------------------------------------------------
# Configuration
# --------------------------------------------------

HOST = "127.0.0.1"
PORT = 5005

# False = run tracking without a visible webcam window.
SHOW_CAMERA = False

# --------------------------------------------------
# MediaPipe Setup
# --------------------------------------------------

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)

# --------------------------------------------------
# Webcam Setup
# --------------------------------------------------

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    hands.close()
    raise RuntimeError(
        "Could not open webcam. Close other apps using the camera."
    )

if SHOW_CAMERA:
    cv2.namedWindow(
        "RehabQuest - MediaPipe to Unity",
        cv2.WINDOW_NORMAL,
    )

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

connection = None

try:
    # --------------------------------------------------
    # Wait for Unity
    # --------------------------------------------------

    server.bind((HOST, PORT))
    server.listen(1)

    print("----------------------------------------")
    print("REHABQUEST MEDIAPIPE -> UNITY")
    print("----------------------------------------")
    print("Waiting for Unity to connect...")

    connection, address = server.accept()
    connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    print("Unity connected:", address)
    print("Hand tracking started.")
    print("Camera display:", "ON" if SHOW_CAMERA else "OFF")
    print("Press Ctrl+C in this terminal to stop.")
    print()

    # --------------------------------------------------
    # Main Tracking Loop
    # --------------------------------------------------

    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            print("Could not read webcam frame.")
            break

        # Mirror the camera for natural movement.
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]
            wrist = hand.landmark[mp_hands.HandLandmark.WRIST]

            x = float(wrist.x)
            y = float(wrist.y)

            # Send one complete JSON object per line.
            message = json.dumps({"x": x, "y": y}) + "\n"
            connection.sendall(message.encode("utf-8"))

            print(f"\rWrist: X={x:.3f}, Y={y:.3f}", end="", flush=True)

            if SHOW_CAMERA:
                mp_drawing.draw_landmarks(
                    frame,
                    hand,
                    mp_hands.HAND_CONNECTIONS,
                )

                cv2.putText(
                    frame,
                    f"Wrist X: {x:.3f}  Y: {y:.3f}",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2,
                )
        elif SHOW_CAMERA:
            cv2.putText(
                frame,
                "No hand detected",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2,
            )

        # No window is created or updated when SHOW_CAMERA is False.
        if SHOW_CAMERA:
            cv2.imshow("RehabQuest - MediaPipe to Unity", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

except KeyboardInterrupt:
    print("\nStopping MediaPipe tracking...")

except (BrokenPipeError, ConnectionResetError, OSError) as exc:
    print(f"\nSocket connection ended: {exc}")

finally:
    if connection is not None:
        try:
            connection.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        connection.close()

    server.close()
    cap.release()
    hands.close()

    if SHOW_CAMERA:
        cv2.destroyAllWindows()

    print("\nMediaPipe tracking stopped and resources released.")

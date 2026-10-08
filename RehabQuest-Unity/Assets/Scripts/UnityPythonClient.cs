using UnityEngine;
using System;
using System.Globalization;
using System.IO;
using System.Net.Sockets;
using System.Text;
using System.Threading;

public class UnityPythonClient : MonoBehaviour
{
    [Serializable]
    private class WristMessage
    {
        public float x;
        public float y;
    }

    [Header("Scene References")]
    [SerializeField] private Transform playerHand;

    [Header("Unity Movement Bounds")]
    [Tooltip("World-space X range for PlayerHand movement across the GameFloor.")]
    [SerializeField] private Vector2 xBounds = new Vector2(-2.25f, 2.25f);

    [Tooltip("World-space Z range for PlayerHand movement across the GameFloor.")]
    [SerializeField] private Vector2 zBounds = new Vector2(-2.25f, 2.25f);

    [Tooltip("Fixed world-space Y height for PlayerHand above the GameFloor.")]
    [SerializeField] private float handHeight = 1f;

    [Header("Webcam Input Calibration")]
    [Tooltip("Usable MediaPipe X input range. Narrow this if your hand stays in the middle of the webcam image.")]
    [SerializeField] private Vector2 inputXBounds = new Vector2(0f, 1f);

    [Tooltip("Usable MediaPipe Y input range. MediaPipe Y still increases downward; this is inverted during world mapping.")]
    [SerializeField] private Vector2 inputYBounds = new Vector2(0f, 1f);

    [Header("Smoothing")]
    [Tooltip("How quickly PlayerHand catches up to the latest wrist position. Higher is snappier; lower is smoother.")]
    [SerializeField] private float smoothingStrength = 12f;

    [Header("Connection")]
    [SerializeField] private float reconnectDelaySeconds = 2f;

    public float LatestWristX { get; private set; }
    public float LatestWristY { get; private set; }
    public bool HasTrackingData { get; private set; }

    private const string Host = "127.0.0.1";
    private const int Port = 5005;

    private TcpClient client;
    private NetworkStream stream;
    private Thread receiveThread;
    private Rigidbody playerHandRigidbody;
    private readonly object dataLock = new object();
    private volatile bool isRunning;
    private bool loggedTrackingStarted;
    private bool hasSmoothedPosition;
    private Vector2 latestWrist;
    private Vector3 smoothedPosition;

    void Start()
    {
        if (playerHand == null)
        {
            GameObject playerHandObject = GameObject.Find("PlayerHand");

            if (playerHandObject != null)
            {
                playerHand = playerHandObject.transform;
            }
        }

        if (playerHand != null)
        {
            playerHandRigidbody = playerHand.GetComponent<Rigidbody>();

            if (playerHandRigidbody != null)
            {
                playerHandRigidbody.isKinematic = true;
                playerHandRigidbody.useGravity = false;
            }
        }
        else
        {
            Debug.LogWarning("PlayerHand object was not found. Wrist data will be received but no object will move.");
        }

        Debug.Log(
            "MediaPipe movement settings: " +
            $"inputX={inputXBounds}, inputY={inputYBounds}, " +
            $"worldX={xBounds}, worldZ={zBounds}, " +
            $"height={handHeight}, smoothing={smoothingStrength}"
        );

        isRunning = true;
        receiveThread = new Thread(ReceiveLoop)
        {
            IsBackground = true
        };
        receiveThread.Start();
    }

    void FixedUpdate()
    {
        Vector2 wrist;
        bool hasData;

        lock (dataLock)
        {
            wrist = latestWrist;
            hasData = HasTrackingData;
        }

        if (!hasData || playerHand == null)
        {
            return;
        }

        Vector3 targetPosition = MapWristToWorld(wrist);
        Vector3 movementPosition = SmoothPosition(targetPosition);

        if (playerHandRigidbody != null)
        {
            playerHandRigidbody.MovePosition(movementPosition);
        }
        else
        {
            playerHand.position = movementPosition;
        }
    }

    private void ReceiveLoop()
    {
        while (isRunning)
        {
            try
            {
                using (client = new TcpClient())
                {
                    client.Connect(Host, Port);

                    using (stream = client.GetStream())
                    using (StreamReader reader = new StreamReader(stream, Encoding.UTF8))
                    {
                        Debug.Log($"Connected to Python server at {Host}:{Port}.");

                        string line;

                        while (isRunning && (line = reader.ReadLine()) != null)
                        {
                            HandleMessage(line);
                        }
                    }
                }

                if (isRunning)
                {
                    Debug.LogWarning("Python connection lost.");
                }
            }
            catch (SocketException e)
            {
                if (isRunning)
                {
                    Debug.LogWarning($"Python connection failed: {e.Message}");
                }
            }
            catch (IOException e)
            {
                if (isRunning)
                {
                    Debug.LogWarning($"Python connection lost: {e.Message}");
                }
            }
            catch (ObjectDisposedException)
            {
                if (isRunning)
                {
                    Debug.LogWarning("Python connection closed unexpectedly.");
                }
            }
            catch (Exception e)
            {
                if (isRunning)
                {
                    Debug.LogWarning($"Python receive error: {e.Message}");
                }
            }

            CloseConnection();

            if (isRunning)
            {
                Thread.Sleep(Mathf.Max(1, Mathf.RoundToInt(reconnectDelaySeconds * 1000f)));
            }
        }
    }

    private void HandleMessage(string message)
    {
        if (string.IsNullOrWhiteSpace(message))
        {
            return;
        }

        try
        {
            WristMessage wristMessage = JsonUtility.FromJson<WristMessage>(message);

            if (!MessageContainsCoordinateFields(message) ||
                wristMessage == null ||
                float.IsNaN(wristMessage.x) ||
                float.IsNaN(wristMessage.y) ||
                wristMessage.x < 0f ||
                wristMessage.x > 1f ||
                wristMessage.y < 0f ||
                wristMessage.y > 1f)
            {
                Debug.LogWarning("Malformed wrist JSON received: " + message);
                return;
            }

            lock (dataLock)
            {
                latestWrist = new Vector2(wristMessage.x, wristMessage.y);
                LatestWristX = wristMessage.x;
                LatestWristY = wristMessage.y;
                HasTrackingData = true;
            }

            if (!loggedTrackingStarted)
            {
                loggedTrackingStarted = true;
                Debug.Log(
                    "Tracking started. Received wrist data: x=" +
                    wristMessage.x.ToString("F3", CultureInfo.InvariantCulture) +
                    ", y=" +
                    wristMessage.y.ToString("F3", CultureInfo.InvariantCulture)
                );
            }
        }
        catch (Exception e)
        {
            Debug.LogWarning($"Malformed wrist JSON received: {message}. Error: {e.Message}");
        }
    }

    private Vector3 MapWristToWorld(Vector2 wrist)
    {
        // Calibration expands the configured webcam range back to 0..1.
        // Values outside that range are clamped so the hand stays on the floor.
        float calibratedX = CalibrateInput(wrist.x, inputXBounds);
        float calibratedY = CalibrateInput(wrist.y, inputYBounds);

        float worldX = Mathf.Lerp(xBounds.x, xBounds.y, calibratedX);
        float invertedY = 1f - calibratedY;
        float worldZ = Mathf.Lerp(zBounds.x, zBounds.y, invertedY);

        return new Vector3(worldX, handHeight, worldZ);
    }

    private float CalibrateInput(float value, Vector2 inputBounds)
    {
        float min = Mathf.Min(inputBounds.x, inputBounds.y);
        float max = Mathf.Max(inputBounds.x, inputBounds.y);

        if (Mathf.Approximately(min, max))
        {
            return 0.5f;
        }

        float normalized = Mathf.InverseLerp(min, max, value);
        return Mathf.Clamp01(normalized);
    }

    private Vector3 SmoothPosition(Vector3 targetPosition)
    {
        if (!hasSmoothedPosition || smoothingStrength <= 0f)
        {
            smoothedPosition = targetPosition;
            hasSmoothedPosition = true;
            return smoothedPosition;
        }

        // Exponential smoothing: stable across frame rates and easy to tune.
        float smoothingFactor = 1f - Mathf.Exp(-smoothingStrength * Time.fixedDeltaTime);
        smoothedPosition = Vector3.Lerp(smoothedPosition, targetPosition, smoothingFactor);

        return smoothedPosition;
    }

    private bool MessageContainsCoordinateFields(string message)
    {
        return message.Contains("\"x\"") && message.Contains("\"y\"");
    }

    void OnValidate()
    {
        handHeight = Mathf.Max(0f, handHeight);
        smoothingStrength = Mathf.Max(0f, smoothingStrength);
        reconnectDelaySeconds = Mathf.Max(0.25f, reconnectDelaySeconds);
    }

    void OnApplicationQuit()
    {
        StopReceiver();
    }

    void OnDestroy()
    {
        StopReceiver();
    }

    private void StopReceiver()
    {
        isRunning = false;
        CloseConnection();

        if (receiveThread != null && receiveThread.IsAlive)
        {
            receiveThread.Join(500);
        }
    }

    private void CloseConnection()
    {
        if (stream != null)
        {
            stream.Close();
            stream = null;
        }

        if (client != null)
        {
            client.Close();
            client = null;
        }
    }
}

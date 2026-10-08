using UnityEngine;
using System.Net.Sockets;
using System.Text;

public class UnityPythonClient : MonoBehaviour
{
    private TcpClient client;
    private NetworkStream stream;

    void Start()
    {
        try
        {
            client = new TcpClient("127.0.0.1", 5005);
            stream = client.GetStream();

            Debug.Log("Connected to Python server!");

            string message = ReadMessage();

            Debug.Log("Received from Python: " + message);
        }
        catch (System.Exception e)
        {
            Debug.LogError("Python connection failed: " + e.Message);
        }
    }

    string ReadMessage()
    {
        byte[] buffer = new byte[1024];

        int bytesRead = stream.Read(buffer, 0, buffer.Length);

        return Encoding.UTF8.GetString(buffer, 0, bytesRead);
    }

    void OnApplicationQuit()
    {
        if (stream != null)
            stream.Close();

        if (client != null)
            client.Close();
    }
}
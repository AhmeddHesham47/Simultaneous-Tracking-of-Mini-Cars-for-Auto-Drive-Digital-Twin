using System.Collections.Concurrent;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading; 
using UnityEngine;
using System;

public class UDPReceive : MonoBehaviour
{
    private Thread receiveThread;
    private UdpClient client;
    private ConcurrentQueue<string> dataQueue = new ConcurrentQueue<string>();
    private volatile bool isRunning = true;

    public int port = 5053;
    public int maxQueueSize = 100;
    public bool printToConsole = false;

    void Start() => StartReceiving();

    void OnDisable() => StopReceiving();

    private void StartReceiving()
    {
        receiveThread = new Thread(ReceiveData) { IsBackground = true };
        receiveThread.Start();
    }

    private void StopReceiving()
    {
        isRunning = false;
        client?.Close();
        receiveThread?.Join();
    }

    private void ReceiveData()
    {
        client = new UdpClient(port) { Client = { ReceiveBufferSize = 65527 } };

        while (isRunning)
        {
            try
            {
                IPEndPoint anyIP = new IPEndPoint(IPAddress.Any, 0);
                string data = Encoding.UTF8.GetString(client.Receive(ref anyIP));

                foreach (var message in data.Split(new[] { "\r\n", "\r", "\n" }, System.StringSplitOptions.RemoveEmptyEntries))
                {
                    if (dataQueue.Count >= maxQueueSize) dataQueue.TryDequeue(out _);
                    dataQueue.Enqueue(message);
                }

                if (printToConsole) Debug.Log($"Received {dataQueue.Count} messages");
            }
            catch (SocketException e)
            {
                if (!isRunning) break;
                Debug.LogError($"Socket Error: {e}");
            }
            catch (Exception e)
            {
                Debug.LogError($"Error: {e}");
            }
        }
    }

    public string[] GetLatestData() => dataQueue.ToArray();

    void OnApplicationQuit() => StopReceiving();
}

using UnityEngine;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Collections.Concurrent;
using System.Collections.Generic;
using Newtonsoft.Json.Linq;

public class RouterController : MonoBehaviour
{
    private Thread socketThread;
    private bool isRunning = true;

    private ConcurrentQueue<JObject> incomingMessages = new ConcurrentQueue<JObject>();
    private ConcurrentQueue<JObject> outgoingMessages = new ConcurrentQueue<JObject>();

    private Dictionary<string, AgentController> agents = new Dictionary<string, AgentController>();

    void Start()
    {
        socketThread = new Thread(new ThreadStart(SocketListener));
        socketThread.IsBackground = true;
        socketThread.Start();

        StartCoroutine(ProcessMessages());
    }

    void Update()
    {
        while (outgoingMessages.TryDequeue(out JObject message))
        {
            SendMessageToPython(message);
        }
    }

    private void SocketListener()
    {
        IPAddress ip = IPAddress.Parse("127.0.0.1");
        IPEndPoint endPoint = new IPEndPoint(ip, 8003);
        Socket listener = new Socket(ip.AddressFamily, SocketType.Stream, ProtocolType.Tcp);

        try
        {
            listener.Bind(endPoint);
            listener.Listen(10);

            while (isRunning)
            {
                if (listener.Poll(1000000, SelectMode.SelectRead))
                {
                    Socket handler = listener.Accept();
                    byte[] bytes = new byte[1024];
                    int bytesRec = handler.Receive(bytes);
                    string data = Encoding.ASCII.GetString(bytes, 0, bytesRec);
                    JObject message = JObject.Parse(data);
                    incomingMessages.Enqueue(message);

                    handler.Shutdown(SocketShutdown.Both);
                    handler.Close();
                }
            }

            listener.Close();
        }
        catch (System.Exception e)
        {
            Debug.LogError("Socket Exception: " + e.ToString());
        }
    }

    private System.Collections.IEnumerator ProcessMessages()
    {
        while (true)
        {
            while (incomingMessages.TryDequeue(out JObject message))
            {
                string agentName = message["agent_name"].ToString();
                if (agents.TryGetValue(agentName, out AgentController agent))
                {
                    agent.ReceiveMessage(message["message"].ToString());
                }
            }
            yield return null;
        }
    }

    public void RegisterAgent(string agentName, AgentController agent)
    {
        agents[agentName] = agent;
    }

    public void SendMessageFromAgent(string agentName, string message)
    {
        Debug.Log($"Sending message from {agentName}: {message}");
        JObject outgoingMessage = new JObject
        {
            ["agent_name"] = agentName,
            ["message"] = message
        };
        outgoingMessages.Enqueue(outgoingMessage);
    }

    private void SendMessageToPython(JObject message)
    {
        IPAddress ip = IPAddress.Parse("127.0.0.1");
        IPEndPoint endPoint = new IPEndPoint(ip, 8004);
        Socket socket = null;
        try
        {
            socket = new Socket(ip.AddressFamily, SocketType.Stream, ProtocolType.Tcp);
            socket.Connect(endPoint);
            byte[] msg = Encoding.ASCII.GetBytes(message.ToString());
            socket.Send(msg);
        }
        catch (SocketException e)
        {
            Debug.LogWarning($"Unable to connect to Python: {e.Message}");
        }
        finally
        {
            if (socket != null && socket.Connected)
            {
                socket.Shutdown(SocketShutdown.Both);
                socket.Close();
            }
        }
    }

    private void OnApplicationQuit()
    {
        isRunning = false;

        if (socketThread != null && socketThread.IsAlive)
        {
            socketThread.Join();
        }
    }
}
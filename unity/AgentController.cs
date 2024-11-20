using UnityEngine;
using UnityEngine.AI;
using System.Collections;
using System.Collections.Generic;
using TMPro;

public class AgentController : MonoBehaviour
{
    private NavMeshAgent agent;
    private Vector3 targetPosition;
    private bool shouldNavigate = false;
    private bool shouldStop = false;
    public TextMeshPro messageText;

    private HashSet<string> nearbyAgents = new HashSet<string>();
    private RouterController router;
    public string agentName;

    // 添加一个变量来跟踪是否正在导航
    private bool isNavigating = false;

    void Start()
    {
        agent = GetComponent<NavMeshAgent>();
        router = FindObjectOfType<RouterController>();
        router.RegisterAgent(agentName, this);

        // 保持对nearby agents的定期检查
        InvokeRepeating("CheckForNearbyAgents", 0f, 0.5f);
    }

    public float arrivalThreshold = 2f;

    void Update()
    {
        if (shouldStop)
        {
            agent.ResetPath();
            shouldStop = false;
            isNavigating = false;
            ShowMessage("I am stopping", 2f);
        }

        if (shouldNavigate)
        {
            agent.SetDestination(targetPosition);
            shouldNavigate = false;
            isNavigating = true;
        }

        // 修改检查是否到达目的地的逻辑
        if (isNavigating && !agent.pathPending)
        {
            if (Vector3.Distance(transform.position, targetPosition) <= arrivalThreshold)
            {
                isNavigating = false;
                OnDestinationReached();
            }
        }
    }

    private void OnDestinationReached()
    {
        string message = $"ARRIVED {targetPosition.x},{targetPosition.y},{targetPosition.z}";
        router.SendMessageFromAgent(agentName, message);
        ShowMessage("I have arrived near the destination", 2f);
    }

    private void CheckForNearbyAgents()
    {
        HashSet<string> currentNearbyAgents = new HashSet<string>();
        Collider[] hitColliders = Physics.OverlapSphere(agent.transform.position, 5.0f);
        foreach (var hitCollider in hitColliders)
        {
            NavMeshAgent otherAgent = hitCollider.GetComponent<NavMeshAgent>();
            if (otherAgent != null && otherAgent != agent)
            {
                NavMeshHit hit;
                if (!NavMesh.Raycast(agent.transform.position, otherAgent.transform.position, out hit, NavMesh.AllAreas))
                {
                    string otherAgentName = otherAgent.GetComponent<AgentController>().agentName;
                    currentNearbyAgents.Add(otherAgentName);
                    if (!nearbyAgents.Contains(otherAgentName))
                    {
                        // 新的nearby agent
                        router.SendMessageFromAgent(agentName, $"NEW_AGENT:{otherAgentName}");
                        Debug.Log($"New nearby agent detected: {otherAgentName}");
                    }
                }
            }
        }
        nearbyAgents = currentNearbyAgents;
    }

    public void ReceiveMessage(string message)
    {
        string[] splitData = message.Split(',');
        if (splitData.Length == 3)
        {
            if (float.TryParse(splitData[0], out float x) && 
                float.TryParse(splitData[1], out float y) && 
                float.TryParse(splitData[2], out float z))
            {
                targetPosition = new Vector3(x, y, z);
                shouldNavigate = true;
            }
        }
        else if (message.Trim() == "STOP")
        {
            shouldStop = true;
        }
    }

    private void ShowMessage(string message, float duration)
    {
        StartCoroutine(DisplayMessage(message, duration));
    }

    private IEnumerator DisplayMessage(string message, float duration)
    {
        messageText.text = message;
        messageText.gameObject.SetActive(true);
        yield return new WaitForSeconds(duration);
        messageText.gameObject.SetActive(false);
    }
}
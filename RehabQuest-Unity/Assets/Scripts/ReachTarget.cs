using UnityEngine;

public class ReachTarget : MonoBehaviour
{
    private ReachAndCollectGameManager gameManager;
    private Renderer targetRenderer;
    private Vector3 baseScale;
    private float lifetimeSeconds;
    private float timeRemaining;
    private float pulseSpeed;
    private float pulseAmount;
    private bool isActiveTarget;
    private bool hasReportedResult;

    public float TimeRemaining => Mathf.Max(0f, timeRemaining);
    public float LifetimeSeconds => lifetimeSeconds;

    private void Awake()
    {
        targetRenderer = GetComponent<Renderer>();
        baseScale = transform.localScale;
        DisableLegacyCollector();
    }

    public void Configure(
        ReachAndCollectGameManager manager,
        float targetLifetimeSeconds,
        float targetPulseSpeed,
        float targetPulseAmount
    )
    {
        gameManager = manager;
        lifetimeSeconds = targetLifetimeSeconds;
        pulseSpeed = targetPulseSpeed;
        pulseAmount = targetPulseAmount;
        DisableLegacyCollector();
    }

    public void Activate(Vector3 position, float diameter, Color color)
    {
        transform.position = position;
        baseScale = Vector3.one * diameter;
        transform.localScale = baseScale;

        if (targetRenderer != null)
        {
            targetRenderer.material.color = color;
        }

        timeRemaining = lifetimeSeconds;
        hasReportedResult = false;
        isActiveTarget = true;
        gameObject.SetActive(true);
    }

    private void Update()
    {
        if (!isActiveTarget || hasReportedResult)
        {
            return;
        }

        timeRemaining -= Time.deltaTime;

        float pulse = 1f + Mathf.Sin(Time.time * pulseSpeed) * pulseAmount;
        transform.localScale = baseScale * pulse;

        if (timeRemaining <= 0f)
        {
            ReportMiss();
        }
    }

    private void OnTriggerEnter(Collider other)
    {
        if (!isActiveTarget || hasReportedResult)
        {
            return;
        }

        if (other.gameObject.name == "PlayerHand")
        {
            ReportCollected();
        }
    }

    private void ReportCollected()
    {
        hasReportedResult = true;
        isActiveTarget = false;
        gameManager?.HandleTargetCollected(this, transform.position);
        gameObject.SetActive(false);
    }

    private void ReportMiss()
    {
        hasReportedResult = true;
        isActiveTarget = false;
        gameManager?.HandleTargetMissed(this);
        gameObject.SetActive(false);
    }

    private void DisableLegacyCollector()
    {
        TargetCollect legacyCollector = GetComponent<TargetCollect>();

        if (legacyCollector != null)
        {
            legacyCollector.enabled = false;
        }
    }
}

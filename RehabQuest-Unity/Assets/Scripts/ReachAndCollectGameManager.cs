using System.Collections;
using System;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem.UI;

public class ReachAndCollectGameManager : MonoBehaviour
{
    private enum GameState
    {
        Countdown,
        Playing,
        Complete
    }

    [Header("Scene References")]
    [SerializeField] private Transform playerHand;
    [SerializeField] private ReachTarget target;

    [Header("Session")]
    [SerializeField] private int totalTargets = 12;
    [SerializeField] private float sessionDurationSeconds = 60f;
    [SerializeField] private float countdownSeconds = 3f;
    [SerializeField] private float targetLifetimeSeconds = 8f;
    [SerializeField] private float minimumTargetLifetimeSeconds = 6.5f;

    [Header("Spawn Area")]
    [SerializeField] private Vector2 spawnXBounds = new Vector2(-1.65f, 1.65f);
    [SerializeField] private Vector2 spawnZBounds = new Vector2(-1.55f, 1.75f);
    [SerializeField] private float targetHeight = 1f;
    [SerializeField] private float minimumDistanceFromHand = 0.45f;

    [Header("Target Visuals")]
    [SerializeField] private float targetDiameter = 0.70f;
    [SerializeField] private float minimumTargetDiameter = 0.55f;
    [SerializeField] private float targetPulseSpeed = 5f;
    [SerializeField] private float targetPulseAmount = 0.12f;

    [SerializeField]
    private Color targetColor = new Color(0.15f, 0.95f, 0.75f);

    [SerializeField]
    private Color targetMissColor = new Color(1f, 0.42f, 0.32f);

    [Header("Scoring")]
    [SerializeField] private int pointsPerTarget = 100;
    [SerializeField] private int streakBonus = 15;

    [Header("Session Recording")]
    [SerializeField] private float handSampleIntervalSeconds = 0.1f;

    private const string ReachAndCollectSceneName = "ReachAndCollect";
    private const string SampleSceneName = "SampleScene";

    private GameState state;

    private int score;
    private int successfulTargets;
    private int missedTargets;
    private int currentStreak;
    private int bestStreak;
    private int spawnedTargets;

    private float sessionTimeRemaining;
    private float sessionStartRealtime;
    private float nextHandSampleTime;

    private Coroutine countdownRoutine;
    private Coroutine spawnRoutine;

    private RehabQuestSessionResult currentSessionResult;
    private ReachTargetResult activeTargetResult;

    private Canvas canvas;

    private Text titleText;
    private Text scoreText;
    private Text timerText;
    private Text targetsText;
    private Text streakText;
    private Text feedbackText;
    private Text countdownText;
    private Text targetTimerText;

    private Image progressFill;
    private Image targetTimeFill;

    private GameObject completionPanel;

    private Text completionTitleText;
    private Text completionSummaryText;


    // =========================================================
    // BOOTSTRAP
    // =========================================================

    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
    private static void BootstrapReachAndCollect()
    {
        Scene activeScene = SceneManager.GetActiveScene();

        if (activeScene.name != ReachAndCollectSceneName)
        {
            return;
        }

        if (FindFirstObjectByType<ReachAndCollectGameManager>() != null)
        {
            return;
        }

        GameObject managerObject =
            new GameObject("ReachAndCollectGameManager");

        managerObject.AddComponent<ReachAndCollectGameManager>();
    }


    // =========================================================
    // UNITY LIFECYCLE
    // =========================================================

    private void Awake()
    {
        Time.timeScale = 1f;

        FindSceneReferences();
        PrepareTarget();
        BuildRuntimeUi();
    }

    private void Start()
    {
        RestartSession();
    }

    private void Update()
    {
        if (state != GameState.Playing)
        {
            return;
        }

        sessionTimeRemaining -= Time.deltaTime;

        if (sessionTimeRemaining <= 0f)
        {
            CompleteSession("Time Complete");
            return;
        }

        RecordPlayerHandSampleIfDue();

        UpdateHud();
    }


    // =========================================================
    // TARGET EVENTS
    // =========================================================

    public void HandleTargetCollected(
        ReachTarget collectedTarget,
        Vector3 collectionPosition)
    {
        if (state != GameState.Playing)
        {
            return;
        }

        if (collectedTarget != target)
        {
            return;
        }

        Vector3 recordedCollectionPosition =
            playerHand != null
                ? playerHand.position
                : collectionPosition;

        RecordTargetCollected(
            recordedCollectionPosition
        );

        successfulTargets++;

        currentStreak++;

        bestStreak = Mathf.Max(
            bestStreak,
            currentStreak
        );

        score +=
            pointsPerTarget +
            Mathf.Max(0, currentStreak - 1) * streakBonus;

        ShowFeedback(
            GetPositiveFeedback(),
            new Color(0.3f, 1f, 0.65f)
        );

        PlayCollectBurst(
            collectionPosition,
            targetColor
        );

        if (successfulTargets >= totalTargets)
        {
            CompleteSession("Exercise Complete");
            return;
        }

        QueueNextTarget(0.35f);

        UpdateHud();
    }


    public void HandleTargetMissed(ReachTarget missedTarget)
    {
        if (state != GameState.Playing)
        {
            return;
        }

        if (missedTarget != target)
        {
            return;
        }

        RecordTargetMissed();

        missedTargets++;

        currentStreak = 0;

        ShowFeedback(
            "Keep going!",
            targetMissColor
        );

        if (spawnedTargets >= totalTargets)
        {
            CompleteSession("Exercise Complete");
            return;
        }

        QueueNextTarget(0.25f);

        UpdateHud();
    }


    // =========================================================
    // SESSION CONTROL
    // =========================================================

    public void RestartSession()
    {
        Time.timeScale = 1f;

        if (countdownRoutine != null)
        {
            StopCoroutine(countdownRoutine);
            countdownRoutine = null;
        }

        if (spawnRoutine != null)
        {
            StopCoroutine(spawnRoutine);
            spawnRoutine = null;
        }

        score = 0;
        successfulTargets = 0;
        missedTargets = 0;
        currentStreak = 0;
        bestStreak = 0;
        spawnedTargets = 0;

        sessionTimeRemaining = sessionDurationSeconds;
        currentSessionResult = null;
        activeTargetResult = null;
        sessionStartRealtime = 0f;
        nextHandSampleTime = 0f;

        state = GameState.Countdown;

        if (target != null)
        {
            target.gameObject.SetActive(false);
        }

        if (completionPanel != null)
        {
            completionPanel.SetActive(false);
        }

        if (feedbackText != null)
        {
            feedbackText.text = "Get ready";
        }

        if (countdownText != null)
        {
            countdownText.gameObject.SetActive(true);
        }

        countdownRoutine =
            StartCoroutine(CountdownAndStart());

        UpdateHud();
    }


    public void ReturnToMenu()
    {
        Time.timeScale = 1f;

        SceneManager.LoadScene(
            SampleSceneName
        );
    }


    // =========================================================
    // COUNTDOWN
    // =========================================================

    private IEnumerator CountdownAndStart()
    {
        float remaining = countdownSeconds;

        countdownText.gameObject.SetActive(true);

        while (remaining > 0f)
        {
            countdownText.text =
                Mathf.CeilToInt(remaining).ToString();

            remaining -= Time.unscaledDeltaTime;

            yield return null;
        }

        countdownText.text = "Go!";

        yield return new WaitForSecondsRealtime(0.35f);

        countdownText.gameObject.SetActive(false);

        state = GameState.Playing;
        BeginSessionRecording();

        feedbackText.text =
            "Reach for the target";

        Debug.Log(
            "Reach & Collect session started."
        );

        SpawnNextTarget();

        countdownRoutine = null;
    }


    // =========================================================
    // TARGET SPAWNING
    // =========================================================

    private void QueueNextTarget(float delay)
    {
        if (spawnRoutine != null)
        {
            StopCoroutine(spawnRoutine);
        }

        spawnRoutine =
            StartCoroutine(
                SpawnAfterDelay(delay)
            );
    }


    private IEnumerator SpawnAfterDelay(float delay)
    {
        yield return new WaitForSeconds(delay);

        spawnRoutine = null;

        SpawnNextTarget();
    }


    private void SpawnNextTarget()
    {
        if (state != GameState.Playing)
        {
            return;
        }

        if (target == null)
        {
            Debug.LogWarning(
                "Reach & Collect target is missing."
            );

            return;
        }

        if (spawnedTargets >= totalTargets)
        {
            CompleteSession(
                "Exercise Complete"
            );

            return;
        }

        spawnedTargets++;

        float progress =
            totalTargets <= 1
                ? 1f
                : (float)(spawnedTargets - 1)
                    / (totalTargets - 1);

        float difficultyProgress =
            Mathf.SmoothStep(
                0f,
                1f,
                progress
            );

        float diameter =
            Mathf.Lerp(
                targetDiameter,
                minimumTargetDiameter,
                difficultyProgress
            );

        float lifetime =
            Mathf.Lerp(
                targetLifetimeSeconds,
                minimumTargetLifetimeSeconds,
                difficultyProgress
            );

        target.Configure(
            this,
            lifetime,
            targetPulseSpeed,
            targetPulseAmount
        );

        Vector3 spawnPosition =
            GetReachableSpawnPosition();

        RecordTargetSpawned(
            spawnedTargets,
            spawnPosition,
            lifetime,
            diameter
        );

        target.Activate(
            spawnPosition,
            diameter,
            targetColor
        );

        UpdateHud();
    }


    private Vector3 GetReachableSpawnPosition()
    {
        Vector3 handPosition =
            playerHand != null
                ? playerHand.position
                : Vector3.zero;

        Vector3 candidate = Vector3.zero;

        for (int attempt = 0; attempt < 20; attempt++)
        {
            candidate = new Vector3(
                UnityEngine.Random.Range(
                    spawnXBounds.x,
                    spawnXBounds.y
                ),
                targetHeight,
                UnityEngine.Random.Range(
                    spawnZBounds.x,
                    spawnZBounds.y
                )
            );

            if (
                Vector3.Distance(
                    candidate,
                    handPosition
                ) >= minimumDistanceFromHand
            )
            {
                return candidate;
            }
        }

        return candidate;
    }


    // =========================================================
    // SESSION COMPLETION
    // =========================================================

    private void CompleteSession(string heading)
    {
        if (state == GameState.Complete)
        {
            return;
        }

        state = GameState.Complete;

        if (target != null)
        {
            target.gameObject.SetActive(false);
        }

        if (spawnRoutine != null)
        {
            StopCoroutine(spawnRoutine);
            spawnRoutine = null;
        }

        if (countdownRoutine != null)
        {
            StopCoroutine(countdownRoutine);
            countdownRoutine = null;
        }

        RecordUnfinishedTarget();

        float timeUsed =
            sessionDurationSeconds -
            Mathf.Max(0f, sessionTimeRemaining);

        completionTitleText.text = heading;

        completionSummaryText.text =
            $"Score: {score}\n" +
            $"Targets collected: {successfulTargets} / {totalTargets}\n" +
            $"Missed targets: {missedTargets}\n" +
            $"Best streak: {bestStreak}\n" +
            $"Time used: {timeUsed:0}s";

        completionPanel.SetActive(true);

        feedbackText.text =
            "Session complete";

        UpdateHud();

        FinalizeSessionRecording(
            timeUsed
        );

        ExportSessionJson();

        Debug.Log(
            CreateSessionDebugSummary()
        );
    }


    // =========================================================
    // SESSION RECORDING
    // =========================================================

    private void BeginSessionRecording()
    {
        sessionStartRealtime =
            Time.realtimeSinceStartup;

        nextHandSampleTime =
            sessionStartRealtime;

        currentSessionResult =
            new RehabQuestSessionResult
            {
                patientName = RehabQuestSessionData.PatientName,
                patientAge = RehabQuestSessionData.PatientAge,
                dominantHand = RehabQuestSessionData.DominantHand,
                selectedExercise = RehabQuestSessionData.SelectedExercise,
                selectedDifficulty = RehabQuestSessionData.SelectedDifficulty,
                gameName = "Reach & Collect",
                sessionStartTimeUtc = DateTime.UtcNow.ToString("o"),
                totalTargets = totalTargets
            };

        RecordPlayerHandSampleIfDue();
    }


    private void RecordTargetSpawned(
        int targetNumber,
        Vector3 spawnPosition,
        float lifetime,
        float diameter)
    {
        if (currentSessionResult == null)
        {
            return;
        }

        activeTargetResult =
            new ReachTargetResult
            {
                targetNumber = targetNumber,
                spawnTimeSeconds = GetSessionElapsedSeconds(),
                targetLifetimeSeconds = lifetime,
                targetDiameter = diameter,
                spawnPosition = new SerializableVector3(spawnPosition)
            };

        currentSessionResult.targetEvents.Add(
            activeTargetResult
        );
    }


    private void RecordTargetCollected(
        Vector3 collectionPosition)
    {
        if (activeTargetResult == null)
        {
            return;
        }

        float elapsed =
            GetSessionElapsedSeconds();

        activeTargetResult.collected = true;
        activeTargetResult.missed = false;
        activeTargetResult.completionTimeSeconds = elapsed;
        activeTargetResult.timeToCompleteSeconds =
            Mathf.Max(
                0f,
                elapsed - activeTargetResult.spawnTimeSeconds
            );
        activeTargetResult.collectionPosition =
            new SerializableVector3(collectionPosition);

        activeTargetResult = null;
    }


    private void RecordTargetMissed()
    {
        if (activeTargetResult == null)
        {
            return;
        }

        float elapsed =
            GetSessionElapsedSeconds();

        activeTargetResult.collected = false;
        activeTargetResult.missed = true;
        activeTargetResult.completionTimeSeconds = elapsed;
        activeTargetResult.timeToCompleteSeconds =
            Mathf.Max(
                0f,
                elapsed - activeTargetResult.spawnTimeSeconds
            );

        activeTargetResult = null;
    }


    private void RecordUnfinishedTarget()
    {
        if (activeTargetResult == null)
        {
            return;
        }

        float elapsed =
            GetSessionElapsedSeconds();

        activeTargetResult.collected = false;
        activeTargetResult.missed = true;
        activeTargetResult.completionTimeSeconds = elapsed;
        activeTargetResult.timeToCompleteSeconds =
            Mathf.Max(
                0f,
                elapsed - activeTargetResult.spawnTimeSeconds
            );

        activeTargetResult = null;
    }


    private void RecordPlayerHandSampleIfDue()
    {
        if (
            currentSessionResult == null ||
            playerHand == null ||
            handSampleIntervalSeconds <= 0f
        )
        {
            return;
        }

        float now =
            Time.realtimeSinceStartup;

        if (now < nextHandSampleTime)
        {
            return;
        }

        currentSessionResult.playerHandSamples.Add(
            new PlayerHandSample
            {
                timeSeconds = GetSessionElapsedSeconds(),
                position = new SerializableVector3(
                    playerHand.position
                )
            }
        );

        nextHandSampleTime =
            now + handSampleIntervalSeconds;
    }


    private void FinalizeSessionRecording(
        float timeUsed)
    {
        if (currentSessionResult == null)
        {
            return;
        }

        RecordPlayerHandSampleIfDue();

        currentSessionResult.sessionDurationSeconds = timeUsed;
        currentSessionResult.targetsSpawned = spawnedTargets;
        currentSessionResult.targetsCollected = successfulTargets;
        currentSessionResult.missedTargets = missedTargets;
        currentSessionResult.score = score;
        currentSessionResult.bestStreak = bestStreak;

        RehabQuestSessionData.SetLatestReachAndCollectResult(
            currentSessionResult
        );
    }


    private void ExportSessionJson()
    {
        if (
            RehabQuestSessionJsonExporter.TryExportReachAndCollectSession(
                currentSessionResult,
                out string savedPath
            )
        )
        {
            Debug.Log(
                "Reach & Collect session JSON saved:\n" +
                savedPath
            );
        }
    }


    private float GetSessionElapsedSeconds()
    {
        if (sessionStartRealtime <= 0f)
        {
            return 0f;
        }

        return Mathf.Max(
            0f,
            Time.realtimeSinceStartup - sessionStartRealtime
        );
    }


    private string CreateSessionDebugSummary()
    {
        if (currentSessionResult == null)
        {
            return "Reach & Collect session result was not available.";
        }

        return
            "Reach & Collect Session Result\n" +
            "------------------------------\n" +
            $"Game: {currentSessionResult.gameName}\n" +
            $"Difficulty: {currentSessionResult.selectedDifficulty}\n" +
            $"Targets: {currentSessionResult.totalTargets}\n" +
            $"Spawned: {currentSessionResult.targetsSpawned}\n" +
            $"Collected: {currentSessionResult.targetsCollected}\n" +
            $"Missed: {currentSessionResult.missedTargets}\n" +
            $"Score: {currentSessionResult.score}\n" +
            $"Best Streak: {currentSessionResult.bestStreak}\n" +
            $"Duration: {currentSessionResult.sessionDurationSeconds:0.0}s\n" +
            "Hand Samples: " +
            $"{currentSessionResult.playerHandSamples.Count}";
    }


    // =========================================================
    // SCENE REFERENCES
    // =========================================================

    private void FindSceneReferences()
    {
        if (playerHand == null)
        {
            GameObject playerHandObject =
                GameObject.Find("PlayerHand");

            if (playerHandObject != null)
            {
                playerHand =
                    playerHandObject.transform;
            }
        }

        if (target == null)
        {
            GameObject targetObject =
                GameObject.Find("Target");

            if (targetObject != null)
            {
                target =
                    targetObject.GetComponent<ReachTarget>();

                if (target == null)
                {
                    target =
                        targetObject.AddComponent<ReachTarget>();
                }
            }
        }
    }


    private void PrepareTarget()
    {
        if (target == null)
        {
            Debug.LogWarning(
                "Reach & Collect target was not found. " +
                "Gameplay cannot spawn targets."
            );

            return;
        }

        target.Configure(
            this,
            targetLifetimeSeconds,
            targetPulseSpeed,
            targetPulseAmount
        );

        target.gameObject.SetActive(false);
    }


    // =========================================================
    // RUNTIME UI
    // =========================================================

    private void BuildRuntimeUi()
    {
        canvas = CreateCanvas();

        GameObject topPanel =
            CreatePanel(
                "Top HUD",
                canvas.transform,
                new Color(
                    0.05f,
                    0.07f,
                    0.09f,
                    0.82f
                )
            );

        RectTransform topRect =
            topPanel.GetComponent<RectTransform>();

        topRect.anchorMin =
            new Vector2(0.02f, 0.82f);

        topRect.anchorMax =
            new Vector2(0.98f, 0.98f);

        topRect.offsetMin =
            Vector2.zero;

        topRect.offsetMax =
            Vector2.zero;


        titleText =
            CreateText(
                "Title",
                topPanel.transform,
                "Reach & Collect",
                28,
                FontStyle.Bold,
                TextAnchor.MiddleLeft
            );

        SetRect(
            titleText.rectTransform,
            new Vector2(0.03f, 0.54f),
            new Vector2(0.32f, 0.92f)
        );


        scoreText =
            CreateText(
                "Score",
                topPanel.transform,
                "Score: 0",
                22,
                FontStyle.Bold,
                TextAnchor.MiddleLeft
            );

        SetRect(
            scoreText.rectTransform,
            new Vector2(0.34f, 0.56f),
            new Vector2(0.52f, 0.9f)
        );


        timerText =
            CreateText(
                "Timer",
                topPanel.transform,
                "Time: 60",
                22,
                FontStyle.Bold,
                TextAnchor.MiddleLeft
            );

        SetRect(
            timerText.rectTransform,
            new Vector2(0.53f, 0.56f),
            new Vector2(0.68f, 0.9f)
        );


        targetsText =
            CreateText(
                "Targets",
                topPanel.transform,
                "Targets: 0/12",
                22,
                FontStyle.Bold,
                TextAnchor.MiddleLeft
            );

        SetRect(
            targetsText.rectTransform,
            new Vector2(0.69f, 0.56f),
            new Vector2(0.86f, 0.9f)
        );


        streakText =
            CreateText(
                "Streak",
                topPanel.transform,
                "Streak: 0",
                22,
                FontStyle.Bold,
                TextAnchor.MiddleLeft
            );

        SetRect(
            streakText.rectTransform,
            new Vector2(0.86f, 0.56f),
            new Vector2(0.98f, 0.9f)
        );


        progressFill =
            CreateProgressBar(
                "Progress",
                topPanel.transform,
                new Vector2(0.03f, 0.18f),
                new Vector2(0.67f, 0.38f),
                new Color(
                    0.25f,
                    0.9f,
                    0.7f
                )
            );


        targetTimeFill =
            CreateProgressBar(
                "Target Time",
                topPanel.transform,
                new Vector2(0.7f, 0.18f),
                new Vector2(0.97f, 0.38f),
                new Color(
                    1f,
                    0.78f,
                    0.25f
                )
            );


        targetTimerText =
            CreateText(
                "Target Timer",
                topPanel.transform,
                "Target",
                14,
                FontStyle.Normal,
                TextAnchor.MiddleCenter
            );

        SetRect(
            targetTimerText.rectTransform,
            new Vector2(0.7f, 0.02f),
            new Vector2(0.97f, 0.17f)
        );


        feedbackText =
            CreateText(
                "Feedback",
                canvas.transform,
                "",
                32,
                FontStyle.Bold,
                TextAnchor.MiddleCenter
            );

        feedbackText.color =
            new Color(
                0.95f,
                1f,
                0.85f
            );

        SetRect(
            feedbackText.rectTransform,
            new Vector2(0.25f, 0.68f),
            new Vector2(0.75f, 0.79f)
        );


        countdownText =
            CreateText(
                "Countdown",
                canvas.transform,
                "",
                76,
                FontStyle.Bold,
                TextAnchor.MiddleCenter
            );

        countdownText.color =
            new Color(
                0.25f,
                1f,
                0.75f
            );

        SetRect(
            countdownText.rectTransform,
            new Vector2(0.35f, 0.36f),
            new Vector2(0.65f, 0.62f)
        );


        BuildCompletionPanel();
    }


    // =========================================================
    // CANVAS + EVENT SYSTEM
    // =========================================================

    private Canvas CreateCanvas()
    {
        GameObject canvasObject =
            new GameObject(
                "ReachAndCollectCanvas"
            );

        Canvas createdCanvas =
            canvasObject.AddComponent<Canvas>();

        createdCanvas.renderMode =
            RenderMode.ScreenSpaceOverlay;


        CanvasScaler scaler =
            canvasObject.AddComponent<CanvasScaler>();

        scaler.uiScaleMode =
            CanvasScaler.ScaleMode.ScaleWithScreenSize;

        scaler.referenceResolution =
            new Vector2(1920, 1080);


        canvasObject.AddComponent<GraphicRaycaster>();

        ConfigureEventSystem();

        return createdCanvas;
    }


    private void ConfigureEventSystem()
    {
        EventSystem eventSystem =
            FindFirstObjectByType<EventSystem>();

        if (eventSystem == null)
        {
            GameObject eventSystemObject =
                new GameObject("EventSystem");

            eventSystem =
                eventSystemObject.AddComponent<EventSystem>();
        }


        // Remove the old Input Manager module
        // because the project uses the New Input System.

        StandaloneInputModule legacyModule =
            eventSystem.GetComponent<StandaloneInputModule>();

        if (legacyModule != null)
        {
            Destroy(legacyModule);

            Debug.Log(
                "Removed legacy StandaloneInputModule."
            );
        }


        // Add the New Input System UI module
        // if it doesn't already exist.

        InputSystemUIInputModule inputSystemModule =
            eventSystem.GetComponent<InputSystemUIInputModule>();

        if (inputSystemModule == null)
        {
            inputSystemModule =
                eventSystem.gameObject.AddComponent<InputSystemUIInputModule>();
        }


        eventSystem.enabled = true;

        Debug.Log(
            "Reach & Collect EventSystem configured " +
            "for the new Input System."
        );
    }


    // =========================================================
    // COMPLETION PANEL
    // =========================================================

    private void BuildCompletionPanel()
    {
        completionPanel =
            CreatePanel(
                "Completion Panel",
                canvas.transform,
                new Color(
                    0.04f,
                    0.06f,
                    0.08f,
                    0.94f
                )
            );

        RectTransform panelRect =
            completionPanel.GetComponent<RectTransform>();

        panelRect.anchorMin =
            new Vector2(0.32f, 0.22f);

        panelRect.anchorMax =
            new Vector2(0.68f, 0.74f);

        panelRect.offsetMin =
            Vector2.zero;

        panelRect.offsetMax =
            Vector2.zero;


        completionTitleText =
            CreateText(
                "Completion Title",
                completionPanel.transform,
                "Exercise Complete",
                34,
                FontStyle.Bold,
                TextAnchor.MiddleCenter
            );

        SetRect(
            completionTitleText.rectTransform,
            new Vector2(0.08f, 0.78f),
            new Vector2(0.92f, 0.94f)
        );


        completionSummaryText =
            CreateText(
                "Completion Summary",
                completionPanel.transform,
                "",
                22,
                FontStyle.Normal,
                TextAnchor.UpperLeft
            );

        SetRect(
            completionSummaryText.rectTransform,
            new Vector2(0.12f, 0.34f),
            new Vector2(0.88f, 0.76f)
        );


        Button restartButton =
            CreateButton(
                "Restart Button",
                completionPanel.transform,
                "Restart"
            );

        SetRect(
            restartButton.GetComponent<RectTransform>(),
            new Vector2(0.12f, 0.12f),
            new Vector2(0.46f, 0.26f)
        );

        restartButton.onClick.AddListener(
            RestartSession
        );


        Button menuButton =
            CreateButton(
                "Menu Button",
                completionPanel.transform,
                "Return to Menu"
            );

        SetRect(
            menuButton.GetComponent<RectTransform>(),
            new Vector2(0.54f, 0.12f),
            new Vector2(0.88f, 0.26f)
        );

        menuButton.onClick.AddListener(
            ReturnToMenu
        );


        completionPanel.SetActive(false);
    }


    // =========================================================
    // HUD
    // =========================================================

    private void UpdateHud()
    {
        if (scoreText == null)
        {
            return;
        }


        scoreText.text =
            $"Score: {score}";


        timerText.text = $"Time: {Mathf.CeilToInt(Mathf.Max(0f, sessionTimeRemaining))}";


        targetsText.text =
            $"Targets: {successfulTargets}/{totalTargets}";


        streakText.text =
            $"Streak: {currentStreak}";


        float progress =
            totalTargets <= 0
                ? 0f
                : (float)successfulTargets
                    / totalTargets;

        progressFill.fillAmount =
            Mathf.Clamp01(progress);


        if (
            state == GameState.Playing &&
            target != null &&
            target.gameObject.activeSelf
        )
        {
            float targetTimeProgress =
                target.LifetimeSeconds <= 0f
                    ? 0f
                    : target.TimeRemaining
                        / target.LifetimeSeconds;


            targetTimeFill.fillAmount =
                Mathf.Clamp01(
                    targetTimeProgress
                );


            targetTimerText.text =
                $"Target time: {target.TimeRemaining:0.0}s";
        }
        else
        {
            targetTimeFill.fillAmount = 0f;

            targetTimerText.text =
                "Target time";
        }
    }


    // =========================================================
    // FEEDBACK
    // =========================================================

    private void ShowFeedback(
        string message,
        Color color)
    {
        if (feedbackText == null)
        {
            return;
        }

        feedbackText.text = message;
        feedbackText.color = color;
    }


    private string GetPositiveFeedback()
    {
        string[] messages =
        {
            "Great!",
            "Nice!",
            "Well done!",
            "Keep it up!"
        };

        return messages[
            UnityEngine.Random.Range(
                0,
                messages.Length
            )
        ];
    }


    // =========================================================
    // PARTICLE EFFECT
    // =========================================================

    private void PlayCollectBurst(
        Vector3 position,
        Color color)
    {
        GameObject burstObject =
            new GameObject(
                "Target Collect Burst"
            );

        burstObject.transform.position =
            position;


        ParticleSystem particles =
            burstObject.AddComponent<ParticleSystem>();

        ParticleSystem.MainModule main =
            particles.main;

        main.startLifetime = 0.45f;
        main.startSpeed = 2.4f;
        main.startSize = 0.08f;
        main.startColor = color;


        ParticleSystem.EmissionModule emission =
            particles.emission;

        emission.rateOverTime = 0f;

        emission.SetBursts(
            new[]
            {
                new ParticleSystem.Burst(
                    0f,
                    22
                )
            }
        );


        ParticleSystem.ShapeModule shape =
            particles.shape;

        shape.shapeType =
            ParticleSystemShapeType.Sphere;

        shape.radius = 0.12f;


        Destroy(
            burstObject,
            1.2f
        );
    }


    // =========================================================
    // UI HELPERS
    // =========================================================

    private GameObject CreatePanel(
        string name,
        Transform parent,
        Color color)
    {
        GameObject panel =
            new GameObject(name);

        panel.transform.SetParent(
            parent,
            false
        );


        Image image =
            panel.AddComponent<Image>();

        image.color = color;


        return panel;
    }


    private Text CreateText(
        string name,
        Transform parent,
        string text,
        int fontSize,
        FontStyle style,
        TextAnchor anchor)
    {
        GameObject textObject =
            new GameObject(name);

        textObject.transform.SetParent(
            parent,
            false
        );


        Text label =
            textObject.AddComponent<Text>();

        label.text = text;

        label.font = GetDefaultFont();

        label.fontSize = fontSize;

        label.fontStyle = style;

        label.alignment = anchor;

        label.color = Color.white;

        label.horizontalOverflow =
            HorizontalWrapMode.Wrap;

        label.verticalOverflow =
            VerticalWrapMode.Truncate;


        return label;
    }


    private Button CreateButton(
        string name,
        Transform parent,
        string label)
    {
        GameObject buttonObject =
            CreatePanel(
                name,
                parent,
                new Color(
                    0.1f,
                    0.55f,
                    0.72f,
                    1f
                )
            );


        Button button =
            buttonObject.AddComponent<Button>();


        Text buttonText =
            CreateText(
                "Label",
                buttonObject.transform,
                label,
                22,
                FontStyle.Bold,
                TextAnchor.MiddleCenter
            );


        SetRect(
            buttonText.rectTransform,
            Vector2.zero,
            Vector2.one
        );


        return button;
    }


    private Image CreateProgressBar(
        string name,
        Transform parent,
        Vector2 anchorMin,
        Vector2 anchorMax,
        Color fillColor)
    {
        GameObject background =
            CreatePanel(
                name + " Background",
                parent,
                new Color(
                    1f,
                    1f,
                    1f,
                    0.18f
                )
            );


        SetRect(
            background.GetComponent<RectTransform>(),
            anchorMin,
            anchorMax
        );


        GameObject fill =
            CreatePanel(
                name + " Fill",
                background.transform,
                fillColor
            );


        Image fillImage =
            fill.GetComponent<Image>();

        fillImage.type =
            Image.Type.Filled;

        fillImage.fillMethod =
            Image.FillMethod.Horizontal;

        fillImage.fillOrigin =
            (int)Image.OriginHorizontal.Left;

        fillImage.fillAmount = 0f;


        SetRect(
            fill.GetComponent<RectTransform>(),
            Vector2.zero,
            Vector2.one
        );


        return fillImage;
    }


    private void SetRect(
        RectTransform rectTransform,
        Vector2 anchorMin,
        Vector2 anchorMax)
    {
        rectTransform.anchorMin =
            anchorMin;

        rectTransform.anchorMax =
            anchorMax;

        rectTransform.offsetMin =
            Vector2.zero;

        rectTransform.offsetMax =
            Vector2.zero;
    }


    private Font GetDefaultFont()
    {
        Font font =
            Resources.GetBuiltinResource<Font>(
                "LegacyRuntime.ttf"
            );

        if (font == null)
        {
            font =
                Resources.GetBuiltinResource<Font>(
                    "Arial.ttf"
                );
        }

        return font;
    }


    // =========================================================
    // VALIDATION
    // =========================================================

    private void OnValidate()
    {
        totalTargets =
            Mathf.Max(
                1,
                totalTargets
            );


        sessionDurationSeconds =
            Mathf.Max(
                5f,
                sessionDurationSeconds
            );


        countdownSeconds =
            Mathf.Max(
                0f,
                countdownSeconds
            );


        targetLifetimeSeconds =
            Mathf.Max(
                1f,
                targetLifetimeSeconds
            );

        minimumTargetLifetimeSeconds =
            Mathf.Clamp(
                minimumTargetLifetimeSeconds,
                1f,
                targetLifetimeSeconds
            );


        targetDiameter =
            Mathf.Max(
                0.1f,
                targetDiameter
            );


        minimumTargetDiameter =
            Mathf.Clamp(
                minimumTargetDiameter,
                0.1f,
                targetDiameter
            );


        minimumDistanceFromHand =
            Mathf.Max(
                0f,
                minimumDistanceFromHand
            );


        handSampleIntervalSeconds =
            Mathf.Max(
                0.02f,
                handSampleIntervalSeconds
            );
    }
}

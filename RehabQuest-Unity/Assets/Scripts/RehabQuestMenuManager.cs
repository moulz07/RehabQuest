using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Text.RegularExpressions;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem.UI;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

public class RehabQuestMenuManager : MonoBehaviour
{
    private enum MenuScreen
    {
        Dashboard,
        SessionHistory,
        PatientSetup,
        ExerciseSelection
    }

    private const string MenuSceneName = "SampleScene";
    private const string ReachAndCollectSceneName = "ReachAndCollect";
    private const string ExerciseReachAndCollect = "Reach & Collect";
    private const string SessionFolderName = "RehabQuestSessions";
    private const string SessionFilePattern = "reach_and_collect_session_*.json";

    private readonly Color backgroundColor = new Color(0.035f, 0.06f, 0.095f);
    private readonly Color panelColor = new Color(0.07f, 0.105f, 0.145f, 0.94f);
    private readonly Color cardColor = new Color(0.085f, 0.13f, 0.18f, 0.96f);
    private readonly Color accentColor = new Color(0.2f, 0.95f, 0.78f);
    private readonly Color secondaryAccentColor = new Color(0.18f, 0.55f, 0.95f);
    private readonly Color warningColor = new Color(1f, 0.45f, 0.38f);
    private readonly Color mutedTextColor = new Color(0.72f, 0.82f, 0.9f);

    private Canvas canvas;
    private GameObject dashboardPanel;
    private GameObject patientPanel;
    private GameObject exercisePanel;
    private GameObject historyPanel;
    private Transform historyListContent;
    private Text historyStatusText;
    private Text historyDetailsText;

    private sealed class HistoryEntry
    {
        public string filePath;
        public RehabQuestSessionResult result;
        public HashSet<string> fields;
    }

    private InputField patientNameInput;
    private InputField ageInput;
    private Text validationText;
    private Text exercisePatientSummaryText;
    private Text selectedDifficultyText;

    private string selectedDominantHand = "";
    private string selectedDifficulty = "Easy";
    private Button rightHandButton;
    private Button leftHandButton;
    private Button easyButton;
    private Button mediumButton;
    private Button hardButton;

    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
    private static void BootstrapMenu()
    {
        if (SceneManager.GetActiveScene().name != MenuSceneName)
        {
            return;
        }

        if (FindFirstObjectByType<RehabQuestMenuManager>() != null)
        {
            return;
        }

        GameObject managerObject = new GameObject("RehabQuestMenuManager");
        managerObject.AddComponent<RehabQuestMenuManager>();
    }

    private void Awake()
    {
        Time.timeScale = 1f;
        ConfigureCamera();
        BuildUi();
        ShowDashboard();
    }

    private void ConfigureCamera()
    {
        Camera mainCamera = Camera.main;

        if (mainCamera == null)
        {
            return;
        }

        mainCamera.clearFlags = CameraClearFlags.SolidColor;
        mainCamera.backgroundColor = backgroundColor;
    }

    private void BuildUi()
    {
        canvas = CreateCanvas();
        BuildDashboard();
        BuildSessionHistory();
        BuildPatientSetup();
        BuildExerciseSelection();
    }

    private void ShowDashboard()
    {
        ShowScreen(MenuScreen.Dashboard);
    }

    private void ShowSessionHistory()
    {
        ShowScreen(MenuScreen.SessionHistory);
        RefreshSessionHistory();
    }

    private void ShowPatientSetup()
    {
        validationText.text = "";
        ShowScreen(MenuScreen.PatientSetup);
    }

    private void ShowExerciseSelection()
    {
        exercisePatientSummaryText.text =
            $"{RehabQuestSessionData.PatientName} | Age {RehabQuestSessionData.PatientAge} | {RehabQuestSessionData.DominantHand} hand";

        selectedDifficultyText.text =
            $"Selected difficulty: {selectedDifficulty}";

        ShowScreen(MenuScreen.ExerciseSelection);
    }

    private void ShowScreen(MenuScreen screen)
    {
        dashboardPanel.SetActive(screen == MenuScreen.Dashboard);
        historyPanel.SetActive(screen == MenuScreen.SessionHistory);
        patientPanel.SetActive(screen == MenuScreen.PatientSetup);
        exercisePanel.SetActive(screen == MenuScreen.ExerciseSelection);
    }

    private void ContinueFromPatientSetup()
    {
        string patientName = patientNameInput.text.Trim();
        string ageText = ageInput.text.Trim();

        if (string.IsNullOrWhiteSpace(patientName))
        {
            validationText.text = "Please enter a patient name.";
            return;
        }

        if (!int.TryParse(ageText, out int age) || age <= 0 || age > 120)
        {
            validationText.text = "Please enter a reasonable positive age.";
            return;
        }

        if (string.IsNullOrWhiteSpace(selectedDominantHand))
        {
            validationText.text = "Please select a dominant hand.";
            return;
        }

        RehabQuestSessionData.SetPatientDetails(
            patientName,
            age,
            selectedDominantHand
        );

        validationText.text = "";
        ShowExerciseSelection();
    }

    private void SelectDominantHand(string hand)
    {
        selectedDominantHand = hand;
        SetButtonSelected(rightHandButton, hand == "Right");
        SetButtonSelected(leftHandButton, hand == "Left");
    }

    private void SelectDifficulty(string difficulty)
    {
        selectedDifficulty = difficulty;
        SetButtonSelected(easyButton, difficulty == "Easy");
        SetButtonSelected(mediumButton, difficulty == "Medium");
        SetButtonSelected(hardButton, difficulty == "Hard");

        if (selectedDifficultyText != null)
        {
            selectedDifficultyText.text =
                $"Selected difficulty: {selectedDifficulty}";
        }
    }

    private void StartReachAndCollect()
    {
        RehabQuestSessionData.SetExerciseSelection(
            ExerciseReachAndCollect,
            selectedDifficulty
        );

        SceneManager.LoadScene(ReachAndCollectSceneName);
    }

    private void StartTestSession()
    {
        RehabQuestSessionData.SetPatientDetails("Test Patient", 25, "Right");
        RehabQuestSessionData.SetTestSession(true);
        selectedDifficulty = "Easy";
        StartReachAndCollect();
    }

    private void BuildDashboard()
    {
        dashboardPanel = CreateFullScreenPanel("Dashboard Panel");

        GameObject heroCard = CreatePanel(
            "Hero Card",
            dashboardPanel.transform,
            panelColor
        );

        SetRect(
            heroCard.GetComponent<RectTransform>(),
            new Vector2(0.16f, 0.18f),
            new Vector2(0.84f, 0.86f)
        );

        Text logoText = CreateText(
            "Logo",
            heroCard.transform,
            "REHABQUEST",
            56,
            FontStyle.Bold,
            TextAnchor.MiddleCenter
        );

        logoText.color = accentColor;
        SetRect(logoText.rectTransform, new Vector2(0.08f, 0.72f), new Vector2(0.92f, 0.91f));

        Text subtitleText = CreateText(
            "Subtitle",
            heroCard.transform,
            "Interactive Neurorehabilitation",
            30,
            FontStyle.Bold,
            TextAnchor.MiddleCenter
        );

        SetRect(subtitleText.rectTransform, new Vector2(0.08f, 0.62f), new Vector2(0.92f, 0.72f));

        Text descriptionText = CreateText(
            "Description",
            heroCard.transform,
            "Move, play, and track your rehabilitation progress.",
            22,
            FontStyle.Normal,
            TextAnchor.MiddleCenter
        );

        descriptionText.color = mutedTextColor;
        SetRect(descriptionText.rectTransform, new Vector2(0.12f, 0.5f), new Vector2(0.88f, 0.6f));

        Button startButton = CreateButton(
            "Start Session Button",
            heroCard.transform,
            "Start Session",
            accentColor
        );

        SetRect(startButton.GetComponent<RectTransform>(), new Vector2(0.28f, 0.42f), new Vector2(0.72f, 0.52f));
        startButton.onClick.AddListener(ShowPatientSetup);

        Button testSessionButton = CreateButton("Test Session Button", heroCard.transform, "Test Session", secondaryAccentColor);
        SetRect(testSessionButton.GetComponent<RectTransform>(), new Vector2(0.28f, 0.29f), new Vector2(0.72f, 0.39f));
        testSessionButton.onClick.AddListener(StartTestSession);

        Button historyButton = CreateButton(
            "Session History Button",
            heroCard.transform,
            "Session History",
            secondaryAccentColor
        );

        SetRect(historyButton.GetComponent<RectTransform>(), new Vector2(0.22f, 0.16f), new Vector2(0.47f, 0.26f));
        historyButton.onClick.AddListener(ShowSessionHistory);

        Button settingsButton = CreateButton(
            "Settings Button",
            heroCard.transform,
            "Settings",
            secondaryAccentColor
        );

        SetRect(settingsButton.GetComponent<RectTransform>(), new Vector2(0.53f, 0.16f), new Vector2(0.78f, 0.26f));
        settingsButton.interactable = false;

        Text statusText = CreateText(
            "Tracking Status",
            heroCard.transform,
            "Camera Tracking Ready  |  MediaPipe Tracking",
            18,
            FontStyle.Bold,
            TextAnchor.MiddleCenter
        );

        statusText.color = accentColor;
        SetRect(statusText.rectTransform, new Vector2(0.18f, 0.05f), new Vector2(0.82f, 0.12f));
    }

    private void BuildSessionHistory()
    {
        historyPanel = CreateFullScreenPanel("Session History Panel");

        Text title = CreateText("Session History Title", historyPanel.transform,
            "Session History", 42, FontStyle.Bold, TextAnchor.MiddleCenter);
        title.color = accentColor;
        SetRect(title.rectTransform, new Vector2(0.2f, 0.87f), new Vector2(0.8f, 0.97f));

        historyStatusText = CreateText("Session History Status", historyPanel.transform,
            "", 17, FontStyle.Normal, TextAnchor.MiddleCenter);
        historyStatusText.color = mutedTextColor;
        SetRect(historyStatusText.rectTransform, new Vector2(0.1f, 0.81f), new Vector2(0.9f, 0.87f));

        GameObject listCard = CreatePanel("Session History List", historyPanel.transform, panelColor);
        SetRect(listCard.GetComponent<RectTransform>(), new Vector2(0.06f, 0.18f), new Vector2(0.44f, 0.79f));
        CreateScrollArea("Session List Scroll", listCard.transform,
            new Vector2(0.04f, 0.04f), new Vector2(0.96f, 0.96f), out historyListContent);

        GameObject detailCard = CreatePanel("Session Details Card", historyPanel.transform, panelColor);
        SetRect(detailCard.GetComponent<RectTransform>(), new Vector2(0.48f, 0.18f), new Vector2(0.94f, 0.79f));
        historyDetailsText = CreateText("Session Details", detailCard.transform,
            "Select a session to view its details.", 18, FontStyle.Normal, TextAnchor.UpperLeft);
        historyDetailsText.color = Color.white;
        historyDetailsText.horizontalOverflow = HorizontalWrapMode.Wrap;
        historyDetailsText.verticalOverflow = VerticalWrapMode.Overflow;
        SetRect(historyDetailsText.rectTransform, new Vector2(0.06f, 0.05f), new Vector2(0.94f, 0.95f));

        Button backButton = CreateButton("History Back Button", historyPanel.transform,
            "Back", secondaryAccentColor);
        SetRect(backButton.GetComponent<RectTransform>(), new Vector2(0.06f, 0.06f), new Vector2(0.2f, 0.14f));
        backButton.onClick.AddListener(ShowDashboard);

        historyPanel.SetActive(false);
    }

    private void RefreshSessionHistory()
    {
        ClearChildren(historyListContent);
        historyDetailsText.text = "Select a session to view its details.";

        if (string.IsNullOrWhiteSpace(Application.persistentDataPath))
        {
            historyStatusText.text = "Session storage is unavailable on this device.";
            return;
        }

        string directory = Path.Combine(Application.persistentDataPath, SessionFolderName);
        if (!Directory.Exists(directory))
        {
            historyStatusText.text = "No session history folder exists yet. Complete a session to create one.";
            return;
        }

        string[] paths;
        try
        {
            paths = Directory.GetFiles(directory, SessionFilePattern);
        }
        catch (Exception exception)
        {
            historyStatusText.text = "Could not read session history: " + exception.Message;
            return;
        }

        Array.Sort(paths, StringComparer.Ordinal);
        Array.Reverse(paths);

        int loadedCount = 0;
        int skippedCount = 0;
        foreach (string path in paths)
        {
            try
            {
                string json = File.ReadAllText(path);
                RehabQuestSessionResult result = JsonUtility.FromJson<RehabQuestSessionResult>(json);
                HashSet<string> fields = ReadJsonFieldNames(json);
                if (result == null ||
                    (!fields.Contains("schemaVersion") &&
                     !fields.Contains("sessionStartTimeUtc") &&
                     !fields.Contains("patientName") &&
                     !fields.Contains("selectedExercise")))
                {
                    skippedCount++;
                    continue;
                }

                AddHistoryEntry(new HistoryEntry { filePath = path, result = result, fields = fields });
                loadedCount++;
            }
            catch (Exception exception)
            {
                skippedCount++;
                Debug.LogWarning("Skipping unreadable RehabQuest session file '" + path + "': " + exception.Message);
            }
        }

        if (loadedCount == 0 && skippedCount == 0)
        {
            historyStatusText.text = "No saved sessions found. Complete a gameplay session and return here.";
        }
        else if (loadedCount == 0)
        {
            historyStatusText.text = "No readable sessions found. " + skippedCount + " file(s) could not be loaded.";
        }
        else
        {
            historyStatusText.text = loadedCount + " session(s) loaded" +
                (skippedCount > 0 ? " · " + skippedCount + " unreadable file(s) skipped" : "");
        }
    }

    private void AddHistoryEntry(HistoryEntry entry)
    {
        RehabQuestSessionResult result = entry.result;
        DateTime sessionDate;
        string dateLabel = HasField(entry, "sessionStartTimeUtc") &&
            DateTime.TryParse(result.sessionStartTimeUtc, CultureInfo.InvariantCulture,
                DateTimeStyles.AssumeUniversal | DateTimeStyles.AdjustToUniversal, out sessionDate)
            ? sessionDate.ToLocalTime().ToString("g")
            : File.GetLastWriteTime(entry.filePath).ToString("g");

        string patient = FieldText(result.patientName);
        string exercise = FieldText(result.selectedExercise);
        string score = HasField(entry, "score") ? result.score.ToString() : "Not available";
        string sessionType = HasField(entry, "isTestSession") && result.isTestSession ? " [TEST]" : "";
        Button sessionButton = CreateButton("Session Entry", historyListContent,
            dateLabel + sessionType + "\n" + patient + " · " + exercise + " · Score " + score,
            secondaryAccentColor);
        sessionButton.GetComponentInChildren<Text>().fontSize = 17;
        sessionButton.GetComponentInChildren<Text>().alignment = TextAnchor.MiddleLeft;
        LayoutElement layout = sessionButton.gameObject.AddComponent<LayoutElement>();
        layout.minHeight = 82f;
        layout.preferredHeight = 82f;
        sessionButton.onClick.AddListener(() => ShowSessionDetails(entry, dateLabel));
    }

    private void ShowSessionDetails(HistoryEntry entry, string dateLabel)
    {
        RehabQuestSessionResult result = entry.result;
        historyDetailsText.text =
            "Session Details\n\n" +
            "Date: " + dateLabel + "\n" +
            "Patient: " + FieldText(result.patientName) + "\n" +
            "Session type: " + (!HasField(entry, "isTestSession") ? "Unknown" : result.isTestSession ? "TEST" : "Normal") + "\n" +
            "Age: " + (result.patientAge > 0 ? result.patientAge.ToString() : "Not available") + "\n" +
            "Dominant hand: " + FieldText(result.dominantHand) + "\n\n" +
            "Exercise: " + FieldText(result.selectedExercise) + "\n" +
            "Difficulty: " + FieldText(result.selectedDifficulty) + "\n" +
            "Status: Session recorded (gameplay ended)\n\n" +
            "Score: " + (HasField(entry, "score") ? result.score.ToString() : "Not available") + "\n" +
            "Targets collected: " + (HasField(entry, "targetsCollected") ? result.targetsCollected.ToString() : "Not available") + "\n" +
            "Targets missed: " + (HasField(entry, "missedTargets") ? result.missedTargets.ToString() : "Not available") + "\n" +
            "Targets spawned: " + (HasField(entry, "targetsSpawned") ? result.targetsSpawned.ToString() : "Not available") + "\n" +
            "Total targets: " + (HasField(entry, "totalTargets") ? result.totalTargets.ToString() : "Not available") + "\n" +
            "Best streak: " + (HasField(entry, "bestStreak") ? result.bestStreak.ToString() : "Not available") + "\n" +
            "Duration: " + (HasField(entry, "sessionDurationSeconds") ? result.sessionDurationSeconds.ToString("0.0") + " s" : "Not available") + "\n" +
            "Hand samples: " + (HasField(entry, "playerHandSamples") && result.playerHandSamples != null ? result.playerHandSamples.Count.ToString() : "Not available") + "\n" +
            "Target events: " + (HasField(entry, "targetEvents") && result.targetEvents != null ? result.targetEvents.Count.ToString() : "Not available");
    }

    private static bool HasField(HistoryEntry entry, string fieldName)
    {
        return entry.fields.Contains(fieldName);
    }

    private static string FieldText(string value)
    {
        return !string.IsNullOrWhiteSpace(value)
            ? value
            : "Not available";
    }

    private static HashSet<string> ReadJsonFieldNames(string json)
    {
        HashSet<string> names = new HashSet<string>();
        MatchCollection matches = Regex.Matches(json, "\\\"([A-Za-z0-9_]+)\\\"\\s*:");
        foreach (Match match in matches)
        {
            names.Add(match.Groups[1].Value);
        }
        return names;
    }

    private void CreateScrollArea(string name, Transform parent, Vector2 anchorMin,
        Vector2 anchorMax, out Transform content)
    {
        GameObject viewport = new GameObject(name + " Viewport");
        viewport.transform.SetParent(parent, false);
        Image viewportImage = viewport.AddComponent<Image>();
        viewportImage.color = new Color(1f, 1f, 1f, 0.015f);
        RectTransform viewportRect = viewport.GetComponent<RectTransform>();
        SetRect(viewportRect, anchorMin, anchorMax);
        viewport.AddComponent<Mask>().showMaskGraphic = false;

        GameObject contentObject = new GameObject(name + " Content", typeof(RectTransform));
        contentObject.transform.SetParent(viewport.transform, false);
        RectTransform contentRect = contentObject.GetComponent<RectTransform>();
        contentRect.anchorMin = new Vector2(0f, 1f);
        contentRect.anchorMax = new Vector2(1f, 1f);
        contentRect.pivot = new Vector2(0.5f, 1f);
        contentRect.anchoredPosition = Vector2.zero;
        contentRect.sizeDelta = Vector2.zero;
        VerticalLayoutGroup layout = contentObject.AddComponent<VerticalLayoutGroup>();
        layout.spacing = 10f;
        layout.padding = new RectOffset(8, 8, 8, 8);
        layout.childControlWidth = true;
        layout.childControlHeight = true;
        layout.childForceExpandWidth = true;
        layout.childForceExpandHeight = false;
        ContentSizeFitter fitter = contentObject.AddComponent<ContentSizeFitter>();
        fitter.horizontalFit = ContentSizeFitter.FitMode.Unconstrained;
        fitter.verticalFit = ContentSizeFitter.FitMode.PreferredSize;

        ScrollRect scroll = viewport.AddComponent<ScrollRect>();
        scroll.viewport = viewportRect;
        scroll.content = contentRect;
        scroll.horizontal = false;
        scroll.vertical = true;
        content = contentObject.transform;
    }

    private static void ClearChildren(Transform parent)
    {
        for (int index = parent.childCount - 1; index >= 0; index--)
        {
            Destroy(parent.GetChild(index).gameObject);
        }
    }

    private void BuildPatientSetup()
    {
        patientPanel = CreateFullScreenPanel("Patient Setup Panel");

        GameObject card = CreatePanel(
            "Patient Card",
            patientPanel.transform,
            panelColor
        );

        SetRect(card.GetComponent<RectTransform>(), new Vector2(0.2f, 0.14f), new Vector2(0.8f, 0.88f));

        Text title = CreateText(
            "Patient Setup Title",
            card.transform,
            "Patient Setup",
            42,
            FontStyle.Bold,
            TextAnchor.MiddleCenter
        );

        title.color = accentColor;
        SetRect(title.rectTransform, new Vector2(0.08f, 0.82f), new Vector2(0.92f, 0.94f));

        CreateFieldLabel(card.transform, "Patient Name", new Vector2(0.14f, 0.68f), new Vector2(0.42f, 0.74f));
        patientNameInput = CreateInputField("Patient Name Input", card.transform, "Enter name");
        SetRect(patientNameInput.GetComponent<RectTransform>(), new Vector2(0.42f, 0.66f), new Vector2(0.86f, 0.75f));

        CreateFieldLabel(card.transform, "Age", new Vector2(0.14f, 0.54f), new Vector2(0.42f, 0.6f));
        ageInput = CreateInputField("Age Input", card.transform, "Enter age");
        ageInput.contentType = InputField.ContentType.IntegerNumber;
        SetRect(ageInput.GetComponent<RectTransform>(), new Vector2(0.42f, 0.52f), new Vector2(0.86f, 0.61f));

        CreateFieldLabel(card.transform, "Dominant Hand", new Vector2(0.14f, 0.39f), new Vector2(0.42f, 0.46f));

        rightHandButton = CreateButton("Right Hand Button", card.transform, "Right", secondaryAccentColor);
        SetRect(rightHandButton.GetComponent<RectTransform>(), new Vector2(0.42f, 0.38f), new Vector2(0.62f, 0.48f));
        rightHandButton.onClick.AddListener(() => SelectDominantHand("Right"));

        leftHandButton = CreateButton("Left Hand Button", card.transform, "Left", secondaryAccentColor);
        SetRect(leftHandButton.GetComponent<RectTransform>(), new Vector2(0.66f, 0.38f), new Vector2(0.86f, 0.48f));
        leftHandButton.onClick.AddListener(() => SelectDominantHand("Left"));

        validationText = CreateText(
            "Validation Message",
            card.transform,
            "",
            18,
            FontStyle.Bold,
            TextAnchor.MiddleCenter
        );

        validationText.color = warningColor;
        SetRect(validationText.rectTransform, new Vector2(0.12f, 0.26f), new Vector2(0.88f, 0.34f));

        Button backButton = CreateButton("Back Button", card.transform, "Back", secondaryAccentColor);
        SetRect(backButton.GetComponent<RectTransform>(), new Vector2(0.16f, 0.12f), new Vector2(0.38f, 0.22f));
        backButton.onClick.AddListener(ShowDashboard);

        Button continueButton = CreateButton("Continue Button", card.transform, "Continue", accentColor);
        SetRect(continueButton.GetComponent<RectTransform>(), new Vector2(0.62f, 0.12f), new Vector2(0.84f, 0.22f));
        continueButton.onClick.AddListener(ContinueFromPatientSetup);

        patientPanel.SetActive(false);
    }

    private void BuildExerciseSelection()
    {
        exercisePanel = CreateFullScreenPanel("Exercise Selection Panel");

        Text title = CreateText(
            "Exercise Selection Title",
            exercisePanel.transform,
            "Choose Your Exercise",
            44,
            FontStyle.Bold,
            TextAnchor.MiddleCenter
        );

        title.color = accentColor;
        SetRect(title.rectTransform, new Vector2(0.2f, 0.86f), new Vector2(0.8f, 0.96f));

        exercisePatientSummaryText = CreateText(
            "Patient Summary",
            exercisePanel.transform,
            "",
            18,
            FontStyle.Normal,
            TextAnchor.MiddleCenter
        );

        exercisePatientSummaryText.color = mutedTextColor;
        SetRect(exercisePatientSummaryText.rectTransform, new Vector2(0.22f, 0.8f), new Vector2(0.78f, 0.86f));

        BuildReachAndCollectCard();
        BuildPathFollowingCard();

        Button backButton = CreateButton("Exercise Back Button", exercisePanel.transform, "Back", secondaryAccentColor);
        SetRect(backButton.GetComponent<RectTransform>(), new Vector2(0.05f, 0.06f), new Vector2(0.18f, 0.14f));
        backButton.onClick.AddListener(ShowPatientSetup);

        exercisePanel.SetActive(false);
    }

    private void BuildReachAndCollectCard()
    {
        GameObject card = CreatePanel("Reach And Collect Card", exercisePanel.transform, cardColor);
        SetRect(card.GetComponent<RectTransform>(), new Vector2(0.1f, 0.2f), new Vector2(0.48f, 0.76f));

        Text title = CreateText("Reach Title", card.transform, "Reach & Collect", 32, FontStyle.Bold, TextAnchor.MiddleLeft);
        title.color = accentColor;
        SetRect(title.rectTransform, new Vector2(0.08f, 0.77f), new Vector2(0.92f, 0.9f));

        Text description = CreateText(
            "Reach Description",
            card.transform,
            "Reach toward targets using your hand movement.",
            20,
            FontStyle.Normal,
            TextAnchor.UpperLeft
        );

        description.color = mutedTextColor;
        SetRect(description.rectTransform, new Vector2(0.08f, 0.62f), new Vector2(0.92f, 0.75f));

        Text difficultyLabel = CreateText("Difficulty Label", card.transform, "Difficulty", 18, FontStyle.Bold, TextAnchor.MiddleLeft);
        SetRect(difficultyLabel.rectTransform, new Vector2(0.08f, 0.49f), new Vector2(0.4f, 0.56f));

        easyButton = CreateButton("Easy Button", card.transform, "Easy", accentColor);
        SetRect(easyButton.GetComponent<RectTransform>(), new Vector2(0.08f, 0.37f), new Vector2(0.32f, 0.47f));
        easyButton.onClick.AddListener(() => SelectDifficulty("Easy"));

        mediumButton = CreateButton("Medium Button", card.transform, "Medium", secondaryAccentColor);
        SetRect(mediumButton.GetComponent<RectTransform>(), new Vector2(0.38f, 0.37f), new Vector2(0.62f, 0.47f));
        mediumButton.onClick.AddListener(() => SelectDifficulty("Medium"));

        hardButton = CreateButton("Hard Button", card.transform, "Hard", secondaryAccentColor);
        SetRect(hardButton.GetComponent<RectTransform>(), new Vector2(0.68f, 0.37f), new Vector2(0.92f, 0.47f));
        hardButton.onClick.AddListener(() => SelectDifficulty("Hard"));

        selectedDifficultyText = CreateText(
            "Selected Difficulty",
            card.transform,
            "Selected difficulty: Easy",
            16,
            FontStyle.Normal,
            TextAnchor.MiddleLeft
        );

        selectedDifficultyText.color = mutedTextColor;
        SetRect(selectedDifficultyText.rectTransform, new Vector2(0.08f, 0.28f), new Vector2(0.92f, 0.35f));

        Button startButton = CreateButton("Start Exercise Button", card.transform, "Start Exercise", accentColor);
        SetRect(startButton.GetComponent<RectTransform>(), new Vector2(0.24f, 0.1f), new Vector2(0.76f, 0.22f));
        startButton.onClick.AddListener(StartReachAndCollect);

        SelectDifficulty("Easy");
    }

    private void BuildPathFollowingCard()
    {
        GameObject card = CreatePanel("Path Following Card", exercisePanel.transform, cardColor);
        SetRect(card.GetComponent<RectTransform>(), new Vector2(0.52f, 0.2f), new Vector2(0.9f, 0.76f));

        Text title = CreateText("Path Title", card.transform, "Path Following", 32, FontStyle.Bold, TextAnchor.MiddleLeft);
        title.color = new Color(0.62f, 0.78f, 1f);
        SetRect(title.rectTransform, new Vector2(0.08f, 0.77f), new Vector2(0.92f, 0.9f));

        Text description = CreateText(
            "Path Description",
            card.transform,
            "Follow a guided path using controlled hand movement.",
            20,
            FontStyle.Normal,
            TextAnchor.UpperLeft
        );

        description.color = mutedTextColor;
        SetRect(description.rectTransform, new Vector2(0.08f, 0.58f), new Vector2(0.92f, 0.75f));

        Text comingSoon = CreateText("Coming Soon", card.transform, "COMING SOON", 24, FontStyle.Bold, TextAnchor.MiddleCenter);
        comingSoon.color = new Color(1f, 0.82f, 0.34f);
        SetRect(comingSoon.rectTransform, new Vector2(0.2f, 0.37f), new Vector2(0.8f, 0.5f));

        Button disabledButton = CreateButton("Path Disabled Button", card.transform, "Start Exercise", secondaryAccentColor);
        SetRect(disabledButton.GetComponent<RectTransform>(), new Vector2(0.24f, 0.1f), new Vector2(0.76f, 0.22f));
        disabledButton.interactable = false;
    }

    private Canvas CreateCanvas()
    {
        GameObject canvasObject = new GameObject("RehabQuestMenuCanvas");
        Canvas createdCanvas = canvasObject.AddComponent<Canvas>();
        createdCanvas.renderMode = RenderMode.ScreenSpaceOverlay;

        CanvasScaler scaler = canvasObject.AddComponent<CanvasScaler>();
        scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
        scaler.referenceResolution = new Vector2(1920, 1080);

        canvasObject.AddComponent<GraphicRaycaster>();
        ConfigureEventSystem();

        return createdCanvas;
    }

    private void ConfigureEventSystem()
    {
        EventSystem eventSystem = FindFirstObjectByType<EventSystem>();

        if (eventSystem == null)
        {
            GameObject eventSystemObject = new GameObject("EventSystem");
            eventSystem = eventSystemObject.AddComponent<EventSystem>();
        }

        StandaloneInputModule legacyModule = eventSystem.GetComponent<StandaloneInputModule>();

        if (legacyModule != null)
        {
            Destroy(legacyModule);
        }

        InputSystemUIInputModule inputSystemModule =
            eventSystem.GetComponent<InputSystemUIInputModule>();

        if (inputSystemModule == null)
        {
            inputSystemModule =
                eventSystem.gameObject.AddComponent<InputSystemUIInputModule>();
        }

        inputSystemModule.AssignDefaultActions();
    }

    private GameObject CreateFullScreenPanel(string name)
    {
        GameObject panel = CreatePanel(name, canvas.transform, Color.clear);
        SetRect(panel.GetComponent<RectTransform>(), Vector2.zero, Vector2.one);
        return panel;
    }

    private GameObject CreatePanel(string name, Transform parent, Color color)
    {
        GameObject panel = new GameObject(name);
        panel.transform.SetParent(parent, false);

        Image image = panel.AddComponent<Image>();
        image.color = color;

        return panel;
    }

    private void CreateFieldLabel(Transform parent, string text, Vector2 anchorMin, Vector2 anchorMax)
    {
        Text label = CreateText(text + " Label", parent, text, 19, FontStyle.Bold, TextAnchor.MiddleLeft);
        label.color = Color.white;
        SetRect(label.rectTransform, anchorMin, anchorMax);
    }

    private InputField CreateInputField(string name, Transform parent, string placeholder)
    {
        GameObject inputObject = CreatePanel(name, parent, new Color(0.94f, 0.98f, 1f, 0.94f));
        InputField inputField = inputObject.AddComponent<InputField>();

        Text text = CreateText("Text", inputObject.transform, "", 20, FontStyle.Normal, TextAnchor.MiddleLeft);
        text.color = new Color(0.05f, 0.08f, 0.11f);
        SetRect(text.rectTransform, new Vector2(0.04f, 0.08f), new Vector2(0.96f, 0.92f));

        Text placeholderText = CreateText("Placeholder", inputObject.transform, placeholder, 20, FontStyle.Italic, TextAnchor.MiddleLeft);
        placeholderText.color = new Color(0.35f, 0.42f, 0.48f, 0.78f);
        SetRect(placeholderText.rectTransform, new Vector2(0.04f, 0.08f), new Vector2(0.96f, 0.92f));

        inputField.textComponent = text;
        inputField.placeholder = placeholderText;
        inputField.targetGraphic = inputObject.GetComponent<Image>();

        return inputField;
    }

    private Text CreateText(
        string name,
        Transform parent,
        string text,
        int fontSize,
        FontStyle style,
        TextAnchor anchor)
    {
        GameObject textObject = new GameObject(name);
        textObject.transform.SetParent(parent, false);

        Text label = textObject.AddComponent<Text>();
        label.text = text;
        label.font = GetDefaultFont();
        label.fontSize = fontSize;
        label.fontStyle = style;
        label.alignment = anchor;
        label.color = Color.white;
        label.horizontalOverflow = HorizontalWrapMode.Wrap;
        label.verticalOverflow = VerticalWrapMode.Truncate;

        return label;
    }

    private Button CreateButton(string name, Transform parent, string label, Color color)
    {
        GameObject buttonObject = CreatePanel(name, parent, color);
        Button button = buttonObject.AddComponent<Button>();
        button.targetGraphic = buttonObject.GetComponent<Image>();

        ColorBlock colors = button.colors;
        colors.normalColor = color;
        colors.highlightedColor = Color.Lerp(color, Color.white, 0.18f);
        colors.pressedColor = Color.Lerp(color, Color.black, 0.18f);
        colors.selectedColor = colors.highlightedColor;
        colors.disabledColor = new Color(0.25f, 0.3f, 0.36f, 0.7f);
        button.colors = colors;

        Text buttonText = CreateText("Label", buttonObject.transform, label, 22, FontStyle.Bold, TextAnchor.MiddleCenter);
        SetRect(buttonText.rectTransform, Vector2.zero, Vector2.one);

        return button;
    }

    private void SetButtonSelected(Button button, bool selected)
    {
        if (button == null)
        {
            return;
        }

        Image image = button.GetComponent<Image>();

        if (image != null)
        {
            image.color = selected ? accentColor : secondaryAccentColor;
        }
    }

    private void SetRect(RectTransform rectTransform, Vector2 anchorMin, Vector2 anchorMax)
    {
        rectTransform.anchorMin = anchorMin;
        rectTransform.anchorMax = anchorMax;
        rectTransform.offsetMin = Vector2.zero;
        rectTransform.offsetMax = Vector2.zero;
    }

    private Font GetDefaultFont()
    {
        Font font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");

        if (font == null)
        {
            font = Resources.GetBuiltinResource<Font>("Arial.ttf");
        }

        return font;
    }
}

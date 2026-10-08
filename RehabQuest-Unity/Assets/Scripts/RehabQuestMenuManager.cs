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
        PatientSetup,
        ExerciseSelection
    }

    private const string MenuSceneName = "SampleScene";
    private const string ReachAndCollectSceneName = "ReachAndCollect";
    private const string ExerciseReachAndCollect = "Reach & Collect";

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
        BuildPatientSetup();
        BuildExerciseSelection();
    }

    private void ShowDashboard()
    {
        ShowScreen(MenuScreen.Dashboard);
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

        SetRect(startButton.GetComponent<RectTransform>(), new Vector2(0.28f, 0.34f), new Vector2(0.72f, 0.45f));
        startButton.onClick.AddListener(ShowPatientSetup);

        Button historyButton = CreateButton(
            "Session History Button",
            heroCard.transform,
            "Session History",
            secondaryAccentColor
        );

        SetRect(historyButton.GetComponent<RectTransform>(), new Vector2(0.22f, 0.2f), new Vector2(0.47f, 0.3f));
        historyButton.interactable = false;

        Button settingsButton = CreateButton(
            "Settings Button",
            heroCard.transform,
            "Settings",
            secondaryAccentColor
        );

        SetRect(settingsButton.GetComponent<RectTransform>(), new Vector2(0.53f, 0.2f), new Vector2(0.78f, 0.3f));
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
        SetRect(statusText.rectTransform, new Vector2(0.18f, 0.08f), new Vector2(0.82f, 0.16f));
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

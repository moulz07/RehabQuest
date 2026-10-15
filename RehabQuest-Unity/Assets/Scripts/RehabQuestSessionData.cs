public static class RehabQuestSessionData
{
    public static string PatientName { get; private set; } = "";
    public static int PatientAge { get; private set; }
    public static string DominantHand { get; private set; } = "";
    public static string SelectedExercise { get; private set; } = "";
    public static string SelectedDifficulty { get; private set; } = "";
    public static bool IsTestSession { get; private set; }
    public static RehabQuestSessionResult LatestReachAndCollectResult { get; private set; }

    public static bool HasPatientDetails =>
        !string.IsNullOrWhiteSpace(PatientName) &&
        PatientAge > 0 &&
        !string.IsNullOrWhiteSpace(DominantHand);

    public static string GetMissingSetupFields()
    {
        System.Collections.Generic.List<string> missingFields =
            new System.Collections.Generic.List<string>();

        if (string.IsNullOrWhiteSpace(PatientName)) missingFields.Add("patient name");
        if (PatientAge <= 0) missingFields.Add("patient age");
        if (string.IsNullOrWhiteSpace(DominantHand)) missingFields.Add("dominant hand");
        if (string.IsNullOrWhiteSpace(SelectedExercise)) missingFields.Add("exercise selection");
        if (string.IsNullOrWhiteSpace(SelectedDifficulty)) missingFields.Add("difficulty selection");

        return string.Join(", ", missingFields);
    }

    public static void SetPatientDetails(
        string patientName,
        int patientAge,
        string dominantHand)
    {
        PatientName = patientName.Trim();
        PatientAge = patientAge;
        DominantHand = dominantHand;
        IsTestSession = false;
    }

    public static void SetTestSession(bool isTestSession)
    {
        IsTestSession = isTestSession;
    }

    public static void SetExerciseSelection(
        string selectedExercise,
        string selectedDifficulty)
    {
        SelectedExercise = selectedExercise;
        SelectedDifficulty = selectedDifficulty;
    }

    public static void SetLatestReachAndCollectResult(
        RehabQuestSessionResult sessionResult)
    {
        LatestReachAndCollectResult = sessionResult;
    }
}

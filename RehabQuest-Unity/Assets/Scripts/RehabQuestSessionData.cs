public static class RehabQuestSessionData
{
    public static string PatientName { get; private set; } = "";
    public static int PatientAge { get; private set; }
    public static string DominantHand { get; private set; } = "";
    public static string SelectedExercise { get; private set; } = "";
    public static string SelectedDifficulty { get; private set; } = "Easy";

    public static bool HasPatientDetails =>
        !string.IsNullOrWhiteSpace(PatientName) &&
        PatientAge > 0 &&
        !string.IsNullOrWhiteSpace(DominantHand);

    public static void SetPatientDetails(
        string patientName,
        int patientAge,
        string dominantHand)
    {
        PatientName = patientName.Trim();
        PatientAge = patientAge;
        DominantHand = dominantHand;
    }

    public static void SetExerciseSelection(
        string selectedExercise,
        string selectedDifficulty)
    {
        SelectedExercise = selectedExercise;
        SelectedDifficulty = selectedDifficulty;
    }
}

using System;
using System.IO;
using UnityEngine;

public static class RehabQuestSessionJsonExporter
{
    private const string SessionFolderName = "RehabQuestSessions";
    private const string FilePrefix = "reach_and_collect_session_";

    public static bool TryExportReachAndCollectSession(
        RehabQuestSessionResult sessionResult,
        out string savedPath)
    {
        savedPath = "";

        if (sessionResult == null)
        {
            Debug.LogWarning(
                "Reach & Collect session JSON export skipped: session data is missing."
            );

            return false;
        }

        try
        {
            if (string.IsNullOrWhiteSpace(Application.persistentDataPath))
            {
                Debug.LogWarning(
                    "Reach & Collect session JSON export failed: persistent data path is unavailable."
                );

                return false;
            }

            string directory =
                Path.Combine(
                    Application.persistentDataPath,
                    SessionFolderName
                );

            Directory.CreateDirectory(directory);

            string timestamp =
                DateTime.UtcNow.ToString("yyyyMMdd_HHmmss_fff");

            savedPath =
                Path.Combine(
                    directory,
                    FilePrefix + timestamp + ".json"
                );

            sessionResult.exportedJsonPath = savedPath;

            string json =
                JsonUtility.ToJson(
                    sessionResult,
                    true
                );

            File.WriteAllText(
                savedPath,
                json
            );

            return true;
        }
        catch (Exception exception)
        {
            Debug.LogWarning(
                "Reach & Collect session JSON export failed: " +
                exception.Message
            );

            savedPath = "";
            return false;
        }
    }
}

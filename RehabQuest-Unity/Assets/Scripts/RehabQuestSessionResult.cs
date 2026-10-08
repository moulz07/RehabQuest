using System;
using System.Collections.Generic;
using UnityEngine;

[Serializable]
public class RehabQuestSessionResult
{
    public string schemaVersion = "1.0";
    public string patientName;
    public int patientAge;
    public string dominantHand;
    public string selectedExercise;
    public string selectedDifficulty;
    public string gameName;
    public string sessionStartTimeUtc;
    public string exportedJsonPath;
    public float sessionDurationSeconds;

    public int totalTargets;
    public int targetsSpawned;
    public int targetsCollected;
    public int missedTargets;
    public int score;
    public int bestStreak;

    public List<ReachTargetResult> targetEvents =
        new List<ReachTargetResult>();

    public List<PlayerHandSample> playerHandSamples =
        new List<PlayerHandSample>();
}

[Serializable]
public class ReachTargetResult
{
    public int targetNumber;
    public float spawnTimeSeconds;
    public float targetLifetimeSeconds;
    public float targetDiameter;
    public SerializableVector3 spawnPosition;

    public bool collected;
    public bool missed;
    public float completionTimeSeconds;
    public float timeToCompleteSeconds;
    public SerializableVector3 collectionPosition;
}

[Serializable]
public class PlayerHandSample
{
    public float timeSeconds;
    public SerializableVector3 position;
}

[Serializable]
public struct SerializableVector3
{
    public float x;
    public float y;
    public float z;

    public SerializableVector3(Vector3 vector)
    {
        x = vector.x;
        y = vector.y;
        z = vector.z;
    }
}

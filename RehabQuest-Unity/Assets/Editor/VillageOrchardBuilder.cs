using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine.SceneManagement;

public class VillageOrchardBuilder : Editor
{
    private const string ScenePath = "Assets/Scenes/ReachAndCollect.unity";
    private const string RootName = "Environment_VillageOrchard";

    // Material Paths
    private const string GrassMatPath = "Assets/Polytope Studio/Lowpoly_Environments/Sources/Materials/PT_Grass_Mat.mat";
    private const string VillageMatPath = "Assets/Polytope Studio/Lowpoly_Village/Sources/Materials/PT_mat.mat";
    private const string RocksMatPath = "Assets/Polytope Studio/Lowpoly_Environments/Sources/Materials/PT_Rocks_mat.mat";
    private const string SkyboxMatPath = "Assets/Polytope Studio/Lowpoly_Environments/Sources/Materials/PT_Skybox_mat.mat";
    private const string MeadowGrassMatPath = "Assets/Materials/M_Orchard_MeadowGrass.mat";
    private const string GardenPathMatPath = "Assets/Materials/M_Orchard_GardenPath.mat";
    private const string TargetMatPath = "Assets/Materials/M_Orchard_Target.mat";
    private const string HandMatPath = "Assets/Materials/M_Orchard_Hand.mat";

    // Texture Paths
    private const string VillageTexturePath = "Assets/Polytope Studio/Lowpoly_Village/Sources/Textures/PT_texture.tga";
    private const string GrassGroundTexPath = "Assets/Polytope Studio/Lowpoly_Environments/Sources/Textures/PT_Ground_Grass_Green_01.png";
    private const string DirtPathTexPath = "Assets/Polytope Studio/Lowpoly_Environments/Sources/Textures/PT_Ground_Generic_03.png";
    private const string FruitLeavesTexPath = "Assets/Polytope Studio/Lowpoly_Environments/Sources/Textures/PT_Fruit_Tree_Leaves_01.png";
    private const string TreeTrunkTexPath = "Assets/Polytope Studio/Lowpoly_Environments/Sources/Textures/PT_Tree_Trunk_01.png";
    private const string GenericLeavesTexPath = "Assets/Polytope Studio/Lowpoly_Environments/Sources/Textures/PT_Generic_Tree_Leaves_01.png";
    private const string ShrubLeavesTexPath = "Assets/Polytope Studio/Lowpoly_Environments/Sources/Textures/PT_Generic_Leaves_01.png";
    private const string RocksTexPath = "Assets/Polytope Studio/Lowpoly_Environments/Sources/Textures/PT_Rocks_01.png";
    private const string PineLeavesTexPath = "Assets/Polytope Studio/Lowpoly_Environments/Sources/Textures/PT_Pine_Tree_01.png";
    private const string PoppyTexPath = "Assets/Polytope Studio/Lowpoly_Environments/Sources/Textures/PT_Poppy_01.png";
    private const string MushroomTexPath = "Assets/Polytope Studio/Lowpoly_Environments/Sources/Textures/PT_Mushrooms_01.png";

    // Prefab paths
    private const string TreeApplePath = "Assets/Polytope Studio/Lowpoly_Environments/Prefabs/Trees/PT_Fruit_Tree_01_apples.prefab";
    private const string TreePearPath = "Assets/Polytope Studio/Lowpoly_Environments/Prefabs/Trees/PT_Fruit_Tree_01_pears.prefab";
    private const string TreePlumPath = "Assets/Polytope Studio/Lowpoly_Environments/Prefabs/Trees/PT_Fruit_Tree_01_plums.prefab";
    private const string TreeGreenPath = "Assets/Polytope Studio/Lowpoly_Environments/Prefabs/Trees/PT_Fruit_Tree_01_green.prefab";
    private const string TreeLogsPath = "Assets/Polytope Studio/Lowpoly_Environments/Prefabs/Trees/PT_Fruit_Tree_01_logs.prefab";
    private const string TreeStumpPath = "Assets/Polytope Studio/Lowpoly_Environments/Prefabs/Trees/PT_Fruit_Tree_01_stump.prefab";
    private const string TreePinePath = "Assets/Polytope Studio/Lowpoly_Environments/Prefabs/Trees/PT_Pine_Tree_03_green.prefab";

    private const string BridgePath = "Assets/Polytope Studio/Lowpoly_Village/Prefabs/Modular/Bridge/PT_Wooden_Bridge_02.prefab";
    private const string Fence1Path = "Assets/Polytope Studio/Lowpoly_Village/Prefabs/Modular/Fence/PT_Modular_Fence_Wood_01.prefab";
    private const string Fence2Path = "Assets/Polytope Studio/Lowpoly_Village/Prefabs/Modular/Fence/PT_Modular_Fence_Wood_02.prefab";
    private const string Fence3Path = "Assets/Polytope Studio/Lowpoly_Village/Prefabs/Modular/Fence/PT_Modular_Fence_Wood_03.prefab";
    private const string GatePath = "Assets/Polytope Studio/Lowpoly_Village/Prefabs/Modular/Fence/PT_Modular_Gate_Wood_01.prefab";

    private const string PoppyPath = "Assets/Polytope Studio/Lowpoly_Environments/Prefabs/Flowers/PT_Poppy_02.prefab";
    private const string GrassPath = "Assets/Polytope Studio/Lowpoly_Environments/Prefabs/Plants/PT_Grass_02.prefab";
    private const string MushroomPath = "Assets/Polytope Studio/Lowpoly_Environments/Prefabs/Mushrooms/PT_Caesars_Mushroom_01.prefab";
    private const string ShrubPath = "Assets/Polytope Studio/Lowpoly_Environments/Prefabs/Shrubs/PT_Generic_Shrub_01_green.prefab";

    private const string RockGenericPath = "Assets/Polytope Studio/Lowpoly_Environments/Prefabs/Rocks/PT_Generic_Rock_01.prefab";
    private const string RockRiverPath = "Assets/Polytope Studio/Lowpoly_Environments/Prefabs/Rocks/PT_River_Rock_Pile_02.prefab";
    private const string RockMenhirPath = "Assets/Polytope Studio/Lowpoly_Environments/Prefabs/Rocks/PT_Menhir_Rock_02.prefab";

    [MenuItem("RehabQuest/Build Village Orchard Environment")]
    public static void BuildEnvironment()
    {
        EnsureSceneOpen();

        // 1. Fix Materials & Shaders (Converts white Built-in/Amplify shaders to native URP Lit, maps textures, removes snow)
        FixProjectMaterialsAndShaders();

        // 2. Clear previous generated environment
        ClearEnvironment();

        GameObject root = new GameObject(RootName);
        Undo.RegisterCreatedObjectUndo(root, "Build Village Orchard");

        // 3. Setup Expansive Meadow Ground & Winding Cobblestone/Dirt Garden Path
        SetupGroundFloor(root.transform);

        // 4. Setup Lighting, Skybox, and Atmospheric Fog
        SetupLighting();

        // 5. Optimize Camera Vantage Point for Motor Rehabilitation
        SetupCamera();

        // 6. Setup Golden Harvest Apple Target & Electric Cyan Hand Visuals and Shadows
        SetupHandAndTargetVisuals(root.transform);

        // 7. Build Framing Groves, Fence Boundary, and Background Vista
        BuildFenceBoundary(root.transform);
        BuildFruitTreeGroves(root.transform);
        BuildBackgroundVista(root.transform);
        BuildGroundFoliage(root.transform);

        // 8. Living Atmosphere (Warm sun motes / drifting blossom pollen particles)
        BuildAtmosphericParticles(root.transform);

        // 9. Disable decorative scenery colliders for clinical gameplay safety
        DisablePropColliders(root);

        // 10. Update Game Manager serialized parameters
        UpdateGameManagerSettings();

        // Save Scene
        Scene activeScene = SceneManager.GetActiveScene();
        EditorSceneManager.MarkSceneDirty(activeScene);
        EditorSceneManager.SaveScene(activeScene);

        // 11. Automatically capture game-view screenshot to current_status.png
        CaptureScreenshot();

        Debug.Log("<b>[RehabQuest]</b> Village Orchard Environment completely overhauled, verified, and saved successfully!");
    }

    [MenuItem("RehabQuest/Clear Village Orchard Environment")]
    public static void ClearEnvironment()
    {
        EnsureSceneOpen();

        GameObject existingRoot = GameObject.Find(RootName);
        if (existingRoot != null)
        {
            Undo.DestroyObjectImmediate(existingRoot);
        }

        string[] cleanNames = new string[] {
            "PT_Fruit_Tree",
            "PT_Grass_02",
            "PT_Generic_Rock",
            "PT_Menhir_Rock",
            "PT_Ore_Rock",
            "PlayerHand_GroundShadow",
            "Target_GroundShadow",
            "OrchardAtmosphere",
            "Garden_Path"
        };

        foreach (GameObject go in SceneManager.GetActiveScene().GetRootGameObjects())
        {
            if (go.name == RootName || go.name == "PlayerHand" || go.name == "ReachAndCollectGameManager" ||
                go.name == "UnityPythonClient" || go.name == "Main Camera" || go.name == "Directional Light" ||
                go.name == "Target" || go.name == "Global Volume" || go.name == "GameFloor")
            {
                continue;
            }

            foreach (string prefix in cleanNames)
            {
                if (go.name.StartsWith(prefix))
                {
                    Undo.DestroyObjectImmediate(go);
                    break;
                }
            }
        }
    }

    public static void BuildEnvironmentFromCommandLine()
    {
        Debug.Log("[RehabQuest CLI] Starting Village Orchard overhaul build...");
        BuildEnvironment();
        Debug.Log("[RehabQuest CLI] Village Orchard overhaul build complete.");
    }

    private static void EnsureSceneOpen()
    {
        Scene activeScene = SceneManager.GetActiveScene();
        if (activeScene.path != ScenePath)
        {
            EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
        }
    }

    private static void FixProjectMaterialsAndShaders()
    {
        Shader urpLit = Shader.Find("Universal Render Pipeline/Lit");
        if (urpLit == null)
        {
            Debug.LogWarning("[RehabQuest] URP Lit shader not found!");
            return;
        }

        // Ensure Materials directory exists
        if (!AssetDatabase.IsValidFolder("Assets/Materials"))
        {
            AssetDatabase.CreateFolder("Assets", "Materials");
        }

        // 1. Village Fences / Gates / Bridge Wood
        FixMaterial(VillageMatPath, urpLit, VillageTexturePath, Color.white, 0.15f, Vector2.one);

        // 2. Fruit Tree Foliage (Apples, Pears, Plums with colorful fruit and lush green leaves)
        FixMaterial("Assets/Polytope Studio/Lowpoly_Environments/Sources/Materials/PT_Fruit_Tree_Foliage_Mat.mat",
            urpLit, FruitLeavesTexPath, Color.white, 0.10f, Vector2.one);

        // 3. Fruit Tree Trunk & Firewood Logs & Stumps (Warm wood grain)
        FixMaterial("Assets/Polytope Studio/Lowpoly_Environments/Sources/Materials/PT_Fruit_Tree_Opaque_mat.mat",
            urpLit, TreeTrunkTexPath, Color.white, 0.15f, Vector2.one);

        // 4. Generic Tree Foliage (Lush green canopy)
        FixMaterial("Assets/Polytope Studio/Lowpoly_Environments/Sources/Materials/PT_Generic_Tree_Leaves_mat.mat",
            urpLit, GenericLeavesTexPath, Color.white, 0.10f, Vector2.one);

        // 5. Generic Tree Trunk
        FixMaterial("Assets/Polytope Studio/Lowpoly_Environments/Sources/Materials/PT_Generic_Tree_Trunk_mat.mat",
            urpLit, TreeTrunkTexPath, Color.white, 0.15f, Vector2.one);

        // 6. Shrubs & Bushes
        FixMaterial("Assets/Polytope Studio/Lowpoly_Environments/Sources/Materials/PT_Generic_Leaf_mat.mat",
            urpLit, ShrubLeavesTexPath, Color.white, 0.10f, Vector2.one);

        // 7. Rocks (Mossy slate / natural warm earthy stone instead of white chalk)
        FixMaterial(RocksMatPath,
            urpLit, RocksTexPath, new Color(0.70f, 0.74f, 0.68f, 1f), 0.10f, Vector2.one);

        // 8. Pine Tree Leaves
        FixMaterial("Assets/Polytope Studio/Lowpoly_Environments/Sources/Materials/PT_Pine_Tree_Leaves_Mat.mat",
            urpLit, PineLeavesTexPath, Color.white, 0.10f, Vector2.one);

        // 9. Pine Tree Trunk
        FixMaterial("Assets/Polytope Studio/Lowpoly_Environments/Sources/Materials/PT_Pine_Tree_Trunk_Mat.mat",
            urpLit, TreeTrunkTexPath, Color.white, 0.15f, Vector2.one);

        // 10. Poppies
        FixMaterial("Assets/Polytope Studio/Lowpoly_Environments/Sources/Materials/PT_Poppy_mat.mat",
            urpLit, PoppyTexPath, Color.white, 0.10f, Vector2.one);

        // 11. Mushrooms
        FixMaterial("Assets/Polytope Studio/Lowpoly_Environments/Sources/Materials/PT_Mushrooms_mat.mat",
            urpLit, MushroomTexPath, Color.white, 0.15f, Vector2.one);

        // 12. Unified Meadow Grass Ground Material
        FixMaterial(MeadowGrassMatPath,
            urpLit, GrassGroundTexPath, new Color(0.92f, 1.04f, 0.92f, 1f), 0.05f, new Vector2(28f, 28f));

        // 13. Winding Garden Path Material (Earthy dirt / cobblestone texture)
        FixMaterial(GardenPathMatPath,
            urpLit, DirtPathTexPath, new Color(0.94f, 0.88f, 0.78f, 1f), 0.06f, new Vector2(2f, 14f));

        AssetDatabase.SaveAssets();
    }

    private static void FixMaterial(string matPath, Shader shader, string texturePath, Color tint, float smoothness, Vector2 tiling)
    {
        Material mat = AssetDatabase.LoadAssetAtPath<Material>(matPath);
        if (mat == null)
        {
            mat = new Material(shader);
            AssetDatabase.CreateAsset(mat, matPath);
        }
        else
        {
            mat.shader = shader;
        }

        if (!string.IsNullOrEmpty(texturePath))
        {
            Texture tex = AssetDatabase.LoadAssetAtPath<Texture>(texturePath);
            if (tex != null)
            {
                mat.SetTexture("_BaseMap", tex);
                if (mat.HasProperty("_MainTex"))
                {
                    mat.SetTexture("_MainTex", tex);
                }
            }
        }

        mat.SetTextureScale("_BaseMap", tiling);
        mat.SetColor("_BaseColor", tint);
        mat.SetFloat("_Smoothness", smoothness);
        mat.SetFloat("_Metallic", 0f);

        // Disable snow / legacy tinting
        mat.DisableKeyword("_SNOWONOFF_ON");
        if (mat.HasProperty("_SNOWONOFF")) mat.SetFloat("_SNOWONOFF", 0f);
        if (mat.HasProperty("_SnowAmount")) mat.SetFloat("_SnowAmount", 0f);
        if (mat.HasProperty("_SnowNoiseOnOff")) mat.SetFloat("_SnowNoiseOnOff", 0f);

        EditorUtility.SetDirty(mat);
    }

    private static void SetupGroundFloor(Transform parent)
    {
        // 1. Unified continuous meadow
        GameObject floor = GameObject.Find("GameFloor");
        if (floor != null)
        {
            floor.transform.position = new Vector3(0f, -0.05f, 18f);
            floor.transform.localScale = new Vector3(120f, 0.1f, 120f);

            Material meadowMat = AssetDatabase.LoadAssetAtPath<Material>(MeadowGrassMatPath);
            if (meadowMat != null)
            {
                Renderer r = floor.GetComponent<Renderer>();
                if (r != null)
                {
                    r.sharedMaterial = meadowMat;
                }
            }
        }

        // 2. Procedural winding garden path curving through the wooden gate
        BuildGardenPath(parent);
    }

    private static void BuildGardenPath(Transform parent)
    {
        GameObject pathGo = new GameObject("Garden_Path");
        pathGo.transform.SetParent(parent);
        pathGo.transform.localPosition = Vector3.zero;

        MeshFilter mf = pathGo.AddComponent<MeshFilter>();
        MeshRenderer mr = pathGo.AddComponent<MeshRenderer>();

        Material pathMat = AssetDatabase.LoadAssetAtPath<Material>(GardenPathMatPath);
        if (pathMat != null)
        {
            mr.sharedMaterial = pathMat;
        }

        // Smooth spline waypoints entering from lower-right foreground (matching Asset Store reference),
        // sweeping gently through the open wooden gate at Z=3.2f, and under the rustic wooden bridge at Z=9.8f.
        Vector3[] waypoints = new Vector3[] {
            new Vector3(1.40f, 0.025f, -3.2f),
            new Vector3(0.95f, 0.025f, -1.8f),
            new Vector3(0.45f, 0.025f, -0.2f),
            new Vector3(0.12f, 0.025f, 1.4f),
            new Vector3(0.00f, 0.025f, 3.2f),  // passes right through open gate
            new Vector3(0.35f, 0.025f, 5.5f),
            new Vector3(0.80f, 0.025f, 7.6f),
            new Vector3(1.20f, 0.025f, 9.8f),  // passes directly under wooden footbridge
            new Vector3(1.45f, 0.025f, 13.0f),
            new Vector3(1.10f, 0.025f, 17.5f)
        };

        List<Vector3> curvePoints = SubdivideSpline(waypoints, 7);
        float baseWidth = 2.1f;

        List<Vector3> vertices = new List<Vector3>();
        List<Vector2> uvs = new List<Vector2>();
        List<int> triangles = new List<int>();

        for (int i = 0; i < curvePoints.Count; i++)
        {
            Vector3 forward = (i < curvePoints.Count - 1)
                ? (curvePoints[i + 1] - curvePoints[i]).normalized
                : (curvePoints[i] - curvePoints[i - 1]).normalized;

            Vector3 right = Vector3.Cross(Vector3.up, forward).normalized;
            // Soft organic width variation
            float width = baseWidth * (1f + 0.10f * Mathf.Sin(i * 0.35f));

            vertices.Add(curvePoints[i] - right * (width * 0.5f));
            vertices.Add(curvePoints[i] + right * (width * 0.5f));

            float v = i * 0.20f;
            uvs.Add(new Vector2(0f, v));
            uvs.Add(new Vector2(1f, v));

            if (i > 0)
            {
                int baseIdx = (i - 1) * 2;
                // Upward facing winding (Counter-Clockwise in Y-up)
                triangles.Add(baseIdx);
                triangles.Add(baseIdx + 2);
                triangles.Add(baseIdx + 1);

                triangles.Add(baseIdx + 1);
                triangles.Add(baseIdx + 2);
                triangles.Add(baseIdx + 3);
            }
        }

        Mesh mesh = new Mesh();
        mesh.name = "GardenPath_Mesh";
        mesh.SetVertices(vertices);
        mesh.SetUVs(0, uvs);
        mesh.SetTriangles(triangles, 0);
        mesh.RecalculateNormals();
        mesh.RecalculateBounds();

        mf.sharedMesh = mesh;
    }

    private static List<Vector3> SubdivideSpline(Vector3[] waypoints, int segmentsPerPoint)
    {
        List<Vector3> pts = new List<Vector3>();
        for (int i = 0; i < waypoints.Length - 1; i++)
        {
            Vector3 p0 = i > 0 ? waypoints[i - 1] : waypoints[i];
            Vector3 p1 = waypoints[i];
            Vector3 p2 = waypoints[i + 1];
            Vector3 p3 = (i + 2 < waypoints.Length) ? waypoints[i + 2] : p2;

            for (int s = 0; s < segmentsPerPoint; s++)
            {
                float t = (float)s / segmentsPerPoint;
                pts.Add(CatmullRom(p0, p1, p2, p3, t));
            }
        }
        pts.Add(waypoints[waypoints.Length - 1]);
        return pts;
    }

    private static Vector3 CatmullRom(Vector3 p0, Vector3 p1, Vector3 p2, Vector3 p3, float t)
    {
        return 0.5f * (
            (2f * p1) +
            (-p0 + p2) * t +
            (2f * p0 - 5f * p1 + 4f * p2 - p3) * (t * t) +
            (-p0 + 3f * p1 - 3f * p2 + p3) * (t * t * t)
        );
    }

    private static void SetupLighting()
    {
        // 1. Assign Vibrant Countryside Blue Skybox with Fluffy White Clouds
        Material skyMat = AssetDatabase.LoadAssetAtPath<Material>(SkyboxMatPath);
        if (skyMat != null)
        {
            RenderSettings.skybox = skyMat;
        }

        // 2. Atmospheric Horizon Fog
        RenderSettings.fog = true;
        RenderSettings.fogMode = FogMode.Linear;
        RenderSettings.fogColor = new Color(0.70f, 0.88f, 0.98f, 1f); // Cheerful sky blue haze
        RenderSettings.fogStartDistance = 24f;
        RenderSettings.fogEndDistance = 90f;
        RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Skybox;
        RenderSettings.ambientIntensity = 1.20f;

        // 3. Directional Sun Light
        GameObject lightGo = GameObject.Find("Directional Light");
        if (lightGo != null)
        {
            Light light = lightGo.GetComponent<Light>();
            if (light != null)
            {
                lightGo.transform.rotation = Quaternion.Euler(32f, -32f, 0f);
                light.color = new Color(1.0f, 0.97f, 0.90f); // Warm natural afternoon sun
                light.intensity = 1.30f;
                light.shadows = LightShadows.Soft;
                light.shadowStrength = 0.60f;
            }
        }
    }

    private static void SetupCamera()
    {
        GameObject camGo = GameObject.Find("Main Camera");
        if (camGo != null)
        {
            // Ideal therapeutic vantage point:
            // Camera elevated to Y=1.65m, tilted downward at 11.5 deg, at Z=-3.80m.
            // This gives a balanced, picturesque composition where:
            // 1. The 0.85m golden harvest apple and 0.55m cyan hand are hero elements with clear ground presence.
            // 2. The winding path flows cleanly across the ground through the open gate.
            // 3. The lush apple and pear trees frame the top-left and top-right naturally.
            // 4. The wooden footbridge and rolling pine hills are clearly visible in the vista.
            camGo.transform.position = new Vector3(0f, 1.65f, -3.80f);
            camGo.transform.rotation = Quaternion.Euler(11.5f, 0f, 0f);

            Camera cam = camGo.GetComponent<Camera>();
            if (cam != null)
            {
                cam.fieldOfView = 53f;
                cam.clearFlags = CameraClearFlags.Skybox;
                cam.nearClipPlane = 0.1f;
                cam.farClipPlane = 300f;
            }
        }
    }

    private static void SetupHandAndTargetVisuals(Transform parent)
    {
        Shader urpLit = Shader.Find("Universal Render Pipeline/Lit");
        if (urpLit == null) return;

        // 1. Radiant Golden Harvest Apple Target Material
        Material targetMat = AssetDatabase.LoadAssetAtPath<Material>(TargetMatPath);
        if (targetMat == null)
        {
            targetMat = new Material(urpLit);
            AssetDatabase.CreateAsset(targetMat, TargetMatPath);
        }
        targetMat.shader = urpLit;
        Color goldenAmber = new Color(1.0f, 0.75f, 0.10f, 1f);
        targetMat.SetColor("_BaseColor", goldenAmber);
        targetMat.EnableKeyword("_EMISSION");
        targetMat.SetColor("_EmissionColor", goldenAmber * 2.2f);
        targetMat.SetFloat("_Smoothness", 0.85f);
        EditorUtility.SetDirty(targetMat);

        // 2. High-Contrast Electric Aquamarine Hand Material
        Material handMat = AssetDatabase.LoadAssetAtPath<Material>(HandMatPath);
        if (handMat == null)
        {
            handMat = new Material(urpLit);
            AssetDatabase.CreateAsset(handMat, HandMatPath);
        }
        handMat.shader = urpLit;
        Color electricCyan = new Color(0.12f, 0.92f, 1.0f, 1f);
        handMat.SetColor("_BaseColor", electricCyan);
        handMat.EnableKeyword("_EMISSION");
        handMat.SetColor("_EmissionColor", electricCyan * 1.8f);
        handMat.SetFloat("_Smoothness", 0.90f);
        EditorUtility.SetDirty(handMat);

        AssetDatabase.SaveAssets();

        // 3. Configure Target Game Object (Hero scale + Apple Stem & Leaf crown)
        GameObject target = GameObject.Find("Target");
        if (target != null)
        {
            Renderer r = target.GetComponent<Renderer>();
            if (r != null) r.sharedMaterial = targetMat;

            // Positioned at reaching zone right side in default view
            target.transform.localScale = Vector3.one * 0.85f;
            target.transform.position = new Vector3(0.55f, 1.15f, 0.0f);

            // Add or refresh stylized Apple Stem & Leaf
            Transform stemTrans = target.transform.Find("Apple_Stem");
            GameObject stemGo = stemTrans != null ? stemTrans.gameObject : null;
            if (stemGo == null)
            {
                stemGo = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                stemGo.name = "Apple_Stem";
                DestroyImmediate(stemGo.GetComponent<Collider>());
                stemGo.transform.SetParent(target.transform);
                stemGo.transform.localPosition = new Vector3(0f, 0.48f, 0f);
                stemGo.transform.localRotation = Quaternion.Euler(15f, 0f, -10f);
                stemGo.transform.localScale = new Vector3(0.08f, 0.15f, 0.08f);

                Material woodMat = AssetDatabase.LoadAssetAtPath<Material>("Assets/Polytope Studio/Lowpoly_Environments/Sources/Materials/PT_Fruit_Tree_Opaque_mat.mat");
                if (woodMat != null) stemGo.GetComponent<Renderer>().sharedMaterial = woodMat;

                GameObject leafGo = GameObject.CreatePrimitive(PrimitiveType.Sphere);
                leafGo.name = "Apple_Leaf";
                DestroyImmediate(leafGo.GetComponent<Collider>());
                leafGo.transform.SetParent(stemGo.transform);
                leafGo.transform.localPosition = new Vector3(0.45f, 0.6f, 0f);
                leafGo.transform.localRotation = Quaternion.Euler(0f, 0f, -40f);
                leafGo.transform.localScale = new Vector3(1.2f, 0.25f, 0.6f);

                Material leafMat = AssetDatabase.LoadAssetAtPath<Material>("Assets/Polytope Studio/Lowpoly_Environments/Sources/Materials/PT_Fruit_Tree_Foliage_Mat.mat");
                if (leafMat != null) leafGo.GetComponent<Renderer>().sharedMaterial = leafMat;
            }

            // Ground shadow disc for Target
            CreateGroundShadow("Target_GroundShadow", target.transform, 0.60f, new Color(0.04f, 0.08f, 0.04f, 0.45f), parent);
        }

        // 4. Configure PlayerHand Game Object (Hero scale + clear visibility)
        GameObject hand = GameObject.Find("PlayerHand");
        if (hand != null)
        {
            Renderer r = hand.GetComponent<Renderer>();
            if (r != null) r.sharedMaterial = handMat;

            // Positioned at reaching zone left side in default view
            hand.transform.localScale = Vector3.one * 0.55f;
            hand.transform.position = new Vector3(-0.65f, 0.95f, 0.0f);

            // Ground shadow disc for Hand
            CreateGroundShadow("PlayerHand_GroundShadow", hand.transform, 0.50f, new Color(0.04f, 0.08f, 0.04f, 0.45f), parent);
        }
    }

    private static void CreateGroundShadow(string name, Transform tracked, float radius, Color color, Transform parent)
    {
        GameObject shadowGo = GameObject.CreatePrimitive(PrimitiveType.Quad);
        shadowGo.name = name;
        DestroyImmediate(shadowGo.GetComponent<Collider>());
        shadowGo.transform.SetParent(parent);
        shadowGo.transform.rotation = Quaternion.Euler(90f, 0f, 0f);

        GroundShadowFollower follower = shadowGo.AddComponent<GroundShadowFollower>();
        follower.Setup(tracked, radius, color);
    }

    private static void BuildFenceBoundary(Transform parent)
    {
        GameObject fenceGroup = new GameObject("Fences_And_Gates");
        fenceGroup.transform.SetParent(parent);

        // Back boundary fence at Z = 3.2f (Framing the garden vista, path passes right through open gate)
        GameObject gate = SpawnProp(GatePath, new Vector3(0f, 0f, 3.2f), Quaternion.Euler(0f, 0f, 0f), Vector3.one, fenceGroup.transform);
        if (gate != null)
        {
            // Swing the wooden gate doors open toward the garden so the path flows freely!
            Transform leftDoor = gate.transform.Find("PT_Modular_Gate_Wood_01_left");
            if (leftDoor != null)
            {
                leftDoor.localRotation = Quaternion.Euler(0f, -80f, 0f);
            }
            Transform rightDoor = gate.transform.Find("PT_Modular_Gate_Wood_01_right");
            if (rightDoor != null)
            {
                rightDoor.localRotation = Quaternion.Euler(0f, 80f, 0f);
            }
        }

        SpawnProp(Fence1Path, new Vector3(-2.6f, 0f, 3.2f), Quaternion.Euler(0f, 0f, 0f), Vector3.one, fenceGroup.transform);
        SpawnProp(Fence2Path, new Vector3(-5.2f, 0f, 3.2f), Quaternion.Euler(0f, 0f, 0f), Vector3.one, fenceGroup.transform);
        SpawnProp(Fence1Path, new Vector3(2.6f, 0f, 3.2f), Quaternion.Euler(0f, 0f, 0f), Vector3.one, fenceGroup.transform);
        SpawnProp(Fence2Path, new Vector3(5.2f, 0f, 3.2f), Quaternion.Euler(0f, 0f, 0f), Vector3.one, fenceGroup.transform);

        // Left & right flank fencing
        SpawnProp(Fence3Path, new Vector3(-5.2f, 0f, 1.0f), Quaternion.Euler(0f, 90f, 0f), Vector3.one, fenceGroup.transform);
        SpawnProp(Fence1Path, new Vector3(-5.2f, 0f, -1.2f), Quaternion.Euler(0f, 90f, 0f), Vector3.one, fenceGroup.transform);
        SpawnProp(Fence3Path, new Vector3(5.2f, 0f, 1.0f), Quaternion.Euler(0f, -90f, 0f), Vector3.one, fenceGroup.transform);
        SpawnProp(Fence1Path, new Vector3(5.2f, 0f, -1.2f), Quaternion.Euler(0f, -90f, 0f), Vector3.one, fenceGroup.transform);
    }

    private static void BuildFruitTreeGroves(Transform parent)
    {
        GameObject treesGroup = new GameObject("Fruit_Orchard_Trees");
        treesGroup.transform.SetParent(parent);

        // --- LEFT ORCHARD GROVE (Framing upper-left corner with lush green canopy & bright red apples) ---
        SpawnSwayingProp(TreeApplePath, new Vector3(-3.5f, 0f, 1.2f), Quaternion.Euler(0f, 38f, 0f), new Vector3(1.30f, 1.30f, 1.30f), treesGroup.transform, 1.3f, 1.1f);
        SpawnSwayingProp(TreeGreenPath, new Vector3(-5.4f, 0f, 4.2f), Quaternion.Euler(0f, 85f, 0f), new Vector3(1.20f, 1.20f, 1.20f), treesGroup.transform, 1.2f, 0.9f);
        SpawnSwayingProp(TreePlumPath, new Vector3(-7.2f, 0f, 7.2f), Quaternion.Euler(0f, 120f, 0f), new Vector3(1.25f, 1.25f, 1.25f), treesGroup.transform, 1.3f, 1.0f);

        SpawnProp(TreeStumpPath, new Vector3(-2.8f, 0f, -0.3f), Quaternion.Euler(0f, 25f, 0f), Vector3.one, treesGroup.transform);
        SpawnProp(TreeLogsPath, new Vector3(-3.3f, 0f, -0.7f), Quaternion.Euler(0f, 55f, 0f), Vector3.one, treesGroup.transform);

        // --- RIGHT ORCHARD GROVE (Framing upper-right corner with flowering canopy & golden pears) ---
        SpawnSwayingProp(TreePearPath, new Vector3(3.5f, 0f, 1.2f), Quaternion.Euler(0f, -42f, 0f), new Vector3(1.30f, 1.30f, 1.30f), treesGroup.transform, 1.3f, 1.1f);
        SpawnSwayingProp(TreeApplePath, new Vector3(5.4f, 0f, 4.2f), Quaternion.Euler(0f, -95f, 0f), new Vector3(1.20f, 1.20f, 1.20f), treesGroup.transform, 1.2f, 0.9f);
        SpawnSwayingProp(TreePlumPath, new Vector3(7.2f, 0f, 7.2f), Quaternion.Euler(0f, -125f, 0f), new Vector3(1.25f, 1.25f, 1.25f), treesGroup.transform, 1.3f, 1.0f);

        SpawnProp(TreeStumpPath, new Vector3(2.8f, 0f, -0.3f), Quaternion.Euler(0f, -30f, 0f), Vector3.one, treesGroup.transform);
        SpawnProp(TreeLogsPath, new Vector3(3.3f, 0f, -0.7f), Quaternion.Euler(0f, -60f, 0f), Vector3.one, treesGroup.transform);
    }

    private static void BuildBackgroundVista(Transform parent)
    {
        GameObject vistaGroup = new GameObject("Background_Vista");
        vistaGroup.transform.SetParent(parent);

        // Rustic wooden footbridge placed along the winding garden path
        SpawnProp(BridgePath, new Vector3(1.20f, 0f, 9.8f), Quaternion.Euler(0f, 20f, 0f), new Vector3(1.15f, 1.15f, 1.15f), vistaGroup.transform);

        // Natural mossy slate rock formations along the trail
        SpawnProp(RockMenhirPath, new Vector3(-4.5f, 0f, 8.5f), Quaternion.Euler(0f, 45f, 0f), new Vector3(1.15f, 1.15f, 1.15f), vistaGroup.transform);
        SpawnProp(RockRiverPath, new Vector3(3.2f, 0f, 7.8f), Quaternion.Euler(0f, -25f, 0f), new Vector3(1.10f, 1.10f, 1.10f), vistaGroup.transform);
        SpawnProp(RockGenericPath, new Vector3(-1.8f, 0f, 6.2f), Quaternion.Euler(0f, 65f, 0f), new Vector3(1.0f, 1.0f, 1.0f), vistaGroup.transform);

        // Dense layered pine forest along the rolling horizon
        Vector3[] pinePositions = new Vector3[] {
            new Vector3(-12.0f, 0f, 14.0f),
            new Vector3(-8.5f, 0f, 15.0f),
            new Vector3(-4.5f, 0f, 18.0f),
            new Vector3(0.0f, 0f, 22.0f),
            new Vector3(4.5f, 0f, 19.0f),
            new Vector3(9.0f, 0f, 15.0f),
            new Vector3(12.5f, 0f, 14.0f),
            // Back row
            new Vector3(-15.0f, 0f, 24.0f),
            new Vector3(-10.0f, 0f, 26.0f),
            new Vector3(-5.0f, 0f, 28.0f),
            new Vector3(5.0f, 0f, 27.0f),
            new Vector3(10.0f, 0f, 25.0f),
            new Vector3(15.0f, 0f, 23.0f)
        };

        for (int i = 0; i < pinePositions.Length; i++)
        {
            float rotY = (i * 67f) % 360f;
            float scale = 1.35f + (i % 3) * 0.25f;
            SpawnSwayingProp(TreePinePath, pinePositions[i], Quaternion.Euler(0f, rotY, 0f), Vector3.one * scale, vistaGroup.transform, 1.0f, 0.8f);
        }
    }

    private static void BuildGroundFoliage(Transform parent)
    {
        GameObject foliageGroup = new GameObject("Ground_Foliage");
        foliageGroup.transform.SetParent(parent);

        // Red poppies along the fence line and garden path
        Vector3[] poppyPositions = new Vector3[] {
            new Vector3(1.20f, 0f, -1.2f),
            new Vector3(0.35f, 0f, 0.2f),
            new Vector3(-1.10f, 0f, 1.2f),
            new Vector3(1.60f, 0f, 1.8f),
            new Vector3(-1.40f, 0f, 2.8f),
            new Vector3(1.50f, 0f, 2.8f),
            new Vector3(-2.80f, 0f, 3.1f),
            new Vector3(2.80f, 0f, 3.1f),
            new Vector3(-1.20f, 0f, 3.1f),
            new Vector3(1.20f, 0f, 3.1f),
            new Vector3(-3.20f, 0f, 1.2f),
            new Vector3(3.20f, 0f, 1.2f),
            new Vector3(-0.40f, 0f, 4.5f),
            new Vector3(0.90f, 0f, 5.0f),
            new Vector3(2.20f, 0f, 8.5f),
            new Vector3(-0.20f, 0f, 8.8f)
        };

        for (int i = 0; i < poppyPositions.Length; i++)
        {
            float rotY = (i * 47f) % 360f;
            float scale = 0.95f + (i % 3) * 0.1f;
            SpawnSwayingProp(PoppyPath, poppyPositions[i], Quaternion.Euler(0f, rotY, 0f), Vector3.one * scale, foliageGroup.transform, 3.5f, 1.6f);
        }

        // Wild mushrooms near tree roots and stumps
        Vector3[] mushroomPositions = new Vector3[] {
            new Vector3(-2.4f, 0f, -0.2f),
            new Vector3(2.4f, 0f, -0.2f),
            new Vector3(-3.3f, 0f, 0.7f),
            new Vector3(3.3f, 0f, 0.7f),
            new Vector3(-4.8f, 0f, 3.8f),
            new Vector3(4.8f, 0f, 3.8f)
        };

        for (int i = 0; i < mushroomPositions.Length; i++)
        {
            float rotY = (i * 73f) % 360f;
            SpawnProp(MushroomPath, mushroomPositions[i], Quaternion.Euler(0f, rotY, 0f), Vector3.one * 1.15f, foliageGroup.transform);
        }

        // Lush green shrubs lining the fences and corners
        SpawnProp(ShrubPath, new Vector3(-4.8f, 0f, 3.0f), Quaternion.Euler(0f, 30f, 0f), Vector3.one * 1.2f, foliageGroup.transform);
        SpawnProp(ShrubPath, new Vector3(4.8f, 0f, 3.0f), Quaternion.Euler(0f, -40f, 0f), Vector3.one * 1.2f, foliageGroup.transform);
        SpawnProp(ShrubPath, new Vector3(-5.0f, 0f, 0.2f), Quaternion.Euler(0f, 90f, 0f), Vector3.one * 1.1f, foliageGroup.transform);
        SpawnProp(ShrubPath, new Vector3(5.0f, 0f, 0.2f), Quaternion.Euler(0f, -90f, 0f), Vector3.one * 1.1f, foliageGroup.transform);

        // Grass tufts along path borders
        Vector3[] grassPositions = new Vector3[] {
            new Vector3(1.7f, 0f, -2.4f),
            new Vector3(0.5f, 0f, -1.5f),
            new Vector3(-1.8f, 0f, 3.1f),
            new Vector3(1.8f, 0f, 3.1f),
            new Vector3(-2.8f, 0f, 1.8f),
            new Vector3(2.8f, 0f, 1.8f),
            new Vector3(-0.8f, 0f, 1.2f),
            new Vector3(1.3f, 0f, 1.4f)
        };

        for (int i = 0; i < grassPositions.Length; i++)
        {
            float rotY = (i * 61f) % 360f;
            SpawnSwayingProp(GrassPath, grassPositions[i], Quaternion.Euler(0f, rotY, 0f), Vector3.one * 1.2f, foliageGroup.transform, 3.0f, 1.5f);
        }
    }

    private static void BuildAtmosphericParticles(Transform parent)
    {
        GameObject atmGo = new GameObject("OrchardAtmosphere");
        atmGo.transform.SetParent(parent);
        atmGo.transform.position = new Vector3(0f, 2.5f, 1.0f);

        ParticleSystem ps = atmGo.AddComponent<ParticleSystem>();
        ParticleSystem.MainModule main = ps.main;
        main.startLifetime = 8f;
        main.startSpeed = 0.22f;
        main.startSize = 0.08f;
        main.startColor = new Color(1.0f, 0.94f, 0.70f, 0.65f); // Warm sun pollen motes
        main.maxParticles = 65;
        main.simulationSpace = ParticleSystemSimulationSpace.World;

        ParticleSystem.EmissionModule emission = ps.emission;
        emission.rateOverTime = 7f;

        ParticleSystem.ShapeModule shape = ps.shape;
        shape.shapeType = ParticleSystemShapeType.Box;
        shape.scale = new Vector3(8f, 3.2f, 6f);

        ParticleSystem.VelocityOverLifetimeModule vel = ps.velocityOverLifetime;
        vel.enabled = true;
        vel.x = new ParticleSystem.MinMaxCurve(-0.1f, 0.2f);
        vel.y = new ParticleSystem.MinMaxCurve(-0.12f, -0.04f);
        vel.z = new ParticleSystem.MinMaxCurve(-0.12f, 0.08f);

        ParticleSystem.ColorOverLifetimeModule col = ps.colorOverLifetime;
        col.enabled = true;
        Gradient grad = new Gradient();
        grad.SetKeys(
            new GradientColorKey[] { new GradientColorKey(new Color(1f, 0.96f, 0.75f), 0f), new GradientColorKey(new Color(1f, 0.88f, 0.55f), 1f) },
            new GradientAlphaKey[] { new GradientAlphaKey(0f, 0f), new GradientAlphaKey(0.75f, 0.3f), new GradientAlphaKey(0.75f, 0.7f), new GradientAlphaKey(0f, 1f) }
        );
        col.color = grad;

        ParticleSystemRenderer rend = atmGo.GetComponent<ParticleSystemRenderer>();
        if (rend != null)
        {
            Shader unlit = Shader.Find("Universal Render Pipeline/Particles/Unlit");
            if (unlit == null) unlit = Shader.Find("Particles/Standard Unlit");
            if (unlit != null)
            {
                Material pMat = new Material(unlit);
                rend.sharedMaterial = pMat;
            }
        }
    }

    private static void UpdateGameManagerSettings()
    {
        ReachAndCollectGameManager mgr = FindFirstObjectByType<ReachAndCollectGameManager>();
        if (mgr != null)
        {
            SerializedObject so = new SerializedObject(mgr);
            SerializedProperty dProp = so.FindProperty("targetDiameter");
            if (dProp != null) dProp.floatValue = 0.85f;
            SerializedProperty minDProp = so.FindProperty("minimumTargetDiameter");
            if (minDProp != null) minDProp.floatValue = 0.70f;
            SerializedProperty colorProp = so.FindProperty("targetColor");
            if (colorProp != null) colorProp.colorValue = new Color(1.0f, 0.75f, 0.10f, 1f);
            so.ApplyModifiedProperties();
            EditorUtility.SetDirty(mgr);
        }
    }

    [MenuItem("RehabQuest/Capture Orchard Screenshot")]
    public static void CaptureScreenshot()
    {
        EnsureSceneOpen();
        GameObject camGo = GameObject.Find("Main Camera");
        if (camGo == null) return;
        Camera cam = camGo.GetComponent<Camera>();
        if (cam == null) return;

        int width = 1920;
        int height = 1080;
        RenderTexture rt = new RenderTexture(width, height, 24);
        cam.targetTexture = rt;
        Texture2D screenShot = new Texture2D(width, height, TextureFormat.RGB24, false);
        cam.Render();
        RenderTexture.active = rt;
        screenShot.ReadPixels(new Rect(0, 0, width, height), 0, 0);
        screenShot.Apply();
        cam.targetTexture = null;
        RenderTexture.active = null;
        DestroyImmediate(rt);

        byte[] bytes = screenShot.EncodeToPNG();
        string shotPath = "C:/Sindhu_2025/RehabQuest/current_status.png";
        System.IO.File.WriteAllBytes(shotPath, bytes);
        Debug.Log("<b>[RehabQuest]</b> Captured camera screenshot saved to: " + shotPath);
    }

    private static GameObject SpawnProp(string assetPath, Vector3 localPos, Quaternion localRot, Vector3 localScale, Transform parent)
    {
        GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(assetPath);
        if (prefab == null) return null;

        GameObject instance = PrefabUtility.InstantiatePrefab(prefab, parent) as GameObject;
        if (instance != null)
        {
            instance.transform.localPosition = localPos;
            instance.transform.localRotation = localRot;
            instance.transform.localScale = localScale;
        }

        return instance;
    }

    private static GameObject SpawnSwayingProp(string assetPath, Vector3 localPos, Quaternion localRot, Vector3 localScale, Transform parent, float swayAmount, float swaySpeed)
    {
        GameObject go = SpawnProp(assetPath, localPos, localRot, localScale, parent);
        if (go != null)
        {
            GentleWindSway sway = go.AddComponent<GentleWindSway>();
            sway.Configure(swayAmount, swaySpeed);
        }
        return go;
    }

    private static void DisablePropColliders(GameObject root)
    {
        Collider[] colliders = root.GetComponentsInChildren<Collider>(true);
        foreach (Collider col in colliders)
        {
            col.enabled = false;
        }
    }
}

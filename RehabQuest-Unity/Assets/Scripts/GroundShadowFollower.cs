using UnityEngine;

/// <summary>
/// Projects a soft ground shadow onto the orchard meadow directly beneath
/// the PlayerHand or Target, grounding floating objects in 3D space.
/// </summary>
public class GroundShadowFollower : MonoBehaviour
{
    [SerializeField] private Transform trackedObject;
    [SerializeField] private float shadowRadius = 0.5f;
    [SerializeField] private float groundY = 0.02f;

    private MeshRenderer meshRenderer;
    private static Material shadowMaterial;

    public void Setup(Transform target, float radius, Color shadowColor)
    {
        trackedObject = target;
        shadowRadius = radius;
        transform.localScale = new Vector3(radius * 2f, 1f, radius * 2f);

        CreateOrAssignMaterial(shadowColor);
    }

    private void Awake()
    {
        meshRenderer = GetComponent<MeshRenderer>();
    }

    private void LateUpdate()
    {
        if (trackedObject == null)
        {
            if (gameObject.activeSelf) gameObject.SetActive(false);
            return;
        }

        bool shouldBeVisible = trackedObject.gameObject.activeInHierarchy;
        if (meshRenderer != null && meshRenderer.enabled != shouldBeVisible)
        {
            meshRenderer.enabled = shouldBeVisible;
        }

        if (shouldBeVisible)
        {
            transform.position = new Vector3(
                trackedObject.position.x,
                groundY,
                trackedObject.position.z
            );
        }
    }

    private void CreateOrAssignMaterial(Color shadowColor)
    {
        Renderer rend = GetComponent<Renderer>();
        if (rend == null) return;

        if (shadowMaterial == null)
        {
            Shader unlit = Shader.Find("Universal Render Pipeline/Unlit");
            if (unlit == null) unlit = Shader.Find("Unlit/Transparent");

            shadowMaterial = new Material(unlit);
            shadowMaterial.SetFloat("_Surface", 1); // Transparent in URP
            shadowMaterial.SetFloat("_Blend", 0);   // Alpha blend
            shadowMaterial.SetInt("_SrcBlend", (int)UnityEngine.Rendering.BlendMode.SrcAlpha);
            shadowMaterial.SetInt("_DstBlend", (int)UnityEngine.Rendering.BlendMode.OneMinusSrcAlpha);
            shadowMaterial.SetInt("_ZWrite", 0);
            shadowMaterial.renderQueue = 3000;

            Texture2D tex = CreateSoftDiscTexture();
            shadowMaterial.mainTexture = tex;
        }

        Material instMat = new Material(shadowMaterial);
        instMat.color = shadowColor;
        if (instMat.HasProperty("_BaseColor"))
        {
            instMat.SetColor("_BaseColor", shadowColor);
        }
        rend.material = instMat;
    }

    private static Texture2D CreateSoftDiscTexture()
    {
        int res = 64;
        Texture2D tex = new Texture2D(res, res, TextureFormat.RGBA32, false);
        Vector2 center = new Vector2(res / 2f, res / 2f);
        float maxRadius = res / 2f;

        for (int y = 0; y < res; y++)
        {
            for (int x = 0; x < res; x++)
            {
                float dist = Vector2.Distance(new Vector2(x, y), center);
                float norm = Mathf.Clamp01(dist / maxRadius);
                // Smooth falloff
                float alpha = Mathf.SmoothStep(1f, 0f, norm);
                alpha = Mathf.Pow(alpha, 1.5f);
                tex.SetPixel(x, y, new Color(0f, 0f, 0f, alpha));
            }
        }

        tex.Apply();
        return tex;
    }
}

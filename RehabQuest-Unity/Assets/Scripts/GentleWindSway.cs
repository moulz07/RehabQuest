using UnityEngine;

/// <summary>
/// Adds organic, natural wind sway to trees, foliage, and flowers.
/// Phase offsets prevent synchronized unnatural movement.
/// </summary>
public class GentleWindSway : MonoBehaviour
{
    [SerializeField] private float swayAmount = 1.8f;
    [SerializeField] private float swaySpeed = 1.2f;
    [SerializeField] private Vector3 swayAxis = new Vector3(1f, 0.2f, 0.5f);

    private Quaternion initialRotation;
    private float phaseOffset;

    private void Start()
    {
        initialRotation = transform.localRotation;
        // Deterministic pseudo-random phase based on world position
        phaseOffset = (transform.position.x * 1.73f + transform.position.z * 2.41f) % (Mathf.PI * 2f);
    }

    public void Configure(float amount, float speed)
    {
        swayAmount = amount;
        swaySpeed = speed;
    }

    private void Update()
    {
        float t = Time.time * swaySpeed + phaseOffset;
        float wave = Mathf.Sin(t) * 0.7f + Mathf.Sin(t * 1.8f) * 0.3f;
        float currentAngle = wave * swayAmount;

        transform.localRotation = initialRotation * Quaternion.Euler(swayAxis.normalized * currentAngle);
    }
}

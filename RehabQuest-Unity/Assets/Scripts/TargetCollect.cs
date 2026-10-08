using UnityEngine;

public class TargetCollect : MonoBehaviour
{
    private void OnTriggerEnter(Collider other)
    {
        if (other.gameObject.name == "PlayerHand")
        {
            gameObject.SetActive(false);
        }
    }
}
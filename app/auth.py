
"""
Authentication for RehabQuest
-----------------------------
Local offline authentication supporting pre-configured profiles
and explicit patient registration.

Note:
This prototype does not verify passwords. Do not use it as
production-grade authentication for real patient records.
"""

from pathlib import Path
import sys
from typing import Dict, Any


APP_DIR = Path(__file__).resolve().parent

if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from local_data import get_user, register_user


class AuthError(Exception):
    """Authentication error with a machine-readable reason."""

    def __init__(self, reason: str, message: str = ""):
        super().__init__(message or reason)
        self.reason = reason


def _clean_user_id(user_id: str) -> str:
    """Validate and normalize a user ID."""
    if not user_id or not user_id.strip():
        raise AuthError(
            "empty_user_id",
            "Please enter a Patient or User ID.",
        )

    return user_id.strip().upper()


def login(
    user_id: str,
    password: str = "",
) -> Dict[str, Any]:
    """
    Sign in using an existing local profile.

    The password argument is retained for compatibility with
    the current UI, but is not verified by this prototype.
    """
    clean_id = _clean_user_id(user_id)

    user = get_user(clean_id)

    if not user:
        raise AuthError(
            "user_not_found",
            "No profile was found for this ID. "
            "Please check the ID or register a profile.",
        )

    return user


def register(
    user_id: str,
    name: str,
    password: str = "",
) -> Dict[str, Any]:
    """
    Register a local profile.

    The password argument is retained for compatibility,
    but is not stored or verified by this prototype.
    """
    clean_id = _clean_user_id(user_id)

    clean_name = name.strip() if name else ""

    if not clean_name:
        raise AuthError(
            "empty_name",
            "Please enter your name.",
        )

    if get_user(clean_id):
        raise AuthError(
            "user_exists",
            "This Patient ID already exists. "
            "Please sign in using that ID.",
        )

    try:
        return register_user(clean_id, clean_name)
    except Exception as exc:
        raise AuthError(
            "registration_failed",
            f"Could not register this profile: {exc}",
        ) from exc

"""
Authentication for RehabQuest
-----------------------------
Local offline authentication supporting pre-configured profiles or on-the-fly
patient registration.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from typing import Optional, Dict, Any
from local_data import get_users, register_user, get_user



class AuthError(Exception):
    def __init__(self, reason: str, message: str = ""):
        super().__init__(message or reason)
        self.reason = reason


def login(user_id: str, password: str = "") -> Dict[str, Any]:
    if not user_id or not user_id.strip():
        raise AuthError("empty_user_id", "Please enter a Patient or User ID.")
    
    clean_id = user_id.strip().upper()
    user = get_user(clean_id)
    if not user:
        # For seamless demo experience: auto-register if not found
        user = register_user(clean_id, clean_id.title())
        
    return user


def register(user_id: str, name: str, password: str = "") -> Dict[str, Any]:
    if not user_id or not user_id.strip():
        raise AuthError("empty_user_id", "Please enter a Patient ID.")
    
    clean_id = user_id.strip().upper()
    clean_name = name.strip() if name else clean_id.title()
    return register_user(clean_id, clean_name)

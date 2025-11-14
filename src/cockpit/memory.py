"""
In-memory repository implementations.

Useful for local testing and FastAPI dependency injection without
requiring a backing database.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Dict, List, Optional

from src.cockpit.storage import AuthRepository, UserRepository
from src.models import AuthProfile, User


class InMemoryUserRepository(UserRepository):
    """Simple in-memory user storage."""

    def __init__(self) -> None:
        self._users: Dict[str, User] = {}

    def save_user(self, user: User) -> None:
        self._users[user.id] = deepcopy(user)

    def get_user(self, user_id: str) -> Optional[User]:
        user = self._users.get(user_id)
        return deepcopy(user) if user else None

    def get_user_by_username(self, username: str) -> Optional[User]:
        for user in self._users.values():
            if user.username == username:
                return deepcopy(user)
        return None

    def get_user_by_email(self, email: str) -> Optional[User]:
        for user in self._users.values():
            if user.email == email:
                return deepcopy(user)
        return None

    def list_users(self) -> List[User]:
        return [deepcopy(user) for user in self._users.values()]

    def delete_user(self, user_id: str) -> None:
        self._users.pop(user_id, None)


class InMemoryAuthRepository(AuthRepository):
    """In-memory auth profile storage."""

    def __init__(self) -> None:
        self._profiles_by_id: Dict[str, AuthProfile] = {}
        self._profiles_by_username: Dict[str, str] = {}
        self._profiles_by_email: Dict[str, str] = {}
        self._profiles_by_user_id: Dict[str, str] = {}

    def save_profile(self, profile: AuthProfile) -> None:
        self._profiles_by_id[profile.id] = deepcopy(profile)
        self._profiles_by_username[profile.username] = profile.id
        self._profiles_by_email[profile.email] = profile.id
        self._profiles_by_user_id[profile.user_id] = profile.id

    def _get(self, profile_id: str) -> Optional[AuthProfile]:
        profile = self._profiles_by_id.get(profile_id)
        return deepcopy(profile) if profile else None

    def get_by_username(self, username: str) -> Optional[AuthProfile]:
        profile_id = self._profiles_by_username.get(username)
        return self._get(profile_id) if profile_id else None

    def get_by_email(self, email: str) -> Optional[AuthProfile]:
        profile_id = self._profiles_by_email.get(email)
        return self._get(profile_id) if profile_id else None

    def get_by_user_id(self, user_id: str) -> Optional[AuthProfile]:
        profile_id = self._profiles_by_user_id.get(user_id)
        return self._get(profile_id) if profile_id else None

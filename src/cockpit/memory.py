"""
In-memory repository implementations.

Useful for local testing and FastAPI dependency injection without
requiring a backing database.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Dict, List, Optional

from src.cockpit.storage import AuthRepository, ProjectRepository, UserRepository
from src.models import AuthProfile, Project, User


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


class InMemoryProjectRepository(ProjectRepository):
    """Simple in-memory project storage."""

    def __init__(self) -> None:
        self._projects: Dict[str, Project] = {}

    def save_project(self, project: Project) -> None:
        """Save or update a project."""
        self._projects[project.id] = deepcopy(project)

    def get_project(self, project_id: str) -> Optional[Project]:
        """Retrieve a project by ID."""
        project = self._projects.get(project_id)
        return deepcopy(project) if project else None

    def list_projects(
        self,
        user_id: Optional[str] = None,
        is_public: Optional[bool] = None,
        mission_type: Optional[str] = None,
    ) -> List[Project]:
        """List projects with optional filtering."""
        results = []
        for project in self._projects.values():
            if user_id is not None and project.user_id != user_id:
                continue
            if is_public is not None and project.is_public != is_public:
                continue
            if mission_type is not None and project.mission_type != mission_type:
                continue
            results.append(deepcopy(project))
        return results

    def delete_project(self, project_id: str) -> None:
        """Delete a project by ID."""
        self._projects.pop(project_id, None)

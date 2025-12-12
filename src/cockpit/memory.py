"""
In-memory repository implementations.

Useful for local testing and FastAPI dependency injection without
requiring a backing database.
"""

from __future__ import annotations

from copy import deepcopy

from src.cockpit.storage import (
    AuthRepository,
    MissionRepository,
    ObjectMetadataRepository,
    ProjectRepository,
    UserRepository,
)
from src.models import AuthProfile, Mission, Project, User


class InMemoryUserRepository(UserRepository):
    """Simple in-memory user storage."""

    def __init__(self) -> None:
        self._users: dict[str, User] = {}

    def save_user(self, user: User) -> None:
        self._users[user.id] = deepcopy(user)

    def get_user(self, user_id: str) -> User | None:
        user = self._users.get(user_id)
        return deepcopy(user) if user else None

    def get_user_by_username(self, username: str) -> User | None:
        for user in self._users.values():
            if user.username == username:
                return deepcopy(user)
        return None

    def get_user_by_email(self, email: str) -> User | None:
        for user in self._users.values():
            if user.email == email:
                return deepcopy(user)
        return None

    def list_users(self) -> list[User]:
        return [deepcopy(user) for user in self._users.values()]

    def delete_user(self, user_id: str) -> None:
        self._users.pop(user_id, None)


class InMemoryAuthRepository(AuthRepository):
    """In-memory auth profile storage."""

    def __init__(self) -> None:
        self._profiles_by_id: dict[str, AuthProfile] = {}
        self._profiles_by_username: dict[str, str] = {}
        self._profiles_by_email: dict[str, str] = {}
        self._profiles_by_user_id: dict[str, str] = {}

    def save_profile(self, profile: AuthProfile) -> None:
        self._profiles_by_id[profile.id] = deepcopy(profile)
        self._profiles_by_username[profile.username] = profile.id
        self._profiles_by_email[profile.email] = profile.id
        self._profiles_by_user_id[profile.user_id] = profile.id

    def _get(self, profile_id: str) -> AuthProfile | None:
        profile = self._profiles_by_id.get(profile_id)
        return deepcopy(profile) if profile else None

    def get_by_username(self, username: str) -> AuthProfile | None:
        profile_id = self._profiles_by_username.get(username)
        return self._get(profile_id) if profile_id else None

    def get_by_email(self, email: str) -> AuthProfile | None:
        profile_id = self._profiles_by_email.get(email)
        return self._get(profile_id) if profile_id else None

    def get_by_user_id(self, user_id: str) -> AuthProfile | None:
        profile_id = self._profiles_by_user_id.get(user_id)
        return self._get(profile_id) if profile_id else None


class InMemoryProjectRepository(ProjectRepository):
    """Simple in-memory project storage."""

    def __init__(self) -> None:
        self._projects: dict[str, Project] = {}

    def save_project(self, project: Project) -> None:
        """Save or update a project."""
        self._projects[project.id] = deepcopy(project)

    def get_project(self, project_id: str) -> Project | None:
        """Retrieve a project by ID."""
        project = self._projects.get(project_id)
        return deepcopy(project) if project else None

    def list_projects(
        self,
        user_id: str | None = None,
        is_public: bool | None = None,
        mission_type: str | None = None,
    ) -> list[Project]:
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


class InMemoryMissionRepository(MissionRepository):
    """Simple in-memory mission storage."""

    def __init__(self) -> None:
        self._missions: dict[str, Mission] = {}

    def save_mission(self, mission: Mission) -> None:
        """Save or update a mission."""
        self._missions[mission.id] = deepcopy(mission)

    def get_mission(self, mission_id: str) -> Mission | None:
        """Retrieve a mission by ID."""
        mission = self._missions.get(mission_id)
        return deepcopy(mission) if mission else None

    def list_missions(
        self,
        user_id: str | None = None,
        status: str | None = None,
        mission_type: str | None = None,
    ) -> list[Mission]:
        """List missions with optional filtering."""
        results = []
        for mission in self._missions.values():
            if status is not None and mission.status != status:
                continue
            if mission_type is not None and mission.type != mission_type:
                continue
            results.append(deepcopy(mission))
        return results

    def delete_mission(self, mission_id: str) -> None:
        """Delete a mission by ID."""
        self._missions.pop(mission_id, None)


class InMemoryObjectMetadataRepository(ObjectMetadataRepository):
    """Simple in-memory object metadata storage."""

    def __init__(self) -> None:
        self._metadata: dict[str, dict] = {}
        self._initialize_default_metadata()

    def _initialize_default_metadata(self) -> None:
        """Initialize with default solar system metadata."""
        default_objects = [
            {
                "object_id": "sun",
                "name": "Sun",
                "type": "star",
                "description": "The central star of our solar system",
                "mass": 1.9891e30,
                "radius": 6.9634e8,
                "temperature": 5778.0,
                "has_atmosphere": False,
                "has_water": False,
                "distance_from_sun": 0.0,
            },
            {
                "object_id": "mercury",
                "name": "Mercury",
                "type": "planet",
                "description": "The smallest planet in our solar system",
                "mass": 3.3011e23,
                "radius": 2.4397e6,
                "temperature": 440.0,
                "has_atmosphere": False,
                "has_water": False,
                "distance_from_sun": 5.79e10,
            },
            {
                "object_id": "venus",
                "name": "Venus",
                "type": "planet",
                "description": "The hottest planet with a thick atmosphere",
                "mass": 4.8675e24,
                "radius": 6.0518e6,
                "temperature": 737.0,
                "has_atmosphere": True,
                "has_water": False,
                "distance_from_sun": 1.082e11,
            },
            {
                "object_id": "earth",
                "name": "Earth",
                "type": "planet",
                "description": "Our home planet with liquid water and life",
                "mass": 5.972e24,
                "radius": 6.371e6,
                "temperature": 288.0,
                "has_atmosphere": True,
                "has_water": True,
                "distance_from_sun": 1.496e11,
            },
            {
                "object_id": "mars",
                "name": "Mars",
                "type": "planet",
                "description": "The red planet, potential future home for humans",
                "mass": 6.4171e23,
                "radius": 3.3895e6,
                "temperature": 210.0,
                "has_atmosphere": True,
                "has_water": True,
                "distance_from_sun": 2.279e11,
            },
            {
                "object_id": "jupiter",
                "name": "Jupiter",
                "type": "planet",
                "description": "The largest planet, a gas giant",
                "mass": 1.8982e27,
                "radius": 6.9911e7,
                "temperature": 165.0,
                "has_atmosphere": True,
                "has_water": False,
                "distance_from_sun": 7.785e11,
            },
            {
                "object_id": "saturn",
                "name": "Saturn",
                "type": "planet",
                "description": "The ringed planet, famous for its beautiful rings",
                "mass": 5.6834e26,
                "radius": 5.8232e7,
                "temperature": 134.0,
                "has_atmosphere": True,
                "has_water": False,
                "distance_from_sun": 1.433e12,
            },
            {
                "object_id": "uranus",
                "name": "Uranus",
                "type": "planet",
                "description": "An ice giant with a tilted rotation axis",
                "mass": 8.6810e25,
                "radius": 2.5362e7,
                "temperature": 76.0,
                "has_atmosphere": True,
                "has_water": False,
                "distance_from_sun": 2.867e12,
            },
            {
                "object_id": "neptune",
                "name": "Neptune",
                "type": "planet",
                "description": "The farthest planet, an ice giant with strong winds",
                "mass": 1.02413e26,
                "radius": 2.4622e7,
                "temperature": 72.0,
                "has_atmosphere": True,
                "has_water": False,
                "distance_from_sun": 4.515e12,
            },
        ]
        for obj in default_objects:
            object_id = obj.pop("object_id")
            self._metadata[object_id] = obj

    def save_metadata(self, object_id: str, metadata: dict) -> None:
        """Save or update metadata for an object."""
        self._metadata[object_id] = deepcopy(metadata)

    def get_metadata(self, object_id: str) -> dict | None:
        """Retrieve metadata for an object by ID."""
        metadata = self._metadata.get(object_id)
        return deepcopy(metadata) if metadata else None

    def search_metadata(
        self,
        query: str | None = None,
        object_type: str | None = None,
        min_mass: float | None = None,
        max_mass: float | None = None,
        has_atmosphere: bool | None = None,
        limit: int = 100,
    ) -> list[dict]:
        """Search for objects by metadata criteria."""
        results = []
        query_lower = query.lower() if query else None

        for object_id, metadata in self._metadata.items():
            # Text search
            if query_lower:
                searchable_text = (
                    metadata.get("name", "")
                    + " "
                    + metadata.get("description", "")
                    + " "
                    + metadata.get("type", "")
                ).lower()
                if query_lower not in searchable_text:
                    continue

            # Type filter
            if object_type and metadata.get("type") != object_type:
                continue

            # Mass filters
            mass = metadata.get("mass", 0.0)
            if min_mass is not None and mass < min_mass:
                continue
            if max_mass is not None and mass > max_mass:
                continue

            # Atmosphere filter
            if has_atmosphere is not None:
                if metadata.get("has_atmosphere") != has_atmosphere:
                    continue

            result = deepcopy(metadata)
            result["object_id"] = object_id
            results.append(result)
            if len(results) >= limit:
                break

        return results

    def list_all_metadata(self) -> list[dict]:
        """List all stored metadata."""
        return [deepcopy(metadata) for metadata in self._metadata.values()]

    def delete_metadata(self, object_id: str) -> None:
        """Delete metadata for an object."""
        self._metadata.pop(object_id, None)

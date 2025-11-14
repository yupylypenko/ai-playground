"""
Storage Ports (Interfaces)

Protocols defining storage operations for the Cosmic Flight Simulator.
These define the contracts that storage adapters must implement.
"""

from __future__ import annotations

from typing import List, Optional, Protocol

from src.models import AuthProfile, Mission, Objective, User


class UserRepository(Protocol):
    """
    Protocol for user data storage operations.

    Defines the interface for persisting and retrieving user profiles.
    """

    def save_user(self, user: User) -> None:
        """
        Save or update a user profile.

        Args:
            user: User instance to save
        """
        ...

    def get_user(self, user_id: str) -> Optional[User]:
        """
        Retrieve a user by ID.

        Args:
            user_id: Unique user identifier

        Returns:
            User instance or None if not found
        """
        ...

    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Retrieve a user by username.

        Args:
            username: Username to search for

        Returns:
            User instance or None if not found
        """
        ...

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Retrieve a user by email.

        Args:
            email: Email address to search for

        Returns:
            User instance or None if not found
        """
        ...

    def list_users(self) -> List[User]:
        """
        List all users.

        Returns:
            List of all user instances
        """
        ...

    def delete_user(self, user_id: str) -> None:
        """
        Delete a user by ID.

        Args:
            user_id: Unique user identifier
        """
        ...


class MissionRepository(Protocol):
    """
    Protocol for mission data storage operations.

    Defines the interface for persisting and retrieving missions.
    """

    def save_mission(self, mission: Mission) -> None:
        """
        Save or update a mission.

        Args:
            mission: Mission instance to save
        """
        ...

    def get_mission(self, mission_id: str) -> Optional[Mission]:
        """
        Retrieve a mission by ID.

        Args:
            mission_id: Unique mission identifier

        Returns:
            Mission instance or None if not found
        """
        ...

    def list_missions(
        self,
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        mission_type: Optional[str] = None,
    ) -> List[Mission]:
        """
        List missions with optional filtering.

        Args:
            user_id: Filter by user ID (if missions are user-specific)
            status: Filter by status ("not_started", "in_progress", "completed", "failed")
            mission_type: Filter by type ("tutorial", "free_flight", "challenge")

        Returns:
            List of matching mission instances
        """
        ...

    def delete_mission(self, mission_id: str) -> None:
        """
        Delete a mission by ID.

        Args:
            mission_id: Unique mission identifier
        """
        ...


class ObjectiveRepository(Protocol):
    """
    Protocol for objective data storage operations.

    Defines the interface for persisting and retrieving mission objectives.
    """

    def save_objective(self, objective: Objective, mission_id: str) -> None:
        """
        Save or update an objective within a mission.

        Args:
            objective: Objective instance to save
            mission_id: ID of the parent mission
        """
        ...


class AuthRepository(Protocol):
    """
    Protocol for authentication profile storage.

    Separates credential persistence from user profile data.
    """

    def save_profile(self, profile: AuthProfile) -> None:
        """
        Persist an authentication profile.

        Args:
            profile: AuthProfile instance
        """
        ...

    def get_by_username(self, username: str) -> Optional[AuthProfile]:
        """
        Retrieve a profile by username.

        Args:
            username: Username string
        """
        ...

    def get_by_email(self, email: str) -> Optional[AuthProfile]:
        """
        Retrieve a profile by email.

        Args:
            email: Email address
        """
        ...

    def get_by_user_id(self, user_id: str) -> Optional[AuthProfile]:
        """
        Retrieve a profile by associated user ID.

        Args:
            user_id: User identifier
        """
        ...

    def get_objective(self, objective_id: str, mission_id: str) -> Optional[Objective]:
        """
        Retrieve an objective by ID within a mission.

        Args:
            objective_id: Unique objective identifier
            mission_id: ID of the parent mission

        Returns:
            Objective instance or None if not found
        """
        ...

    def list_objectives(self, mission_id: str) -> List[Objective]:
        """
        List all objectives for a mission.

        Args:
            mission_id: ID of the parent mission

        Returns:
            List of objective instances
        """
        ...

    def delete_objective(self, objective_id: str, mission_id: str) -> None:
        """
        Delete an objective by ID.

        Args:
            objective_id: Unique objective identifier
        """
        ...

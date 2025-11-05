"""
Application Services

Services that coordinate domain logic with storage repositories.
"""

from __future__ import annotations

from typing import List, Optional

from src.cockpit.storage import MissionRepository, UserRepository
from src.models import Mission, User


class UserService:
    """
    Service for user management operations.

    Coordinates user operations with storage repositories.
    """

    def __init__(self, user_repository: UserRepository) -> None:
        """
        Initialize user service.

        Args:
            user_repository: User repository implementation
        """
        self.user_repository = user_repository

    def create_user(
        self, username: str, email: str, display_name: str, user_id: Optional[str] = None
    ) -> User:
        """
        Create a new user.

        Args:
            username: Username
            email: Email address
            display_name: Display name
            user_id: Optional user ID (generated if not provided)

        Returns:
            Created user instance

        Raises:
            ValueError: If username or email already exists
        """
        if self.user_repository.get_user_by_username(username):
            raise ValueError(f"Username '{username}' already exists")
        if self.user_repository.get_user_by_email(email):
            raise ValueError(f"Email '{email}' already exists")

        if not user_id:
            import uuid
            user_id = f"user-{uuid.uuid4().hex[:8]}"

        user = User(
            id=user_id,
            username=username,
            email=email,
            display_name=display_name,
        )
        self.user_repository.save_user(user)
        return user

    def get_user(self, user_id: str) -> Optional[User]:
        """
        Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User instance or None
        """
        return self.user_repository.get_user(user_id)

    def update_user(self, user: User) -> None:
        """
        Update user profile.

        Args:
            user: User instance to update
        """
        self.user_repository.save_user(user)


class MissionService:
    """
    Service for mission management operations.

    Coordinates mission operations with storage repositories.
    """

    def __init__(self, mission_repository: MissionRepository) -> None:
        """
        Initialize mission service.

        Args:
            mission_repository: Mission repository implementation
        """
        self.mission_repository = mission_repository

    def create_mission(
        self,
        name: str,
        mission_type: str,
        difficulty: str,
        description: str,
        mission_id: Optional[str] = None,
    ) -> Mission:
        """
        Create a new mission.

        Args:
            name: Mission name
            mission_type: Mission type ("tutorial", "free_flight", "challenge")
            difficulty: Difficulty level
            description: Mission description
            mission_id: Optional mission ID (generated if not provided)

        Returns:
            Created mission instance
        """
        if not mission_id:
            import uuid
            mission_id = f"mission-{uuid.uuid4().hex[:8]}"

        mission = Mission(
            id=mission_id,
            name=name,
            type=mission_type,
            difficulty=difficulty,
            description=description,
        )
        self.mission_repository.save_mission(mission)
        return mission

    def get_mission(self, mission_id: str) -> Optional[Mission]:
        """
        Get mission by ID.

        Args:
            mission_id: Mission ID

        Returns:
            Mission instance or None
        """
        return self.mission_repository.get_mission(mission_id)

    def list_user_missions(
        self, user_id: str, status: Optional[str] = None
    ) -> List[Mission]:
        """
        List missions for a user.

        Args:
            user_id: User ID
            status: Optional status filter

        Returns:
            List of mission instances
        """
        return self.mission_repository.list_missions(user_id=user_id, status=status)

    def update_mission(self, mission: Mission) -> None:
        """
        Update mission.

        Args:
            mission: Mission instance to update
        """
        self.mission_repository.save_mission(mission)


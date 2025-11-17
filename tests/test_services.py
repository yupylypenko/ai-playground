"""
Tests for application services.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Dict, List, Optional

import pytest

from src.cockpit.memory import InMemoryUserRepository
from src.cockpit.services import MissionService, UserService
from src.cockpit.storage import MissionRepository
from src.models import Mission


class InMemoryMissionRepository(MissionRepository):
    """Simple in-memory mission repository for testing."""

    def __init__(self) -> None:
        self._missions: Dict[str, Mission] = {}

    def save_mission(self, mission: Mission) -> None:
        self._missions[mission.id] = deepcopy(mission)

    def get_mission(self, mission_id: str) -> Optional[Mission]:
        mission = self._missions.get(mission_id)
        return deepcopy(mission) if mission else None

    def list_missions(
        self,
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        mission_type: Optional[str] = None,
    ) -> List[Mission]:
        filtered = []
        for mission in self._missions.values():
            if status and mission.status != status:
                continue
            if mission_type and mission.type != mission_type:
                continue
            filtered.append(deepcopy(mission))
        return filtered

    def delete_mission(self, mission_id: str) -> None:
        self._missions.pop(mission_id, None)


class TestUserService:
    """Tests for UserService."""

    def test_create_user_with_custom_id(self) -> None:
        """Test creating a user with a custom user ID."""
        repo = InMemoryUserRepository()
        service = UserService(repo)

        user = service.create_user(
            username="testuser",
            email="test@example.com",
            display_name="Test User",
            user_id="custom-id-123",
        )

        assert user.id == "custom-id-123"
        assert user.username == "testuser"
        assert repo.get_user("custom-id-123") == user

    def test_create_user_duplicate_username(self) -> None:
        """Test creating a user with duplicate username raises ValueError."""
        repo = InMemoryUserRepository()
        service = UserService(repo)

        service.create_user(
            username="testuser", email="test1@example.com", display_name="User 1"
        )

        with pytest.raises(ValueError, match="Username 'testuser' already exists"):
            service.create_user(
                username="testuser", email="test2@example.com", display_name="User 2"
            )

    def test_create_user_duplicate_email(self) -> None:
        """Test creating a user with duplicate email raises ValueError."""
        repo = InMemoryUserRepository()
        service = UserService(repo)

        service.create_user(
            username="user1", email="test@example.com", display_name="User 1"
        )

        with pytest.raises(ValueError, match="Email 'test@example.com' already exists"):
            service.create_user(
                username="user2", email="test@example.com", display_name="User 2"
            )

    def test_get_user_existing(self) -> None:
        """Test getting an existing user."""
        repo = InMemoryUserRepository()
        service = UserService(repo)

        created = service.create_user(
            username="testuser", email="test@example.com", display_name="Test User"
        )

        retrieved = service.get_user(created.id)
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.username == "testuser"

    def test_get_user_nonexistent(self) -> None:
        """Test getting a non-existent user returns None."""
        repo = InMemoryUserRepository()
        service = UserService(repo)

        result = service.get_user("nonexistent-id")
        assert result is None

    def test_update_user(self) -> None:
        """Test updating a user."""
        repo = InMemoryUserRepository()
        service = UserService(repo)

        user = service.create_user(
            username="testuser", email="test@example.com", display_name="Test User"
        )

        user.display_name = "Updated Name"
        service.update_user(user)

        updated = repo.get_user(user.id)
        assert updated is not None
        assert updated.display_name == "Updated Name"


class TestMissionService:
    """Tests for MissionService."""

    def test_create_mission_with_custom_id(self) -> None:
        """Test creating a mission with a custom mission ID."""
        repo = InMemoryMissionRepository()
        service = MissionService(repo)

        mission = service.create_mission(
            name="Test Mission",
            mission_type="tutorial",
            difficulty="beginner",
            description="A test mission",
            mission_id="custom-mission-123",
        )

        assert mission.id == "custom-mission-123"
        assert mission.name == "Test Mission"
        assert repo.get_mission("custom-mission-123") == mission

    def test_create_mission_auto_generated_id(self) -> None:
        """Test creating a mission with auto-generated ID."""
        repo = InMemoryMissionRepository()
        service = MissionService(repo)

        mission = service.create_mission(
            name="Test Mission",
            mission_type="tutorial",
            difficulty="beginner",
            description="A test mission",
        )

        assert mission.id.startswith("mission-")
        assert len(mission.id) > 8

    def test_get_mission_existing(self) -> None:
        """Test getting an existing mission."""
        repo = InMemoryMissionRepository()
        service = MissionService(repo)

        created = service.create_mission(
            name="Test Mission",
            mission_type="tutorial",
            difficulty="beginner",
            description="A test mission",
        )

        retrieved = service.get_mission(created.id)
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == "Test Mission"

    def test_get_mission_nonexistent(self) -> None:
        """Test getting a non-existent mission returns None."""
        repo = InMemoryMissionRepository()
        service = MissionService(repo)

        result = service.get_mission("nonexistent-id")
        assert result is None

    def test_list_user_missions_with_status_filter(self) -> None:
        """Test listing missions with status filter."""
        repo = InMemoryMissionRepository()
        service = MissionService(repo)

        mission1 = service.create_mission(
            name="Mission 1",
            mission_type="tutorial",
            difficulty="beginner",
            description="Mission 1",
        )
        mission1.status = "completed"

        mission2 = service.create_mission(
            name="Mission 2",
            mission_type="challenge",
            difficulty="intermediate",
            description="Mission 2",
        )
        mission2.status = "in_progress"

        repo.save_mission(mission1)
        repo.save_mission(mission2)

        completed = service.list_user_missions("user-123", status="completed")
        assert len(completed) == 1
        assert completed[0].id == mission1.id

    def test_list_user_missions_no_filter(self) -> None:
        """Test listing missions without status filter."""
        repo = InMemoryMissionRepository()
        service = MissionService(repo)

        mission1 = service.create_mission(
            name="Mission 1",
            mission_type="tutorial",
            difficulty="beginner",
            description="Mission 1",
        )
        mission2 = service.create_mission(
            name="Mission 2",
            mission_type="challenge",
            difficulty="intermediate",
            description="Mission 2",
        )

        repo.save_mission(mission1)
        repo.save_mission(mission2)

        all_missions = service.list_user_missions("user-123")
        assert len(all_missions) >= 2

    def test_update_mission(self) -> None:
        """Test updating a mission."""
        repo = InMemoryMissionRepository()
        service = MissionService(repo)

        mission = service.create_mission(
            name="Test Mission",
            mission_type="tutorial",
            difficulty="beginner",
            description="A test mission",
        )

        mission.name = "Updated Mission"
        mission.status = "completed"
        service.update_mission(mission)

        updated = repo.get_mission(mission.id)
        assert updated is not None
        assert updated.name == "Updated Mission"
        assert updated.status == "completed"

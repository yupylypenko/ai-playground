"""
Tests for MongoDB Storage Adapters

Tests for MongoDB repository implementations.
"""

from __future__ import annotations

import pytest
from pymongo import MongoClient

from src.adapters.mongodb import (
    MongoDatabase,
    MongoMissionRepository,
    MongoObjectiveRepository,
    MongoUserRepository,
)
from src.cockpit.config import MongoConfig
from src.models import Mission, Objective, User


def _mongodb_available() -> bool:
    """Check if MongoDB is available for testing."""
    try:
        client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=1000)
        client.server_info()
        client.close()
        return True
    except Exception:
        return False


@pytest.fixture
def mongo_config() -> MongoConfig:
    """Create MongoDB configuration for testing."""
    return MongoConfig(
        host="localhost",
        port=27017,
        database="cosmic_flight_sim_test",
    )


@pytest.fixture
def mongo_db(mongo_config: MongoConfig) -> MongoDatabase:
    """
    Create MongoDB database connection for testing.

    Cleans up test database after tests.
    """
    db = MongoDatabase(mongo_config)
    db.connect()
    yield db
    # Cleanup: drop test database
    if db.client:
        db.client.drop_database(mongo_config.database)
    db.disconnect()


@pytest.fixture
def user_repo(mongo_db: MongoDatabase) -> MongoUserRepository:
    """Create user repository for testing."""
    return mongo_db.user_repository


@pytest.fixture
def mission_repo(mongo_db: MongoDatabase) -> MongoMissionRepository:
    """Create mission repository for testing."""
    return mongo_db.mission_repository


@pytest.fixture
def objective_repo(mongo_db: MongoDatabase) -> MongoObjectiveRepository:
    """Create objective repository for testing."""
    return mongo_db.objective_repository


@pytest.mark.skipif(
    not _mongodb_available(),
    reason="MongoDB not available",
)
class TestMongoUserRepository:
    """Tests for MongoUserRepository."""

    def test_save_and_get_user(self, user_repo: MongoUserRepository) -> None:
        """Test saving and retrieving a user."""
        user = User(
            id="test-user-1",
            username="testuser",
            email="test@example.com",
            display_name="Test User",
        )
        user_repo.save_user(user)

        retrieved = user_repo.get_user("test-user-1")
        assert retrieved is not None
        assert retrieved.id == "test-user-1"
        assert retrieved.username == "testuser"
        assert retrieved.email == "test@example.com"

    def test_get_user_by_username(self, user_repo: MongoUserRepository) -> None:
        """Test retrieving user by username."""
        user = User(
            id="test-user-2",
            username="testuser2",
            email="test2@example.com",
            display_name="Test User 2",
        )
        user_repo.save_user(user)

        retrieved = user_repo.get_user_by_username("testuser2")
        assert retrieved is not None
        assert retrieved.username == "testuser2"

    def test_get_user_by_email(self, user_repo: MongoUserRepository) -> None:
        """Test retrieving user by email."""
        user = User(
            id="test-user-3",
            username="testuser3",
            email="test3@example.com",
            display_name="Test User 3",
        )
        user_repo.save_user(user)

        retrieved = user_repo.get_user_by_email("test3@example.com")
        assert retrieved is not None
        assert retrieved.email == "test3@example.com"

    def test_list_users(self, user_repo: MongoUserRepository) -> None:
        """Test listing all users."""
        user1 = User(
            id="test-user-4",
            username="testuser4",
            email="test4@example.com",
            display_name="Test User 4",
        )
        user2 = User(
            id="test-user-5",
            username="testuser5",
            email="test5@example.com",
            display_name="Test User 5",
        )
        user_repo.save_user(user1)
        user_repo.save_user(user2)

        users = user_repo.list_users()
        assert len(users) >= 2
        user_ids = [u.id for u in users]
        assert "test-user-4" in user_ids
        assert "test-user-5" in user_ids

    def test_delete_user(self, user_repo: MongoUserRepository) -> None:
        """Test deleting a user."""
        user = User(
            id="test-user-6",
            username="testuser6",
            email="test6@example.com",
            display_name="Test User 6",
        )
        user_repo.save_user(user)

        user_repo.delete_user("test-user-6")

        retrieved = user_repo.get_user("test-user-6")
        assert retrieved is None


@pytest.mark.skipif(
    not _mongodb_available(),
    reason="MongoDB not available",
)
class TestMongoMissionRepository:
    """Tests for MongoMissionRepository."""

    def test_save_and_get_mission(self, mission_repo: MongoMissionRepository) -> None:
        """Test saving and retrieving a mission."""
        mission = Mission(
            id="test-mission-1",
            name="Test Mission",
            type="tutorial",
            difficulty="beginner",
            description="A test mission",
        )
        mission_repo.save_mission(mission)

        retrieved = mission_repo.get_mission("test-mission-1")
        assert retrieved is not None
        assert retrieved.id == "test-mission-1"
        assert retrieved.name == "Test Mission"

    def test_mission_with_objectives(
        self, mission_repo: MongoMissionRepository
    ) -> None:
        """Test saving and retrieving mission with objectives."""
        mission = Mission(
            id="test-mission-2",
            name="Test Mission 2",
            type="challenge",
            difficulty="intermediate",
            description="Mission with objectives",
        )
        mission.objectives.append(
            Objective(
                id="obj-1",
                description="Reach orbit",
                type="reach",
                target_id="earth",
            )
        )
        mission.objectives.append(
            Objective(
                id="obj-2",
                description="Collect samples",
                type="collect",
            )
        )
        mission_repo.save_mission(mission)

        retrieved = mission_repo.get_mission("test-mission-2")
        assert retrieved is not None
        assert len(retrieved.objectives) == 2
        assert retrieved.objectives[0].id == "obj-1"
        assert retrieved.objectives[1].id == "obj-2"

    def test_list_missions(self, mission_repo: MongoMissionRepository) -> None:
        """Test listing missions with filters."""
        mission1 = Mission(
            id="test-mission-3",
            name="Tutorial Mission",
            type="tutorial",
            difficulty="beginner",
            description="Tutorial",
        )
        mission1.status = "completed"

        mission2 = Mission(
            id="test-mission-4",
            name="Challenge Mission",
            type="challenge",
            difficulty="advanced",
            description="Challenge",
        )
        mission2.status = "in_progress"

        mission_repo.save_mission(mission1)
        mission_repo.save_mission(mission2)

        completed = mission_repo.list_missions(status="completed")
        assert len(completed) >= 1
        assert all(m.status == "completed" for m in completed)

        tutorials = mission_repo.list_missions(mission_type="tutorial")
        assert len(tutorials) >= 1
        assert all(m.type == "tutorial" for m in tutorials)


@pytest.mark.skipif(
    not _mongodb_available(),
    reason="MongoDB not available",
)
class TestMongoObjectiveRepository:
    """Tests for MongoObjectiveRepository."""

    def test_save_and_get_objective(
        self, mission_repo: MongoMissionRepository, objective_repo: MongoObjectiveRepository
    ) -> None:
        """Test saving and retrieving objectives."""
        mission = Mission(
            id="test-mission-obj",
            name="Mission with Objectives",
            type="tutorial",
            difficulty="beginner",
            description="Test mission",
        )
        mission_repo.save_mission(mission)

        objective = Objective(
            id="obj-test-1",
            description="Test objective",
            type="reach",
            target_id="earth",
        )
        objective_repo.save_objective(objective, "test-mission-obj")

        retrieved = objective_repo.get_objective("obj-test-1", "test-mission-obj")
        assert retrieved is not None
        assert retrieved.id == "obj-test-1"
        assert retrieved.description == "Test objective"

    def test_list_objectives(
        self, mission_repo: MongoMissionRepository, objective_repo: MongoObjectiveRepository
    ) -> None:
        """Test listing objectives for a mission."""
        mission = Mission(
            id="test-mission-obj2",
            name="Mission with Multiple Objectives",
            type="challenge",
            difficulty="intermediate",
            description="Test mission",
        )
        mission_repo.save_mission(mission)

        obj1 = Objective(id="obj-1", description="Objective 1", type="reach")
        obj2 = Objective(id="obj-2", description="Objective 2", type="collect")

        objective_repo.save_objective(obj1, "test-mission-obj2")
        objective_repo.save_objective(obj2, "test-mission-obj2")

        objectives = objective_repo.list_objectives("test-mission-obj2")
        assert len(objectives) == 2
        obj_ids = [obj.id for obj in objectives]
        assert "obj-1" in obj_ids
        assert "obj-2" in obj_ids


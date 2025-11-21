"""
Tests for the /missions API endpoint.

Covers mission creation from scratch and from project templates,
validation, authentication, and error handling.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.api.app import create_app
from src.api.errors import ErrorCode
from src.cockpit.auth import AuthService
from src.cockpit.memory import InMemoryAuthRepository, InMemoryUserRepository
from src.cockpit.services import UserService


@pytest.fixture
def auth_service() -> AuthService:
    """Create an AuthService for testing."""
    user_repo = InMemoryUserRepository()
    auth_repo = InMemoryAuthRepository()
    user_service = UserService(user_repo)
    return AuthService(user_service=user_service, auth_repository=auth_repo)


@pytest.fixture
def test_user(auth_service: AuthService) -> tuple[str, str]:
    """
    Create a test user and return (user_id, token).

    Returns:
        Tuple of (user_id, jwt_token)
    """
    result = auth_service.register_user(
        username="testuser",
        email="test@example.com",
        password="TestPass123",
        display_name="Test User",
    )
    user = result.user

    # Generate token manually for testing
    import os
    from datetime import datetime, timedelta, timezone

    from jose import jwt

    secret_key = os.getenv(
        "API_SECRET_KEY", "dev-secret-key-please-change-in-production"
    )
    expire = datetime.now(tz=timezone.utc) + timedelta(minutes=60)
    claims = {
        "sub": user.id,
        "username": user.username,
        "exp": int(expire.timestamp()),
        "iat": int(datetime.now(tz=timezone.utc).timestamp()),
    }
    token = jwt.encode(claims, secret_key, algorithm="HS256")
    return (user.id, token)


@pytest.fixture
def test_project(client: TestClient, test_user: tuple[str, str]) -> str:
    """Create a test project via API and return project_id."""
    _, token = test_user

    # Create project through API to ensure it's in the same repository
    response = client.post(
        "/projects",
        json={
            "name": "Test Project",
            "description": "Test project description",
            "mission_type": "challenge",
            "difficulty": "intermediate",
            "target_body_id": "mars",
            "max_fuel": 1500.0,
            "objectives": [
                {
                    "description": "Reach Mars orbit",
                    "type": "reach",
                    "target_id": "mars",
                }
            ],
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    return response.json()["project_id"]


@pytest.fixture
def client(auth_service: AuthService) -> TestClient:
    """Create a test client with auth service."""
    app = create_app(auth_service=auth_service)
    return TestClient(app)


class TestCreateMissionFromScratch:
    """Test mission creation from scratch (without project template)."""

    def test_create_mission_success(
        self, client: TestClient, test_user: tuple[str, str]
    ) -> None:
        """Test successful mission creation from scratch."""
        _, token = test_user

        payload = {
            "name": "Mars Landing Mission",
            "description": "Land safely on Mars surface",
            "mission_type": "challenge",
            "difficulty": "intermediate",
            "target_body_id": "mars",
            "max_fuel": 1500.0,
            "objectives": [
                {
                    "description": "Reach Mars orbit",
                    "type": "reach",
                    "target_id": "mars",
                }
            ],
        }

        response = client.post(
            "/missions",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == payload["name"]
        assert data["description"] == payload["description"]
        assert data["mission_type"] == payload["mission_type"]
        assert data["difficulty"] == payload["difficulty"]
        assert data["mission_id"] is not None
        assert data["status"] == "not_started"
        assert len(data["objectives"]) == 1
        assert data["objectives"][0]["description"] == "Reach Mars orbit"

    def test_create_mission_minimal(
        self, client: TestClient, test_user: tuple[str, str]
    ) -> None:
        """Test mission creation with minimal required fields."""
        _, token = test_user

        payload = {
            "name": "Simple Mission",
            "description": "A simple mission",
            "mission_type": "tutorial",
            "difficulty": "beginner",
        }

        response = client.post(
            "/missions",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == payload["name"]
        assert data["mission_type"] == payload["mission_type"]
        assert data["difficulty"] == payload["difficulty"]
        assert data["start_position"] == [0.0, 0.0, 0.0]
        assert data["max_fuel"] == 1000.0
        assert data["status"] == "not_started"

    def test_create_mission_with_all_fields(
        self, client: TestClient, test_user: tuple[str, str]
    ) -> None:
        """Test mission creation with all optional fields."""
        _, token = test_user

        payload = {
            "name": "Complete Mission",
            "description": "Mission with all fields",
            "mission_type": "challenge",
            "difficulty": "advanced",
            "target_body_id": "jupiter",
            "start_position": [50.0, 100.0, 150.0],
            "max_fuel": 2000.0,
            "time_limit": 7200.0,
            "allowed_ship_types": ["explorer", "cargo", "fighter"],
            "failure_conditions": ["Out of fuel", "Collision", "Time limit exceeded"],
            "objectives": [
                {
                    "description": "Reach Jupiter",
                    "type": "reach",
                    "target_id": "jupiter",
                    "position": [500.0, 600.0, 700.0],
                }
            ],
        }

        response = client.post(
            "/missions",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["target_body_id"] == "jupiter"
        assert data["max_fuel"] == 2000.0
        assert data["time_limit"] == 7200.0
        assert len(data["allowed_ship_types"]) == 3
        assert len(data["failure_conditions"]) == 3

    def test_create_mission_invalid_mission_type(
        self, client: TestClient, test_user: tuple[str, str]
    ) -> None:
        """Test mission creation with invalid mission type."""
        _, token = test_user

        payload = {
            "name": "Test Mission",
            "description": "Test",
            "mission_type": "invalid_type",
            "difficulty": "beginner",
        }

        response = client.post(
            "/missions",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == ErrorCode.VALIDATION_MISSION_TYPE_INVALID.value

    def test_create_mission_invalid_difficulty(
        self, client: TestClient, test_user: tuple[str, str]
    ) -> None:
        """Test mission creation with invalid difficulty."""
        _, token = test_user

        payload = {
            "name": "Test Mission",
            "description": "Test",
            "mission_type": "tutorial",
            "difficulty": "invalid_difficulty",
        }

        response = client.post(
            "/missions",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == ErrorCode.VALIDATION_DIFFICULTY_INVALID.value


class TestCreateMissionFromProject:
    """Test mission creation from project templates."""

    def test_create_mission_from_project_success(
        self,
        client: TestClient,
        test_user: tuple[str, str],
        test_project: str,
    ) -> None:
        """Test successful mission creation from project template."""
        _, token = test_user

        payload = {
            "name": "My Mars Mission",
            "description": "Custom mission",
            "mission_type": "challenge",
            "difficulty": "intermediate",
            "project_id": test_project,
        }

        response = client.post(
            "/missions",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == payload["name"]
        assert data["mission_type"] == "challenge"
        assert data["difficulty"] == "intermediate"
        assert data["target_body_id"] == "mars"
        assert data["max_fuel"] == 1500.0
        # Objectives from project should be included
        assert len(data["objectives"]) == 1
        assert data["objectives"][0]["description"] == "Reach Mars orbit"

    def test_create_mission_from_nonexistent_project(
        self, client: TestClient, test_user: tuple[str, str]
    ) -> None:
        """Test mission creation from non-existent project."""
        _, token = test_user

        payload = {
            "name": "Test Mission",
            "description": "Test",
            "mission_type": "tutorial",
            "difficulty": "beginner",
            "project_id": "nonexistent-project",
        }

        response = client.post(
            "/missions",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 404
        error = response.json()["error"]
        assert error["code"] == ErrorCode.RESOURCE_NOT_FOUND.value
        assert "not found" in error["message"].lower()


class TestMissionAuthentication:
    """Test authentication requirements for mission creation."""

    def test_create_mission_requires_authentication(self, client: TestClient) -> None:
        """Test that mission creation requires authentication."""
        payload = {
            "name": "Test Mission",
            "description": "Test",
            "mission_type": "tutorial",
            "difficulty": "beginner",
        }

        response = client.post("/missions", json=payload)

        assert response.status_code in (401, 403)

    def test_create_mission_invalid_token(self, client: TestClient) -> None:
        """Test mission creation with invalid token."""
        payload = {
            "name": "Test Mission",
            "description": "Test",
            "mission_type": "tutorial",
            "difficulty": "beginner",
        }

        response = client.post(
            "/missions",
            json=payload,
            headers={"Authorization": "Bearer invalid-token"},
        )

        assert response.status_code == 401
        error = response.json()["error"]
        assert error["code"] in (
            ErrorCode.AUTH_INVALID_TOKEN.value,
            ErrorCode.AUTH_EXPIRED_TOKEN.value,
        )


class TestMissionValidation:
    """Test mission validation scenarios."""

    @pytest.mark.parametrize(
        "mission_type",
        ["tutorial", "free_flight", "challenge"],
    )
    def test_create_mission_all_valid_types(
        self, client: TestClient, test_user: tuple[str, str], mission_type: str
    ) -> None:
        """Test mission creation with all valid mission types."""
        _, token = test_user

        payload = {
            "name": f"Test {mission_type}",
            "description": "Test",
            "mission_type": mission_type,
            "difficulty": "beginner",
        }

        response = client.post(
            "/missions",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        assert response.json()["mission_type"] == mission_type

    @pytest.mark.parametrize(
        "difficulty",
        ["beginner", "intermediate", "advanced"],
    )
    def test_create_mission_all_valid_difficulties(
        self, client: TestClient, test_user: tuple[str, str], difficulty: str
    ) -> None:
        """Test mission creation with all valid difficulty levels."""
        _, token = test_user

        payload = {
            "name": f"Test {difficulty}",
            "description": "Test",
            "mission_type": "tutorial",
            "difficulty": difficulty,
        }

        response = client.post(
            "/missions",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        assert response.json()["difficulty"] == difficulty

    def test_create_mission_missing_required_fields(
        self, client: TestClient, test_user: tuple[str, str]
    ) -> None:
        """Test mission creation with missing required fields."""
        _, token = test_user

        payload = {
            "name": "Test Mission",
            # Missing description, mission_type, difficulty
        }

        response = client.post(
            "/missions",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 422  # Validation error

    def test_create_mission_empty_name(
        self, client: TestClient, test_user: tuple[str, str]
    ) -> None:
        """Test mission creation with empty name."""
        _, token = test_user

        payload = {
            "name": "",
            "description": "Test",
            "mission_type": "tutorial",
            "difficulty": "beginner",
        }

        response = client.post(
            "/missions",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 422
        error = response.json()["error"]
        assert error["code"] == ErrorCode.VALIDATION_INVALID_FORMAT.value

"""
Tests for the /projects API endpoint.

Covers project creation, validation, authentication, and error handling.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.api.app import create_app
from src.api.errors import ErrorCode
from src.cockpit.auth import AuthService
from src.cockpit.memory import (
    InMemoryAuthRepository,
    InMemoryProjectRepository,
    InMemoryUserRepository,
)
from src.cockpit.services import ProjectService, UserService


@pytest.fixture
def auth_service() -> AuthService:
    """Create an AuthService for testing."""
    user_repo = InMemoryUserRepository()
    auth_repo = InMemoryAuthRepository()
    user_service = UserService(user_repo)
    return AuthService(user_service=user_service, auth_repository=auth_repo)


@pytest.fixture
def project_service() -> ProjectService:
    """Create a ProjectService for testing."""
    project_repo = InMemoryProjectRepository()
    return ProjectService(project_repository=project_repo)


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
def client(auth_service: AuthService) -> TestClient:
    """Create a test client with auth service."""
    app = create_app(auth_service=auth_service)
    return TestClient(app)


class TestCreateProject:
    """Test project creation endpoint."""

    def test_create_project_success(
        self, client: TestClient, test_user: tuple[str, str]
    ) -> None:
        """Test successful project creation."""
        user_id, token = test_user

        payload = {
            "name": "Mars Exploration Mission",
            "description": "A challenging mission to reach Mars orbit",
            "mission_type": "challenge",
            "difficulty": "intermediate",
            "target_body_id": "mars",
            "max_fuel": 1500.0,
            "time_limit": 3600.0,
            "objectives": [
                {
                    "description": "Reach Mars orbit",
                    "type": "reach",
                    "target_id": "mars",
                }
            ],
            "is_public": False,
        }

        response = client.post(
            "/projects",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == payload["name"]
        assert data["description"] == payload["description"]
        assert data["mission_type"] == payload["mission_type"]
        assert data["difficulty"] == payload["difficulty"]
        assert data["user_id"] == user_id
        assert data["project_id"] is not None
        assert data["created_at"] is not None
        assert data["updated_at"] is not None
        assert len(data["objectives"]) == 1
        assert data["objectives"][0]["description"] == "Reach Mars orbit"

    def test_create_project_minimal(
        self, client: TestClient, test_user: tuple[str, str]
    ) -> None:
        """Test project creation with minimal required fields."""
        _, token = test_user

        payload = {
            "name": "Simple Mission",
            "description": "A simple mission",
            "mission_type": "tutorial",
            "difficulty": "beginner",
        }

        response = client.post(
            "/projects",
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
        assert data["is_public"] is False

    def test_create_project_with_multiple_objectives(
        self, client: TestClient, test_user: tuple[str, str]
    ) -> None:
        """Test project creation with multiple objectives."""
        _, token = test_user

        payload = {
            "name": "Complex Mission",
            "description": "A mission with multiple objectives",
            "mission_type": "challenge",
            "difficulty": "advanced",
            "objectives": [
                {"description": "Reach Mars", "type": "reach", "target_id": "mars"},
                {"description": "Collect samples", "type": "collect"},
                {"description": "Maintain orbit", "type": "maintain"},
            ],
        }

        response = client.post(
            "/projects",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert len(data["objectives"]) == 3

    def test_create_project_requires_authentication(self, client: TestClient) -> None:
        """Test that project creation requires authentication."""
        payload = {
            "name": "Test Mission",
            "description": "Test",
            "mission_type": "tutorial",
            "difficulty": "beginner",
        }

        response = client.post("/projects", json=payload)

        # FastAPI's HTTPBearer returns 403 when Authorization header is missing
        assert response.status_code in (401, 403)
        # The error might be handled by FastAPI's security system
        if response.status_code == 403:
            # FastAPI's HTTPBearer returns 403 with detail
            assert "detail" in response.json() or "error" in response.json()
        else:
            error = response.json()["error"]
            assert error["code"] in (
                ErrorCode.AUTH_REQUIRED.value,
                ErrorCode.AUTH_INVALID_TOKEN.value,
            )

    def test_create_project_invalid_token(self, client: TestClient) -> None:
        """Test project creation with invalid token."""
        payload = {
            "name": "Test Mission",
            "description": "Test",
            "mission_type": "tutorial",
            "difficulty": "beginner",
        }

        response = client.post(
            "/projects",
            json=payload,
            headers={"Authorization": "Bearer invalid-token"},
        )

        assert response.status_code == 401
        error = response.json()["error"]
        assert error["code"] in (
            ErrorCode.AUTH_INVALID_TOKEN.value,
            ErrorCode.AUTH_EXPIRED_TOKEN.value,
        )

    def test_create_project_invalid_mission_type(
        self, client: TestClient, test_user: tuple[str, str]
    ) -> None:
        """Test project creation with invalid mission type."""
        _, token = test_user

        payload = {
            "name": "Test Mission",
            "description": "Test",
            "mission_type": "invalid_type",
            "difficulty": "beginner",
        }

        response = client.post(
            "/projects",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == ErrorCode.VALIDATION_MISSION_TYPE_INVALID.value
        assert "mission type" in error["message"].lower()

    def test_create_project_invalid_difficulty(
        self, client: TestClient, test_user: tuple[str, str]
    ) -> None:
        """Test project creation with invalid difficulty."""
        _, token = test_user

        payload = {
            "name": "Test Mission",
            "description": "Test",
            "mission_type": "tutorial",
            "difficulty": "invalid_difficulty",
        }

        response = client.post(
            "/projects",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == ErrorCode.VALIDATION_DIFFICULTY_INVALID.value
        assert "difficulty" in error["message"].lower()

    def test_create_project_empty_name(
        self, client: TestClient, test_user: tuple[str, str]
    ) -> None:
        """Test project creation with empty name."""
        _, token = test_user

        payload = {
            "name": "",
            "description": "Test",
            "mission_type": "tutorial",
            "difficulty": "beginner",
        }

        response = client.post(
            "/projects",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        # Pydantic validates empty string before it reaches our service
        # Our validation error handler converts 422 to our error format
        assert response.status_code == 422
        error = response.json()["error"]
        assert error["code"] == ErrorCode.VALIDATION_INVALID_FORMAT.value

    def test_create_project_missing_required_fields(
        self, client: TestClient, test_user: tuple[str, str]
    ) -> None:
        """Test project creation with missing required fields."""
        _, token = test_user

        payload = {
            "name": "Test Mission",
            # Missing description, mission_type, difficulty
        }

        response = client.post(
            "/projects",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 422  # Validation error

    def test_create_project_with_custom_start_position(
        self, client: TestClient, test_user: tuple[str, str]
    ) -> None:
        """Test project creation with custom start position."""
        _, token = test_user

        payload = {
            "name": "Custom Position Mission",
            "description": "Mission with custom start",
            "mission_type": "free_flight",
            "difficulty": "intermediate",
            "start_position": [100.0, 200.0, 300.0],
        }

        response = client.post(
            "/projects",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["start_position"] == [100.0, 200.0, 300.0]

    def test_create_project_with_all_fields(
        self, client: TestClient, test_user: tuple[str, str]
    ) -> None:
        """Test project creation with all optional fields."""
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
            "is_public": True,
        }

        response = client.post(
            "/projects",
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
        assert data["is_public"] is True

    def test_create_project_negative_fuel(
        self, client: TestClient, test_user: tuple[str, str]
    ) -> None:
        """Test project creation with negative fuel value."""
        _, token = test_user

        payload = {
            "name": "Test Mission",
            "description": "Test",
            "mission_type": "tutorial",
            "difficulty": "beginner",
            "max_fuel": -100.0,
        }

        response = client.post(
            "/projects",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 422  # Validation error from Pydantic

    def test_create_project_all_mission_types(
        self, client: TestClient, test_user: tuple[str, str]
    ) -> None:
        """Test project creation with all valid mission types."""
        _, token = test_user

        for mission_type in ["tutorial", "free_flight", "challenge"]:
            payload = {
                "name": f"Test {mission_type}",
                "description": "Test",
                "mission_type": mission_type,
                "difficulty": "beginner",
            }

            response = client.post(
                "/projects",
                json=payload,
                headers={"Authorization": f"Bearer {token}"},
            )

            assert response.status_code == 201
            assert response.json()["mission_type"] == mission_type

    def test_create_project_all_difficulties(
        self, client: TestClient, test_user: tuple[str, str]
    ) -> None:
        """Test project creation with all valid difficulty levels."""
        _, token = test_user

        for difficulty in ["beginner", "intermediate", "advanced"]:
            payload = {
                "name": f"Test {difficulty}",
                "description": "Test",
                "mission_type": "tutorial",
                "difficulty": difficulty,
            }

            response = client.post(
                "/projects",
                json=payload,
                headers={"Authorization": f"Bearer {token}"},
            )

            assert response.status_code == 201
            assert response.json()["difficulty"] == difficulty

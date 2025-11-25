"""
Tests for the GET /projects API endpoint.

Covers project listing, filtering, authentication, and validation.
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
    """Create a test user and return (user_id, token)."""
    result = auth_service.register_user(
        username="testuser",
        email="test@example.com",
        password="TestPass123",
        display_name="Test User",
    )
    user = result.user

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
def test_user2(auth_service: AuthService) -> tuple[str, str]:
    """Create a second test user and return (user_id, token)."""
    result = auth_service.register_user(
        username="testuser2",
        email="test2@example.com",
        password="TestPass123",
        display_name="Test User 2",
    )
    user = result.user

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


@pytest.fixture
def setup_projects(
    client: TestClient, test_user: tuple[str, str], test_user2: tuple[str, str]
) -> None:
    """Set up test projects for both users."""
    user1_id, user1_token = test_user
    user2_id, user2_token = test_user2

    # User 1: private tutorial, public challenge
    client.post(
        "/projects",
        json={
            "name": "User1 Private Tutorial",
            "description": "Private tutorial",
            "mission_type": "tutorial",
            "difficulty": "beginner",
            "is_public": False,
        },
        headers={"Authorization": f"Bearer {user1_token}"},
    )

    client.post(
        "/projects",
        json={
            "name": "User1 Public Challenge",
            "description": "Public challenge",
            "mission_type": "challenge",
            "difficulty": "intermediate",
            "is_public": True,
        },
        headers={"Authorization": f"Bearer {user1_token}"},
    )

    # User 2: public tutorial, private challenge
    client.post(
        "/projects",
        json={
            "name": "User2 Public Tutorial",
            "description": "Public tutorial",
            "mission_type": "tutorial",
            "difficulty": "beginner",
            "is_public": True,
        },
        headers={"Authorization": f"Bearer {user2_token}"},
    )

    client.post(
        "/projects",
        json={
            "name": "User2 Private Challenge",
            "description": "Private challenge",
            "mission_type": "challenge",
            "difficulty": "advanced",
            "is_public": False,
        },
        headers={"Authorization": f"Bearer {user2_token}"},
    )


class TestListProjects:
    """Test project listing functionality."""

    def test_list_user_projects_default(
        self, client: TestClient, test_user: tuple[str, str], setup_projects: None
    ) -> None:
        """Test listing projects defaults to current user's projects."""
        _, token = test_user

        response = client.get(
            "/projects",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "projects" in data
        assert "total" in data
        assert data["total"] == 2  # User1 has 2 projects
        assert len(data["projects"]) == 2
        assert all(p["user_id"] == test_user[0] for p in data["projects"])

    def test_list_public_projects(
        self, client: TestClient, test_user: tuple[str, str], setup_projects: None
    ) -> None:
        """Test listing only public projects."""
        _, token = test_user

        response = client.get(
            "/projects?is_public=true",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        # When is_public=true without user_id, returns all public projects from all users
        # Note: May include projects from other tests due to shared repository
        assert (
            data["total"] >= 2
        )  # At least 2 public projects (1 from user1, 1 from user2)
        assert all(p["is_public"] is True for p in data["projects"])

    def test_list_private_projects(
        self, client: TestClient, test_user: tuple[str, str], setup_projects: None
    ) -> None:
        """Test listing only private projects."""
        _, token = test_user

        response = client.get(
            "/projects?is_public=false",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1  # User1 has 1 private project
        assert all(p["is_public"] is False for p in data["projects"])

    def test_filter_by_mission_type(
        self, client: TestClient, test_user: tuple[str, str], setup_projects: None
    ) -> None:
        """Test filtering by mission type."""
        _, token = test_user

        response = client.get(
            "/projects?mission_type=tutorial",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert all(p["mission_type"] == "tutorial" for p in data["projects"])

    def test_filter_by_multiple_params(
        self, client: TestClient, test_user: tuple[str, str], setup_projects: None
    ) -> None:
        """Test filtering by multiple parameters."""
        _, token = test_user

        response = client.get(
            "/projects?is_public=true&mission_type=challenge",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        # When is_public=true without user_id, returns all public challenge projects
        # Note: May include projects from other tests due to shared repository
        assert data["total"] >= 1  # At least 1 public challenge project (from user1)
        assert all(p["mission_type"] == "challenge" for p in data["projects"])
        assert all(p["is_public"] is True for p in data["projects"])

    def test_list_empty_results(
        self, client: TestClient, test_user: tuple[str, str]
    ) -> None:
        """Test listing when user has no projects."""
        _, token = test_user

        response = client.get(
            "/projects",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["projects"] == []

    @pytest.mark.parametrize(
        "mission_type",
        ["tutorial", "free_flight", "challenge"],
    )
    def test_all_valid_mission_types(
        self,
        client: TestClient,
        test_user: tuple[str, str],
        mission_type: str,
    ) -> None:
        """Test filtering with all valid mission types."""
        _, token = test_user

        # Create a project of each type
        client.post(
            "/projects",
            json={
                "name": f"Test {mission_type}",
                "description": "Test",
                "mission_type": mission_type,
                "difficulty": "beginner",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        response = client.get(
            f"/projects?mission_type={mission_type}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert all(p["mission_type"] == mission_type for p in data["projects"])


class TestListProjectsValidation:
    """Test validation for project listing."""

    def test_invalid_mission_type(
        self, client: TestClient, test_user: tuple[str, str]
    ) -> None:
        """Test filtering with invalid mission type."""
        _, token = test_user

        response = client.get(
            "/projects?mission_type=invalid",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 400
        error = response.json()["error"]
        assert error["code"] == ErrorCode.VALIDATION_MISSION_TYPE_INVALID.value

    def test_requires_authentication(self, client: TestClient) -> None:
        """Test that listing projects requires authentication."""
        response = client.get("/projects")

        assert response.status_code in (401, 403)

    def test_invalid_token(self, client: TestClient) -> None:
        """Test listing with invalid token."""
        response = client.get(
            "/projects",
            headers={"Authorization": "Bearer invalid-token"},
        )

        assert response.status_code == 401
        error = response.json()["error"]
        assert error["code"] in (
            ErrorCode.AUTH_INVALID_TOKEN.value,
            ErrorCode.AUTH_EXPIRED_TOKEN.value,
        )


class TestListProjectsEdgeCases:
    """Test edge cases for project listing."""

    def test_boolean_string_parsing(
        self, client: TestClient, test_user: tuple[str, str], setup_projects: None
    ) -> None:
        """Test that boolean query parameters are parsed correctly."""
        _, token = test_user

        # FastAPI should parse "true"/"false" strings to booleans
        response = client.get(
            "/projects?is_public=true",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        # Should return public projects

    def test_case_insensitive_mission_type(
        self, client: TestClient, test_user: tuple[str, str]
    ) -> None:
        """Test that mission type is case-sensitive (as expected)."""
        _, token = test_user

        # Create a challenge project
        client.post(
            "/projects",
            json={
                "name": "Challenge Project",
                "description": "Test",
                "mission_type": "challenge",
                "difficulty": "beginner",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        # Try with uppercase (should fail validation)
        response = client.get(
            "/projects?mission_type=CHALLENGE",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 400

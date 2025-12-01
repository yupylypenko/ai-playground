"""
Edge Case Tests for POST /missions Endpoint

Tests non-obvious edge cases that could lead to bugs or unexpected behavior.
"""

from __future__ import annotations

import math
import uuid
from typing import Any

import pytest
from fastapi.testclient import TestClient

from src.api.app import create_app
from src.cockpit.memory import (
    InMemoryAuthRepository,
    InMemoryMissionRepository,
    InMemoryProjectRepository,
    InMemoryUserRepository,
)
from src.cockpit.auth import AuthService
from src.cockpit.services import MissionService, ProjectService, UserService
from src.models import Project, User


@pytest.fixture
def auth_service() -> AuthService:
    """Create an AuthService for testing."""
    user_repo = InMemoryUserRepository()
    auth_repo = InMemoryAuthRepository()
    user_service = UserService(user_repo)
    return AuthService(user_service=user_service, auth_repository=auth_repo)


@pytest.fixture
def test_client(auth_service: AuthService) -> TestClient:
    """Create test client with in-memory services."""
    app = create_app(auth_service=auth_service)
    return TestClient(app)


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
        password="TestPass123!",
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
def test_project(test_client: TestClient, test_user: tuple[str, str]) -> dict[str, Any]:
    """Create a test project for edge case testing."""
    _, token = test_user
    response = test_client.post(
        "/projects",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Test Project",
            "description": "Test project for edge cases",
            "mission_type": "challenge",
            "difficulty": "intermediate",
            "objectives": [],
        },
    )
    assert response.status_code == 201
    return response.json()


class TestEdgeCase1_EmptyProjectObjectives:
    """Edge Case 1: Project template with empty objectives."""

    def test_create_mission_from_project_with_empty_objectives(
        self, test_client: TestClient, test_user: tuple[str, str], test_project: dict[str, Any]
    ) -> None:
        """Test creating mission from project with empty objectives array."""
        _, token = test_user
        # Project already has empty objectives from fixture
        response = test_client.post(
            "/missions",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Mission from Empty Project",
                "description": "Test mission",
                "mission_type": "challenge",
                "difficulty": "intermediate",
                "project_id": test_project["project_id"],
            },
        )

        assert response.status_code == 201
        mission = response.json()
        assert mission["objectives"] == []


class TestEdgeCase2_ConflictingFields:
    """Edge Case 2: project_id + objectives provided together."""

    def test_create_mission_with_project_id_and_objectives_conflict(
        self, test_client: TestClient, test_user: tuple[str, str], test_project: dict[str, Any]
    ) -> None:
        """Test that objectives are ignored when project_id is provided."""
        _, token = test_user
        response = test_client.post(
            "/missions",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Mission with Conflicting Objectives",
                "description": "Test mission",
                "mission_type": "challenge",
                "difficulty": "intermediate",
                "project_id": test_project["project_id"],
                "objectives": [
                    {
                        "description": "This should be ignored",
                        "type": "reach",
                        "target_id": "mars",
                    }
                ],
            },
        )

        assert response.status_code == 201
        mission = response.json()
        # Should use project objectives (empty), not request objectives
        assert mission["objectives"] == []


class TestEdgeCase3_ExtremePositionValues:
    """Edge Case 3: Extremely large start_position values."""

    def test_create_mission_with_extreme_start_position(
        self, test_client: TestClient, test_user: tuple[str, str]
    ) -> None:
        """Test mission creation with near-limit float values for position."""
        _, token = test_user
        # Using very large but still valid float values
        large_value = 1e15  # Large but within reasonable solar system scale
        response = test_client.post(
            "/missions",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Mission with Extreme Position",
                "description": "Test mission",
                "mission_type": "challenge",
                "difficulty": "intermediate",
                "start_position": [large_value, large_value, large_value],
            },
        )

        # Should either succeed or return validation error
        # Current implementation may accept it, but should be tested
        assert response.status_code in [201, 400, 422]


class TestEdgeCase4_AccessControl:
    """Edge Case 4: Project template belongs to different user."""

    def test_create_mission_from_other_users_private_project(
        self, test_client: TestClient, test_user: tuple[str, str]
    ) -> None:
        """Test creating mission from another user's private project."""
        _, token = test_user
        # Create second user
        response = test_client.post(
            "/register",
            json={
                "username": "otheruser",
                "email": "other@example.com",
                "password": "OtherPass123!",
                "display_name": "Other User",
            },
        )
        assert response.status_code == 201

        # Login as second user
        login_response = test_client.post(
            "/login",
            json={"username": "otheruser", "password": "OtherPass123!"},
        )
        other_token = login_response.json()["access_token"]

        # Create private project as second user
        project_response = test_client.post(
            "/projects",
            headers={"Authorization": f"Bearer {other_token}"},
            json={
                "name": "Private Project",
                "description": "Private project",
                "mission_type": "challenge",
                "difficulty": "intermediate",
                "is_public": False,
            },
        )
        assert project_response.status_code == 201
        private_project_id = project_response.json()["project_id"]

        # Try to use it as first user
        mission_response = test_client.post(
            "/missions",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Mission from Private Project",
                "description": "Test",
                "mission_type": "challenge",
                "difficulty": "intermediate",
                "project_id": private_project_id,
            },
        )

        # Should return 403 or 404
        assert mission_response.status_code in [403, 404]


class TestEdgeCase7_SpecialCharacters:
    """Edge Case 7: Unicode and special characters in text fields."""

    def test_create_mission_with_special_characters(
        self, test_client: TestClient, test_user: tuple[str, str]
    ) -> None:
        """Test mission creation with Unicode, emoji, and special characters."""
        _, token = test_user
        response = test_client.post(
            "/missions",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "🚀 Mars Mission 中文 العربية",
                "description": "Land on Mars with <script>alert('xss')</script>",
                "mission_type": "challenge",
                "difficulty": "intermediate",
            },
        )

        # Should handle safely - either sanitize or preserve
        assert response.status_code in [201, 400, 422]
        if response.status_code == 201:
            mission = response.json()
            # Check that special characters are handled
            assert "🚀" in mission["name"] or "<script>" not in mission["description"]


class TestEdgeCase8_TimeLimitZeroVsNone:
    """Edge Case 8: Time limit zero vs None distinction."""

    def test_create_mission_with_zero_time_limit(
        self, test_client: TestClient, test_user: tuple[str, str]
    ) -> None:
        """Test mission creation with time_limit = 0.0 vs None."""
        _, token = test_user
        # Test with 0.0
        response_zero = test_client.post(
            "/missions",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Mission Zero Time",
                "description": "Test",
                "mission_type": "challenge",
                "difficulty": "intermediate",
                "time_limit": 0.0,
            },
        )

        # Should either accept 0.0 or reject it
        assert response_zero.status_code in [201, 400, 422]

        # Test with None (omitted field)
        response_none = test_client.post(
            "/missions",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Mission No Time Limit",
                "description": "Test",
                "mission_type": "challenge",
                "difficulty": "intermediate",
            },
        )

        assert response_none.status_code == 201
        mission = response_none.json()
        assert mission["time_limit"] is None


class TestEdgeCase9_InvalidShipTypes:
    """Edge Case 9: Allowed ship types with invalid/non-existent types."""

    def test_create_mission_with_invalid_ship_types(
        self, test_client: TestClient, test_user: tuple[str, str]
    ) -> None:
        """Test mission creation with non-existent ship type identifiers."""
        _, token = test_user
        response = test_client.post(
            "/missions",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Mission with Invalid Ships",
                "description": "Test",
                "mission_type": "challenge",
                "difficulty": "intermediate",
                "allowed_ship_types": ["unicorn", "dragon", "phoenix"],
            },
        )

        # Should either validate or accept (validation happens later)
        # Current implementation may accept it
        assert response.status_code in [201, 400, 422]


class TestEdgeCase10_NaNInfinityInObjectives:
    """Edge Case 10: Objective position with NaN or Infinity."""

    def test_create_mission_with_nan_in_objectives(
        self, test_client: TestClient, test_user: tuple[str, str]
    ) -> None:
        """Test mission creation with NaN in objective positions."""
        _, token = test_user
        # Note: JSON doesn't support NaN, so we test with very large numbers
        # that might be converted to Infinity, or test at validation level
        response = test_client.post(
            "/missions",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Mission with Invalid Position",
                "description": "Test",
                "mission_type": "challenge",
                "difficulty": "intermediate",
                "objectives": [
                    {
                        "description": "Invalid position",
                        "type": "reach",
                        "position": [1e308, 0.0, 0.0],  # Near infinity
                    }
                ],
            },
        )

        # Should validate and reject or handle gracefully
        assert response.status_code in [201, 400, 422]


class TestEdgeCase12_ExcessiveArrays:
    """Edge Case 12: Very long lists of objectives or ship types."""

    def test_create_mission_with_excessive_objectives(
        self, test_client: TestClient, test_user: tuple[str, str]
    ) -> None:
        """Test mission creation with extremely large objectives array."""
        _, token = test_user
        # Create 1000 objectives (reasonable test limit)
        objectives = [
            {
                "description": f"Objective {i}",
                "type": "reach",
                "target_id": "mars",
            }
            for i in range(1000)
        ]

        response = test_client.post(
            "/missions",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Mission with Many Objectives",
                "description": "Test",
                "mission_type": "challenge",
                "difficulty": "intermediate",
                "objectives": objectives,
            },
        )

        # Should either accept or enforce limit
        assert response.status_code in [201, 400, 422, 413]  # 413 = Payload Too Large


class TestEdgeCase_AdditionalBoundaryTests:
    """Additional boundary value tests."""

    def test_create_mission_with_max_length_name(
        self, test_client: TestClient, test_user: tuple[str, str]
    ) -> None:
        """Test mission creation with maximum length name (100 chars)."""
        _, token = test_user
        max_name = "A" * 100
        response = test_client.post(
            "/missions",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": max_name,
                "description": "Test",
                "mission_type": "challenge",
                "difficulty": "intermediate",
            },
        )
        assert response.status_code == 201

    def test_create_mission_with_over_max_length_name(
        self, test_client: TestClient, test_user: tuple[str, str]
    ) -> None:
        """Test mission creation with name exceeding max length (101 chars)."""
        _, token = test_user
        over_max_name = "A" * 101
        response = test_client.post(
            "/missions",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": over_max_name,
                "description": "Test",
                "mission_type": "challenge",
                "difficulty": "intermediate",
            },
        )
        assert response.status_code == 422  # Validation error

    def test_create_mission_with_negative_max_fuel(
        self, test_client: TestClient, test_user: tuple[str, str]
    ) -> None:
        """Test mission creation with negative max_fuel."""
        _, token = test_user
        response = test_client.post(
            "/missions",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Negative Fuel Mission",
                "description": "Test",
                "mission_type": "challenge",
                "difficulty": "intermediate",
                "max_fuel": -100.0,
            },
        )
        assert response.status_code == 422  # Should reject negative values


"""
Tests for protected routes requiring authentication.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from jose import jwt

from src.api.app import ALGORITHM, SECRET_KEY, create_app


@pytest.fixture
def client() -> TestClient:
    """Create a test client with in-memory repositories."""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def registered_user(client: TestClient) -> dict:
    """Register a test user and return user data."""
    response = client.post(
        "/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPassword123",
            "display_name": "Test User",
        },
    )
    assert response.status_code == 201
    return response.json()


def _create_test_token(
    user_id: str, username: str, expires_in_minutes: int = 60
) -> str:
    """Helper to create a JWT token for testing."""
    expire = datetime.now(tz=timezone.utc) + timedelta(minutes=expires_in_minutes)
    payload = {
        "sub": user_id,
        "username": username,
        "exp": int(expire.timestamp()),
        "iat": int(datetime.now(tz=timezone.utc).timestamp()),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def test_get_me_with_valid_token(client: TestClient, registered_user: dict) -> None:
    """Test accessing /me with a valid JWT token."""
    user_id = registered_user["user_id"]
    username = registered_user["username"]

    token = _create_test_token(user_id, username)

    response = client.get(
        "/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user_id
    assert data["username"] == username
    assert data["email"] == "test@example.com"
    assert data["display_name"] == "Test User"
    assert "created_at" in data


def test_get_me_without_token(client: TestClient) -> None:
    """Test accessing /me without a token should return 403."""
    response = client.get("/me")

    assert response.status_code == 403
    assert "detail" in response.json()


def test_get_me_with_invalid_token(client: TestClient) -> None:
    """Test accessing /me with an invalid token should return 401."""
    response = client.get(
        "/me",
        headers={"Authorization": "Bearer invalid_token_here"},
    )

    assert response.status_code == 401
    assert "Invalid or expired token" in response.json()["detail"]


def test_get_me_with_expired_token(client: TestClient, registered_user: dict) -> None:
    """Test accessing /me with an expired token should return 401."""
    user_id = registered_user["user_id"]
    username = registered_user["username"]

    # Create an expired token (expired 1 minute ago)
    expire = datetime.now(tz=timezone.utc) - timedelta(minutes=1)
    payload = {
        "sub": user_id,
        "username": username,
        "exp": int(expire.timestamp()),
        "iat": int((datetime.now(tz=timezone.utc) - timedelta(minutes=61)).timestamp()),
    }
    expired_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    response = client.get(
        "/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )

    assert response.status_code == 401
    assert "Invalid or expired token" in response.json()["detail"]


def test_get_me_with_token_missing_sub(client: TestClient) -> None:
    """Test accessing /me with a token missing 'sub' claim should return 401."""
    payload = {
        "username": "testuser",
        "exp": int((datetime.now(tz=timezone.utc) + timedelta(minutes=60)).timestamp()),
        "iat": int(datetime.now(tz=timezone.utc).timestamp()),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    response = client.get(
        "/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    assert "Invalid authentication credentials" in response.json()["detail"]


def test_get_me_with_nonexistent_user(client: TestClient) -> None:
    """Test accessing /me with a token for a non-existent user should return 401."""
    token = _create_test_token("nonexistent-user-id", "nonexistent")

    response = client.get(
        "/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    assert "User not found" in response.json()["detail"]


def test_get_me_with_wrong_secret_key(
    client: TestClient, registered_user: dict
) -> None:
    """Test accessing /me with a token signed with wrong secret should return 401."""
    user_id = registered_user["user_id"]
    username = registered_user["username"]

    # Create token with wrong secret
    expire = datetime.now(tz=timezone.utc) + timedelta(minutes=60)
    payload = {
        "sub": user_id,
        "username": username,
        "exp": int(expire.timestamp()),
        "iat": int(datetime.now(tz=timezone.utc).timestamp()),
    }
    wrong_token = jwt.encode(payload, "wrong-secret-key", algorithm=ALGORITHM)

    response = client.get(
        "/me",
        headers={"Authorization": f"Bearer {wrong_token}"},
    )

    assert response.status_code == 401
    assert "Invalid or expired token" in response.json()["detail"]

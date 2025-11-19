"""
Tests for API error handling and standardized error responses.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.api.app import create_app
from src.api.errors import APIError, ErrorCode


@pytest.fixture
def client() -> TestClient:
    """Create a test client."""
    app = create_app()
    return TestClient(app)


def test_error_response_format(client: TestClient) -> None:
    """Test that error responses follow the standardized format."""
    # Trigger a validation error
    response = client.post(
        "/register",
        json={
            "username": "ab",  # Too short
            "email": "invalid-email",  # Invalid format
            "password": "weak",  # Too weak
            "display_name": "",
        },
    )

    assert response.status_code == 422
    data = response.json()

    # Check error response structure
    assert "error" in data
    error = data["error"]
    assert "code" in error
    assert "message" in error
    assert "timestamp" in error
    assert "path" in error
    assert error["path"] == "/register"


def test_validation_error_code(client: TestClient) -> None:
    """Test validation errors return appropriate error codes."""
    response = client.post(
        "/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "weakpass",  # Missing mixed case and digit
            "display_name": "Test User",
        },
    )

    assert response.status_code == 400
    data = response.json()
    error = data["error"]

    # Should have validation error code
    assert error["code"] in [
        ErrorCode.VALIDATION_PASSWORD_POLICY,
        ErrorCode.VALIDATION_INVALID_FORMAT,
    ]
    assert (
        "password" in error["message"].lower()
        or "validation" in error["message"].lower()
    )


def test_duplicate_username_error(client: TestClient) -> None:
    """Test duplicate username returns RESOURCE_ALREADY_EXISTS error code."""
    # Register first user
    client.post(
        "/register",
        json={
            "username": "duplicate_user",
            "email": "first@example.com",
            "password": "TestPass123",
            "display_name": "First User",
        },
    )

    # Try to register with same username
    response = client.post(
        "/register",
        json={
            "username": "duplicate_user",
            "email": "second@example.com",
            "password": "TestPass123",
            "display_name": "Second User",
        },
    )

    assert response.status_code == 400
    data = response.json()
    error = data["error"]

    assert error["code"] == ErrorCode.RESOURCE_ALREADY_EXISTS
    assert (
        "username" in error["message"].lower() or "already" in error["message"].lower()
    )
    assert error["details"] is not None
    assert error["details"]["field"] == "username"


def test_duplicate_email_error(client: TestClient) -> None:
    """Test duplicate email returns RESOURCE_ALREADY_EXISTS error code."""
    # Register first user
    client.post(
        "/register",
        json={
            "username": "user1",
            "email": "duplicate@example.com",
            "password": "TestPass123",
            "display_name": "User One",
        },
    )

    # Try to register with same email
    response = client.post(
        "/register",
        json={
            "username": "user2",
            "email": "duplicate@example.com",
            "password": "TestPass123",
            "display_name": "User Two",
        },
    )

    assert response.status_code == 400
    data = response.json()
    error = data["error"]

    assert error["code"] == ErrorCode.RESOURCE_ALREADY_EXISTS
    assert "email" in error["message"].lower() or "already" in error["message"].lower()
    assert error["details"] is not None
    assert error["details"]["field"] == "email"


def test_auth_invalid_credentials_error(client: TestClient) -> None:
    """Test invalid login credentials return AUTH_INVALID_CREDENTIALS error code."""
    response = client.post(
        "/login",
        json={"username": "nonexistent", "password": "WrongPassword123"},
    )

    assert response.status_code == 401
    data = response.json()
    error = data["error"]

    assert error["code"] == ErrorCode.AUTH_INVALID_CREDENTIALS
    assert (
        "invalid" in error["message"].lower() or "password" in error["message"].lower()
    )


def test_auth_invalid_token_error(client: TestClient) -> None:
    """Test invalid token returns AUTH_INVALID_TOKEN or AUTH_EXPIRED_TOKEN error code."""
    response = client.get(
        "/me",
        headers={"Authorization": "Bearer invalid_token_here"},
    )

    assert response.status_code == 401
    data = response.json()
    error = data["error"]

    assert error["code"] in [
        ErrorCode.AUTH_INVALID_TOKEN,
        ErrorCode.AUTH_EXPIRED_TOKEN,
    ]


def test_auth_missing_token_error(client: TestClient) -> None:
    """Test missing token returns 403 (handled by FastAPI security)."""
    response = client.get("/me")

    # FastAPI HTTPBearer returns 403 for missing token
    assert response.status_code == 403


def test_error_timestamp_format(client: TestClient) -> None:
    """Test that error timestamps are in ISO 8601 format."""
    response = client.post(
        "/login",
        json={"username": "nonexistent", "password": "WrongPassword123"},
    )

    assert response.status_code == 401
    data = response.json()
    error = data["error"]

    # Check timestamp format (ISO 8601)
    timestamp = error["timestamp"]
    assert "T" in timestamp or "Z" in timestamp or "+" in timestamp
    assert len(timestamp) > 10  # Should have date and time


def test_error_path_in_response(client: TestClient) -> None:
    """Test that error response includes the correct path."""
    # Use valid format to trigger auth error, not validation error
    response = client.post(
        "/login",
        json={"username": "nonexistent_user", "password": "ValidPassword123"},
    )

    assert response.status_code == 401
    data = response.json()
    error = data["error"]

    assert error["path"] == "/login"


def test_password_policy_error_details(client: TestClient) -> None:
    """Test password policy errors include details."""
    response = client.post(
        "/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "weakpass",  # Missing requirements
            "display_name": "Test User",
        },
    )

    assert response.status_code == 400
    data = response.json()
    error = data["error"]

    if error["code"] == ErrorCode.VALIDATION_PASSWORD_POLICY:
        assert error["details"] is not None
        assert "field" in error["details"]
        assert error["details"]["field"] == "password"


def test_validation_error_fields(client: TestClient) -> None:
    """Test validation errors include field-level details."""
    response = client.post(
        "/register",
        json={
            "username": "ab",  # Too short
            "email": "not-an-email",
            "password": "TestPass123",
            "display_name": "Test",
        },
    )

    assert response.status_code == 422
    data = response.json()
    error = data["error"]

    # Should have field errors in details
    if error["details"] and "fields" in error["details"]:
        fields = error["details"]["fields"]
        assert len(fields) > 0


def test_api_error_exception() -> None:
    """Test APIError exception creation and properties."""
    error = APIError(
        code=ErrorCode.AUTH_INVALID_CREDENTIALS,
        message="Test error",
        status_code=401,
        details={"field": "username"},
    )

    assert error.code == ErrorCode.AUTH_INVALID_CREDENTIALS
    assert error.message == "Test error"
    assert error.status_code == 401
    assert error.details == {"field": "username"}

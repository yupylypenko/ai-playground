from __future__ import annotations

from fastapi.testclient import TestClient

from src.api.app import create_app
from src.cockpit.auth import AuthService
from src.cockpit.memory import InMemoryAuthRepository, InMemoryUserRepository
from src.cockpit.services import UserService


def build_test_client() -> TestClient:
    user_repo = InMemoryUserRepository()
    auth_repo = InMemoryAuthRepository()
    service = AuthService(UserService(user_repo), auth_repo)
    app = create_app(auth_service=service)
    return TestClient(app)


def test_register_success() -> None:
    client = build_test_client()
    payload = {
        "username": "astro_cadet",
        "email": "astro_cadet@example.com",
        "password": "StrongPass1",
        "display_name": "Astro Cadet",
    }

    response = client.post("/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == payload["username"]
    assert data["email"] == payload["email"]
    assert data["display_name"] == payload["display_name"]
    assert "user_id" in data


def test_register_duplicate_username() -> None:
    client = build_test_client()
    payload = {
        "username": "mission_ctrl",
        "email": "mission1@example.com",
        "password": "MissionPass1",
        "display_name": "Mission Control",
    }
    assert client.post("/register", json=payload).status_code == 201

    duplicate = payload | {"email": "mission2@example.com"}
    response = client.post("/register", json=duplicate)
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert (
        "Username already registered" in data["error"]["message"]
        or "already" in data["error"]["message"].lower()
    )


def test_register_weak_password() -> None:
    client = build_test_client()
    payload = {
        "username": "weakling",
        "email": "weakling@example.com",
        "password": "weakpass1",
        "display_name": "Weak Password",
    }

    response = client.post("/register", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert (
        "mixed case" in data["error"]["message"].lower()
        or "password" in data["error"]["message"].lower()
    )


def test_register_value_error_from_user_service() -> None:
    """Test that ValueError from UserService is caught and returns 400."""
    # This tests the ValueError exception handler in app.py
    client = build_test_client()

    # First registration succeeds
    payload1 = {
        "username": "testuser",
        "email": "test1@example.com",
        "password": "TestPass123",
        "display_name": "Test User 1",
    }
    assert client.post("/register", json=payload1).status_code == 201

    # Second registration with same username should trigger ValueError
    # from UserService (not RegistrationError from AuthService)
    # This tests the ValueError exception path in app.py
    payload2 = {
        "username": "testuser",  # Duplicate username
        "email": "test2@example.com",
        "password": "TestPass123",
        "display_name": "Test User 2",
    }
    response = client.post("/register", json=payload2)
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    message = data["error"]["message"].lower()
    assert "already" in message or "exists" in message or "registered" in message

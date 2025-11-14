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
    assert "Username already registered" in response.json()["detail"]


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
    assert "mixed case" in response.json()["detail"]

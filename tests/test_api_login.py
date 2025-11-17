from __future__ import annotations

from fastapi.testclient import TestClient
from jose import jwt

from src.api.app import ALGORITHM, SECRET_KEY, create_app


def _client() -> TestClient:
    app = create_app()
    return TestClient(app)


def test_login_success() -> None:
    client = _client()
    # First, register a user
    reg = client.post(
        "/register",
        json={
            "username": "login_user",
            "email": "login_user@example.com",
            "password": "StrongPass1",
            "display_name": "Login User",
        },
    )
    assert reg.status_code == 201

    # Now login
    resp = client.post(
        "/login",
        json={"username": "login_user", "password": "StrongPass1"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data and data["token_type"] == "bearer"
    token = data["access_token"]
    claims = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert claims["username"] == "login_user"
    assert "sub" in claims


def test_login_invalid_password() -> None:
    client = _client()
    client.post(
        "/register",
        json={
            "username": "wrongpass",
            "email": "wrongpass@example.com",
            "password": "Correct1Pass",
            "display_name": "Wrong Pass",
        },
    )
    resp = client.post(
        "/login",
        json={"username": "wrongpass", "password": "incorrect"},
    )
    assert resp.status_code == 401
    assert "Invalid username or password" in resp.text


def test_login_unknown_user() -> None:
    client = _client()
    resp = client.post(
        "/login", json={"username": "no_such_user", "password": "Whatever1"}
    )
    assert resp.status_code == 401

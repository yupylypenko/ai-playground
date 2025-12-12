"""
Tests for object search API endpoints.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.api.app import create_app
from src.cockpit.memory import InMemoryObjectMetadataRepository
from src.cockpit.search import ObjectSearchService


@pytest.fixture
def client() -> TestClient:
    """Create a test client."""
    app = create_app()
    return TestClient(app)


class TestObjectSearchAPI:
    """Tests for object search API endpoints."""

    def test_search_objects_endpoint(self, client: TestClient) -> None:
        """Test POST /objects/search endpoint."""
        response = client.post(
            "/objects/search",
            json={"query": "mars", "limit": 10},
        )
        assert response.status_code == 200
        data = response.json()
        assert "objects" in data
        assert "total" in data
        assert len(data["objects"]) > 0

    def test_search_objects_by_type(self, client: TestClient) -> None:
        """Test searching objects by type."""
        response = client.post(
            "/objects/search",
            json={"object_type": "planet", "limit": 10},
        )
        assert response.status_code == 200
        data = response.json()
        assert all(obj["type"] == "planet" for obj in data["objects"])

    def test_get_object_details_endpoint(self, client: TestClient) -> None:
        """Test GET /objects/{object_id} endpoint."""
        response = client.get("/objects/earth")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Earth"
        assert data["object_id"] == "earth"
        assert data["type"] == "planet"

    def test_get_object_details_not_found(self, client: TestClient) -> None:
        """Test getting details for non-existent object."""
        response = client.get("/objects/nonexistent")
        assert response.status_code == 404
        data = response.json()
        assert "error" in data or "message" in data

    def test_compare_objects_endpoint(self, client: TestClient) -> None:
        """Test GET /objects/{id1}/compare/{id2} endpoint."""
        response = client.get("/objects/earth/compare/mars")
        assert response.status_code == 200
        data = response.json()
        assert "object_1" in data
        assert "object_2" in data
        assert "comparison" in data
        assert data["object_1"]["id"] == "earth"
        assert data["object_2"]["id"] == "mars"

    def test_compare_objects_not_found(self, client: TestClient) -> None:
        """Test comparing non-existent objects."""
        response = client.get("/objects/nonexistent1/compare/nonexistent2")
        assert response.status_code == 404

    def test_enrich_object_metadata_endpoint(self, client: TestClient) -> None:
        """Test POST /objects/{object_id}/enrich endpoint."""
        response = client.post("/objects/earth/enrich?use_external_api=false")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Earth"
        # Should have calculated properties
        assert "calculated_properties" in data or data.get("calculated_properties") is not None

    def test_detect_nearby_objects_endpoint(self, client: TestClient) -> None:
        """Test POST /objects/nearby endpoint."""
        response = client.post(
            "/objects/nearby",
            json={
                "position": [0.0, 0.0, 0.0],
                "max_distance": 1e15,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "objects" in data
        assert "position" in data
        assert "max_distance" in data


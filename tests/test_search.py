"""
Tests for object search service and API.
"""

from __future__ import annotations

import pytest

from src.cockpit.memory import InMemoryObjectMetadataRepository
from src.cockpit.search import ObjectSearchService
from src.simulator.solar_system import SolarSystem


class TestObjectSearchService:
    """Tests for ObjectSearchService."""

    def test_search_objects_by_name(self) -> None:
        """Test searching objects by name."""
        repo = InMemoryObjectMetadataRepository()
        service = ObjectSearchService(metadata_repository=repo)

        results = service.search_objects(query="mars")
        assert len(results) > 0
        assert any(obj.get("name", "").lower() == "mars" for obj in results)

    def test_search_objects_by_type(self) -> None:
        """Test searching objects by type."""
        repo = InMemoryObjectMetadataRepository()
        service = ObjectSearchService(metadata_repository=repo)

        results = service.search_objects(object_type="planet")
        assert len(results) > 0
        assert all(obj.get("type") == "planet" for obj in results)

    def test_search_objects_by_mass_range(self) -> None:
        """Test searching objects by mass range."""
        repo = InMemoryObjectMetadataRepository()
        service = ObjectSearchService(metadata_repository=repo)

        # Search for objects with mass between 1e23 and 1e25 kg
        results = service.search_objects(min_mass=1e23, max_mass=1e25)
        assert len(results) > 0
        for obj in results:
            mass = obj.get("mass", 0.0)
            assert 1e23 <= mass <= 1e25

    def test_search_objects_by_atmosphere(self) -> None:
        """Test searching objects by atmosphere presence."""
        repo = InMemoryObjectMetadataRepository()
        service = ObjectSearchService(metadata_repository=repo)

        results = service.search_objects(has_atmosphere=True)
        assert len(results) > 0
        assert all(obj.get("has_atmosphere") is True for obj in results)

    def test_get_object_details(self) -> None:
        """Test getting object details."""
        repo = InMemoryObjectMetadataRepository()
        service = ObjectSearchService(metadata_repository=repo)

        details = service.get_object_details("earth")
        assert details is not None
        assert details.get("name") == "Earth"
        assert details.get("object_id") == "earth"
        assert details.get("type") == "planet"

    def test_get_object_details_not_found(self) -> None:
        """Test getting details for non-existent object."""
        repo = InMemoryObjectMetadataRepository()
        service = ObjectSearchService(metadata_repository=repo)

        details = service.get_object_details("nonexistent")
        assert details is None

    def test_compare_objects(self) -> None:
        """Test comparing two objects."""
        repo = InMemoryObjectMetadataRepository()
        service = ObjectSearchService(metadata_repository=repo)

        comparison = service.compare_objects("earth", "mars")
        assert comparison is not None
        assert comparison["object_1"]["id"] == "earth"
        assert comparison["object_2"]["id"] == "mars"
        assert "comparison" in comparison
        assert "mass_ratio" in comparison["comparison"]
        assert "radius_ratio" in comparison["comparison"]

    def test_compare_objects_not_found(self) -> None:
        """Test comparing non-existent objects."""
        repo = InMemoryObjectMetadataRepository()
        service = ObjectSearchService(metadata_repository=repo)

        comparison = service.compare_objects("nonexistent1", "nonexistent2")
        assert comparison is None

    def test_enrich_object_metadata(self) -> None:
        """Test enriching object metadata."""
        repo = InMemoryObjectMetadataRepository()
        service = ObjectSearchService(metadata_repository=repo)

        enriched = service.enrich_object_metadata("earth", use_external_api=False)
        assert enriched is not None
        assert enriched.get("name") == "Earth"
        # Should have calculated properties
        assert "calculated_properties" in enriched

    def test_enrich_object_metadata_not_found(self) -> None:
        """Test enriching non-existent object."""
        repo = InMemoryObjectMetadataRepository()
        service = ObjectSearchService(metadata_repository=repo)

        enriched = service.enrich_object_metadata("nonexistent")
        assert enriched is None

    def test_detect_nearby_objects(self) -> None:
        """Test detecting nearby objects."""
        repo = InMemoryObjectMetadataRepository()
        solar_system = SolarSystem()
        service = ObjectSearchService(
            metadata_repository=repo, solar_system=solar_system
        )

        # Search near origin (should find sun)
        nearby = service.detect_nearby_objects((0.0, 0.0, 0.0), max_distance=1e15)
        assert len(nearby) > 0
        # Should include distance
        assert all("distance" in obj for obj in nearby)
        # Should be sorted by distance
        distances = [obj.get("distance", float("inf")) for obj in nearby]
        assert distances == sorted(distances)


class TestObjectMetadataRepository:
    """Tests for InMemoryObjectMetadataRepository."""

    def test_save_and_get_metadata(self) -> None:
        """Test saving and retrieving metadata."""
        repo = InMemoryObjectMetadataRepository()
        metadata = {
            "name": "Test Object",
            "type": "planet",
            "mass": 1e24,
        }
        repo.save_metadata("test-object", metadata)

        retrieved = repo.get_metadata("test-object")
        assert retrieved is not None
        assert retrieved["name"] == "Test Object"
        assert retrieved["type"] == "planet"

    def test_search_metadata(self) -> None:
        """Test searching metadata."""
        repo = InMemoryObjectMetadataRepository()
        results = repo.search_metadata(query="earth")
        assert len(results) > 0
        assert any("earth" in obj.get("name", "").lower() for obj in results)

    def test_list_all_metadata(self) -> None:
        """Test listing all metadata."""
        repo = InMemoryObjectMetadataRepository()
        all_metadata = repo.list_all_metadata()
        assert len(all_metadata) > 0

    def test_delete_metadata(self) -> None:
        """Test deleting metadata."""
        repo = InMemoryObjectMetadataRepository()
        # Save custom metadata
        repo.save_metadata("custom", {"name": "Custom"})
        assert repo.get_metadata("custom") is not None

        repo.delete_metadata("custom")
        assert repo.get_metadata("custom") is None


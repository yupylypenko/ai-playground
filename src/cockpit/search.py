"""
Object Search Service

Service for searching, comparing, and enriching celestial object metadata.
"""

from __future__ import annotations

import logging
from typing import Any

from src.cockpit.storage import ObjectMetadataRepository
from src.simulator.solar_system import CelestialBody, SolarSystem

logger = logging.getLogger(__name__)


class ObjectSearchService:
    """
    Service for object search, comparison, and enrichment operations.

    Coordinates object metadata operations with storage repositories and
    external APIs for enrichment.
    """

    def __init__(
        self,
        metadata_repository: ObjectMetadataRepository,
        solar_system: SolarSystem | None = None,
    ) -> None:
        """
        Initialize object search service.

        Args:
            metadata_repository: Object metadata repository implementation
            solar_system: Optional solar system instance for live object data
        """
        self.metadata_repository = metadata_repository
        self.solar_system = solar_system or SolarSystem()

    def search_objects(
        self,
        query: str | None = None,
        object_type: str | None = None,
        min_mass: float | None = None,
        max_mass: float | None = None,
        has_atmosphere: bool | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Search for objects by metadata criteria.

        Args:
            query: Text search query (searches name, description, etc.)
            object_type: Filter by type ("star", "planet", "moon", "asteroid")
            min_mass: Minimum mass in kg
            max_mass: Maximum mass in kg
            has_atmosphere: Filter by atmosphere presence
            limit: Maximum number of results

        Returns:
            List of matching object metadata dictionaries
        """
        return self.metadata_repository.search_metadata(
            query=query,
            object_type=object_type,
            min_mass=min_mass,
            max_mass=max_mass,
            has_atmosphere=has_atmosphere,
            limit=limit,
        )

    def get_object_details(self, object_id: str) -> dict[str, Any] | None:
        """
        Get detailed metadata for a specific object.

        Args:
            object_id: Unique object identifier

        Returns:
            Object metadata dictionary or None if not found
        """
        metadata = self.metadata_repository.get_metadata(object_id)
        if not metadata:
            return None

        # Add object_id to metadata
        result = metadata.copy()
        result["object_id"] = object_id

        # Enrich with live data from solar system if available
        body = self.solar_system.get_body(object_id)
        if body:
            result["live_data"] = {
                "position": {
                    "x": body.position.x,
                    "y": body.position.y,
                    "z": body.position.z,
                },
                "velocity": {
                    "x": body.velocity.x,
                    "y": body.velocity.y,
                    "z": body.velocity.z,
                },
                "surface_gravity": body.get_surface_gravity(),
            }

        return result

    def compare_objects(
        self, object_id_1: str, object_id_2: str
    ) -> dict[str, Any] | None:
        """
        Compare two objects and return comparison metrics.

        Args:
            object_id_1: First object identifier
            object_id_2: Second object identifier

        Returns:
            Comparison dictionary with metrics, or None if either object not found
        """
        obj1 = self.metadata_repository.get_metadata(object_id_1)
        obj2 = self.metadata_repository.get_metadata(object_id_2)

        if not obj1 or not obj2:
            return None

        mass1 = obj1.get("mass", 0.0)
        mass2 = obj2.get("mass", 0.0)
        radius1 = obj1.get("radius", 0.0)
        radius2 = obj2.get("radius", 0.0)
        temp1 = obj1.get("temperature", 0.0)
        temp2 = obj2.get("temperature", 0.0)

        return {
            "object_1": {
                "id": object_id_1,
                "name": obj1.get("name"),
                "type": obj1.get("type"),
            },
            "object_2": {
                "id": object_id_2,
                "name": obj2.get("name"),
                "type": obj2.get("type"),
            },
            "comparison": {
                "mass_ratio": mass1 / mass2 if mass2 > 0 else 0.0,
                "radius_ratio": radius1 / radius2 if radius2 > 0 else 0.0,
                "temperature_difference": abs(temp1 - temp2),
                "mass_difference": abs(mass1 - mass2),
                "radius_difference": abs(radius1 - radius2),
                "both_have_atmosphere": obj1.get("has_atmosphere", False)
                and obj2.get("has_atmosphere", False),
                "both_have_water": obj1.get("has_water", False)
                and obj2.get("has_water", False),
            },
        }

    def enrich_object_metadata(
        self, object_id: str, use_external_api: bool = False
    ) -> dict[str, Any] | None:
        """
        Enrich object metadata with additional information.

        Can fetch from external APIs (e.g., NASA) or enhance with
        calculated properties.

        Args:
            object_id: Unique object identifier
            use_external_api: Whether to fetch from external API

        Returns:
            Enriched metadata dictionary or None if object not found
        """
        metadata = self.metadata_repository.get_metadata(object_id)
        if not metadata:
            return None

        enriched = metadata.copy()
        enriched["object_id"] = object_id

        # Add calculated properties from metadata or live body data
        body = self.solar_system.get_body(object_id)
        if body:
            # Use live body data if available
            enriched["calculated_properties"] = {
                "surface_gravity": body.get_surface_gravity(),
                "volume": (4.0 / 3.0) * 3.14159 * (body.radius**3),
                "density": body.mass / ((4.0 / 3.0) * 3.14159 * (body.radius**3))
                if body.radius > 0
                else 0.0,
            }
        else:
            # Calculate from metadata if body not in solar system
            mass = metadata.get("mass", 0.0)
            radius = metadata.get("radius", 0.0)
            if radius > 0:
                G = 6.67430e-11  # Gravitational constant
                surface_gravity = (G * mass) / (radius**2)
                volume = (4.0 / 3.0) * 3.14159 * (radius**3)
                density = mass / volume if volume > 0 else 0.0
                enriched["calculated_properties"] = {
                    "surface_gravity": surface_gravity,
                    "volume": volume,
                    "density": density,
                }

        # Optionally fetch from external API
        if use_external_api:
            external_data = self._fetch_external_metadata(object_id)
            if external_data:
                enriched["external_data"] = external_data

        # Update stored metadata with enriched data
        self.metadata_repository.save_metadata(object_id, enriched)

        return enriched

    def _fetch_external_metadata(self, object_id: str) -> dict[str, Any] | None:
        """
        Fetch metadata from external API (e.g., NASA).

        Args:
            object_id: Unique object identifier

        Returns:
            External metadata dictionary or None if fetch fails
        """
        try:
            # Example: NASA Planetary Data System API
            # In a real implementation, this would call actual APIs
            # For now, return None to indicate no external data available
            logger.debug("External API fetch not implemented for %s", object_id)
            return None
        except Exception as exc:
            logger.warning("Failed to fetch external metadata for %s: %s", object_id, exc)
            return None

    def detect_nearby_objects(
        self, position: tuple[float, float, float], max_distance: float = 1e12
    ) -> list[dict[str, Any]]:
        """
        Detect objects near a given position.

        Args:
            position: Position (x, y, z) in meters
            max_distance: Maximum distance in meters to consider

        Returns:
            List of nearby objects with distance information
        """
        from src.simulator.types import Vector3D

        pos = Vector3D(position[0], position[1], position[2])
        nearby = []

        for body_id, body in self.solar_system.bodies.items():
            distance = (body.position - pos).magnitude()
            if distance <= max_distance:
                metadata = self.metadata_repository.get_metadata(body_id)
                if metadata:
                    nearby.append(
                        {
                            **metadata,
                            "object_id": body_id,
                            "distance": distance,
                            "position": {
                                "x": body.position.x,
                                "y": body.position.y,
                                "z": body.position.z,
                            },
                        }
                    )

        # Sort by distance
        nearby.sort(key=lambda x: x.get("distance", float("inf")))
        return nearby


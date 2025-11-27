"""
Physics Engine for Cosmic Flight Simulator

Contains core physics calculations including orbital mechanics,
thrust simulation, and momentum conservation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .types import Vector3D

if TYPE_CHECKING:
    from .asteroid import Asteroid
    from .solar_system import CelestialBody
    from .spacecraft import Spacecraft


class PhysicsEngine:
    """
    Physics engine for orbital mechanics and spacecraft dynamics.

    Handles gravitational calculations, thrust, momentum, fuel consumption,
    and multi-body gravitational interactions.

    Attributes:
        gravitational_constant: G constant (6.67430e-11 m³/kg/s²)

    Examples:
        >>> engine = PhysicsEngine()
        >>> force = engine.calculate_gravity(spacecraft, celestial_body)
    """

    def __init__(self) -> None:
        """Initialize physics engine."""
        self.gravitational_constant = 6.67430e-11  # m³/kg/s²

    def calculate_gravity(
        self, spacecraft: Spacecraft, celestial_body: CelestialBody
    ) -> Vector3D:
        """
        Calculate gravitational force on spacecraft.

        Args:
            spacecraft: Source spacecraft
            celestial_body: Source of gravity

        Returns:
            Gravitational force vector in Newtons
        """
        # Vector from celestial body to spacecraft
        r = spacecraft.position - celestial_body.position
        distance = r.magnitude()

        if distance == 0.0:
            return Vector3D(0.0, 0.0, 0.0)

        # Gravitational force magnitude: F = G * M * m / r²
        force_magnitude = (
            self.gravitational_constant
            * celestial_body.mass
            * spacecraft.get_current_mass()
            / (distance**2)
        )

        # Force direction (toward celestial body)
        force_direction = -r.normalize()

        return force_direction * force_magnitude

    def calculate_acceleration(self, force: Vector3D, mass: float) -> Vector3D:
        """
        Calculate acceleration from force (F=ma -> a=F/m).

        Args:
            force: Force vector in Newtons
            mass: Mass in kg

        Returns:
            Acceleration vector in m/s²
        """
        if mass == 0.0:
            return Vector3D(0.0, 0.0, 0.0)
        return force * (1.0 / mass)

    def check_collision(
        self, spacecraft: Spacecraft, asteroid: Asteroid, spacecraft_radius: float = 5.0
    ) -> bool:
        """
        Check if spacecraft is colliding with an asteroid.

        Args:
            spacecraft: Spacecraft to check
            asteroid: Asteroid to check against
            spacecraft_radius: Effective radius of spacecraft in meters

        Returns:
            True if collision detected
        """
        return asteroid.is_colliding_with(spacecraft.position, spacecraft_radius)

    def detect_nearby_asteroids(
        self,
        position: Vector3D,
        asteroids: list[Asteroid],
        detection_range: float = 1000.0,
    ) -> list[Asteroid]:
        """
        Detect asteroids within detection range.

        Args:
            position: Position to search from
            asteroids: List of asteroids to check
            detection_range: Maximum detection range in meters

        Returns:
            List of asteroids within range, sorted by distance
        """
        nearby = []
        for asteroid in asteroids:
            distance = asteroid.get_distance_to(position)
            if distance <= detection_range:
                nearby.append((distance, asteroid))

        # Sort by distance and return asteroids only
        nearby.sort(key=lambda x: x[0])
        return [asteroid for _, asteroid in nearby]

    def calculate_avoidance_vector(
        self, spacecraft: Spacecraft, asteroid: Asteroid
    ) -> Vector3D | None:
        """
        Calculate avoidance vector to evade asteroid collision.

        Args:
            spacecraft: Spacecraft to calculate avoidance for
            asteroid: Asteroid to avoid

        Returns:
            Avoidance direction vector (normalized), or None if no immediate threat
        """
        # Check if on collision course
        time_to_collision = asteroid.get_time_to_collision(
            spacecraft.position, spacecraft.velocity, 5.0
        )

        if time_to_collision is None or time_to_collision > 30.0:
            return None  # No immediate threat

        # Calculate avoidance direction (perpendicular to relative velocity)
        rel_pos = spacecraft.position - asteroid.position
        rel_vel = spacecraft.velocity - asteroid.velocity

        if rel_vel.magnitude() == 0.0:
            # If no relative velocity, move directly away
            return rel_pos.normalize()

        # Calculate perpendicular avoidance vector
        avoidance = rel_pos - (rel_pos.dot(rel_vel.normalize()) * rel_vel.normalize())
        if avoidance.magnitude() < 0.1:
            # If positions are aligned, use cross product
            up = Vector3D(0.0, 1.0, 0.0)
            avoidance = rel_vel.cross(up)
            if avoidance.magnitude() < 0.1:
                avoidance = rel_vel.cross(Vector3D(1.0, 0.0, 0.0))

        return avoidance.normalize()

    def __repr__(self) -> str:
        return "PhysicsEngine()"

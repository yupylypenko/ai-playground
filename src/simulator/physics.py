"""
Physics Engine for Cosmic Flight Simulator

Contains core physics calculations including orbital mechanics,
thrust simulation, and momentum conservation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .types import Vector3D

if TYPE_CHECKING:
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

    def __repr__(self) -> str:
        return "PhysicsEngine()"

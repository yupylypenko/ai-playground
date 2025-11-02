"""
Solar System Data and Celestial Bodies

Defines planets, moons, and other celestial bodies for navigation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .types import Vector3D


@dataclass
class CelestialBody:
    """
    Planetary body with physical and orbital properties.

    Represents planets, moons, stars, and other astronomical objects
    with gravitational fields, orbital mechanics, and atmospheric properties.

    Attributes:
        id: Unique identifier (e.g., "earth", "mars")
        name: Common name
        type: "star", "planet", "moon", "asteroid"
        mass: Mass in kg
        radius: Radius in meters
        atmosphere_pressure: Surface pressure in kPa
        atmosphere_depth: Atmospheric height in meters
        temperature: Surface temperature in Kelvin
        has_atmosphere: Atmosphere flag
        has_water: Surface water flag
        parent_id: Parent body (None for Sun)
        semi_major_axis: Semi-major axis in meters
        eccentricity: Eccentricity 0-1
        inclination: Inclination in radians
        orbital_period: Period in seconds
        rotation_period: Sidereal day in seconds
        orbital_velocity: Mean velocity in m/s
        position: Current position
        velocity: Current velocity

    Examples:
        >>> earth = CelestialBody(
        ...     id="earth",
        ...     name="Earth",
        ...     type="planet",
        ...     mass=5.972e24,
        ...     radius=6.371e6
        ... )
        >>> gravity = earth.get_surface_gravity()
    """

    # Identity
    id: str
    name: str
    type: str  # "star", "planet", "moon", "asteroid"

    # Physical Properties
    mass: float  # kg
    radius: float  # meters
    atmosphere_pressure: float  # kPa
    atmosphere_depth: float  # meters
    temperature: float  # Kelvin
    has_atmosphere: bool
    has_water: bool

    # Orbital Mechanics
    parent_id: Optional[str] = None  # None for Sun
    semi_major_axis: float = 0.0  # meters
    eccentricity: float = 0.0  # 0-1
    inclination: float = 0.0  # radians
    orbital_period: float = 0.0  # seconds
    rotation_period: float = 0.0  # seconds
    orbital_velocity: float = 0.0  # m/s
    position: Vector3D = None
    velocity: Vector3D = None

    def __post_init__(self) -> None:
        """Initialize position and velocity if not provided."""
        if self.position is None:
            self.position = Vector3D(0.0, 0.0, 0.0)
        if self.velocity is None:
            self.velocity = Vector3D(0.0, 0.0, 0.0)

    def get_surface_gravity(self) -> float:
        """
        Calculate surface gravity in m/s².

        Returns:
            Surface gravity acceleration in m/s²
        """
        G = 6.67430e-11  # Gravitational constant
        if self.radius == 0.0:
            return 0.0
        return (G * self.mass) / (self.radius**2)

    def is_in_atmosphere(self, position: Vector3D) -> bool:
        """
        Check if position is within atmosphere.

        Args:
            position: Position to check

        Returns:
            True if within atmosphere
        """
        if not self.has_atmosphere:
            return False
        distance = (position - self.position).magnitude()
        return distance <= (self.radius + self.atmosphere_depth)

    def get_distance_to_surface(self, position: Vector3D) -> float:
        """
        Calculate distance from position to surface.

        Args:
            position: Position to check

        Returns:
            Distance in meters (negative if below surface)
        """
        distance = (position - self.position).magnitude()
        return distance - self.radius

    def __repr__(self) -> str:
        return f"CelestialBody(id='{self.id}', name='{self.name}', type='{self.type}')"


class SolarSystem:
    """
    Solar system containing all celestial bodies.

    Manages the collection of planets, moons, and other astronomical objects
    in the simulation. Provides lookup and iteration capabilities.

    Attributes:
        bodies: Dictionary mapping body IDs to CelestialBody instances
        sun: Reference to the Sun

    Examples:
        >>> system = SolarSystem()
        >>> system.add_body(earth)
        >>> earth_ref = system.get_body("earth")
    """

    def __init__(self) -> None:
        """Initialize empty solar system."""
        self.bodies: dict[str, CelestialBody] = {}
        self.sun: Optional[CelestialBody] = None
        self._initialize_system()

    def _initialize_system(self) -> None:
        """Initialize the solar system with basic celestial bodies."""
        # Sun
        self.sun = CelestialBody(
            id="sun",
            name="Sun",
            type="star",
            mass=1.9891e30,  # kg
            radius=6.9634e8,  # meters
            atmosphere_pressure=0.0,
            atmosphere_depth=0.0,
            temperature=5778.0,  # Kelvin
            has_atmosphere=False,
            has_water=False,
        )
        self.bodies["sun"] = self.sun

        # TODO: Add planets, moons, asteroids

    def add_body(self, body: CelestialBody) -> None:
        """
        Add a celestial body to the system.

        Args:
            body: CelestialBody to add
        """
        self.bodies[body.id] = body

    def get_body(self, body_id: str) -> Optional[CelestialBody]:
        """
        Get a celestial body by ID.

        Args:
            body_id: ID of the body

        Returns:
            CelestialBody or None if not found
        """
        return self.bodies.get(body_id)

    def get_nearest_body(self, position: Vector3D) -> Optional[CelestialBody]:
        """
        Find the nearest celestial body to a position.

        Args:
            position: Position to search from

        Returns:
            Nearest CelestialBody or None if no bodies
        """
        if not self.bodies:
            return None

        nearest = None
        min_distance = float("inf")

        for body in self.bodies.values():
            distance = (position - body.position).magnitude()
            if distance < min_distance:
                min_distance = distance
                nearest = body

        return nearest

    def __repr__(self) -> str:
        return f"SolarSystem(bodies={len(self.bodies)})"

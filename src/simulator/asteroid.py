"""
Asteroid Models and Classes

Defines asteroid objects with physical properties for collision detection
and protection systems.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .types import Vector3D


@dataclass
class Asteroid:
    """
    Asteroid with physical properties for collision detection.

    Represents small to medium-sized asteroids that can pose collision risks
    to spacecraft. Includes size classification and velocity for trajectory
    calculations.

    Attributes:
        id: Unique identifier
        name: Display name
        position: Position in meters (x, y, z)
        velocity: Velocity in m/s (vx, vy, vz)
        radius: Radius in meters
        mass: Mass in kg
        size_category: "small" (< 10m), "medium" (10-100m), "large" (> 100m)
        is_destroyable: Whether asteroid can be destroyed by weapons
        is_hazardous: Whether asteroid poses collision risk

    Examples:
        >>> asteroid = Asteroid(
        ...     id="ast-001",
        ...     name="Asteroid Alpha",
        ...     position=Vector3D(1000.0, 0.0, 0.0),
        ...     velocity=Vector3D(0.0, 0.0, 0.0),
        ...     radius=5.0,
        ...     mass=1000.0
        ... )
        >>> is_small = asteroid.size_category == "small"
    """

    # Identity
    id: str
    name: str

    # Position & Motion
    position: Vector3D = field(default_factory=lambda: Vector3D(0.0, 0.0, 0.0))
    velocity: Vector3D = field(default_factory=lambda: Vector3D(0.0, 0.0, 0.0))

    # Physical Properties
    radius: float = 1.0  # meters
    mass: float = 100.0  # kg

    # Classification
    size_category: str = "small"  # "small", "medium", "large"
    is_destroyable: bool = True
    is_hazardous: bool = True

    def __post_init__(self) -> None:
        """Initialize size category based on radius."""
        if self.radius < 10.0:
            self.size_category = "small"
        elif self.radius < 100.0:
            self.size_category = "medium"
        else:
            self.size_category = "large"
            # Large asteroids are typically not destroyable
            self.is_destroyable = False

    def get_collision_radius(self) -> float:
        """
        Get effective collision radius (includes safety margin).

        Returns:
            Collision radius in meters
        """
        # Add 10% safety margin for collision detection
        return self.radius * 1.1

    def get_distance_to(self, position: Vector3D) -> float:
        """
        Calculate distance from asteroid to a position.

        Args:
            position: Position to measure distance to

        Returns:
            Distance in meters
        """
        return (self.position - position).magnitude()

    def is_colliding_with(self, position: Vector3D, radius: float) -> bool:
        """
        Check if asteroid is colliding with an object.

        Args:
            position: Object position
            radius: Object radius in meters

        Returns:
            True if collision detected
        """
        distance = self.get_distance_to(position)
        collision_distance = self.get_collision_radius() + radius
        return distance < collision_distance

    def get_time_to_collision(
        self, position: Vector3D, velocity: Vector3D, radius: float
    ) -> float | None:
        """
        Calculate time until potential collision.

        Args:
            position: Object position
            velocity: Object velocity in m/s
            radius: Object radius in meters

        Returns:
            Time to collision in seconds, or None if no collision course
        """
        # Relative position and velocity
        rel_pos = position - self.position
        rel_vel = velocity - self.velocity

        # If moving away, no collision
        if rel_pos.dot(rel_vel) > 0:
            return None

        # Solve quadratic equation for collision time
        # |rel_pos + t * rel_vel| = collision_radius
        a = rel_vel.dot(rel_vel)
        if a == 0.0:
            # No relative velocity
            distance = rel_pos.magnitude()
            collision_distance = self.get_collision_radius() + radius
            return 0.0 if distance < collision_distance else None

        b = 2.0 * rel_pos.dot(rel_vel)
        c = rel_pos.dot(rel_pos) - (self.get_collision_radius() + radius) ** 2

        discriminant = b * b - 4 * a * c
        if discriminant < 0:
            return None  # No collision

        t = (-b - (discriminant**0.5)) / (2 * a)
        return t if t >= 0 else None

    def __repr__(self) -> str:
        return (
            f"Asteroid(id='{self.id}', name='{self.name}', "
            f"size='{self.size_category}', radius={self.radius:.1f}m)"
        )

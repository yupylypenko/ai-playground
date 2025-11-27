"""
Asteroid Protection System

Handles automatic avoidance and destruction of asteroids to protect spacecraft.
Implements both avoidance (navigation) and destruction (weapons) systems.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.simulator.asteroid import Asteroid
    from src.simulator.physics import PhysicsEngine
    from src.simulator.spacecraft import Spacecraft
    from src.simulator.types import Vector3D


class ProtectionMode(Enum):
    """Protection system operating mode."""

    OFF = "off"
    AVOIDANCE_ONLY = "avoidance_only"
    DESTROY_ONLY = "destroy_only"
    AUTO = "auto"  # Automatically choose best method


@dataclass
class ProtectionStatus:
    """
    Status of asteroid protection system.

    Attributes:
        mode: Current protection mode
        active_threats: Number of asteroids on collision course
        avoidance_active: Whether avoidance is currently active
        weapons_ready: Whether weapons are ready to fire
        last_avoidance_time: Time since last avoidance maneuver
        asteroids_destroyed: Count of asteroids destroyed
    """

    mode: ProtectionMode = ProtectionMode.OFF
    active_threats: int = 0
    avoidance_active: bool = False
    weapons_ready: bool = False
    last_avoidance_time: float = 0.0
    asteroids_destroyed: int = 0


class AsteroidProtectionSystem:
    """
    Asteroid protection system for spacecraft.

    Provides automatic collision avoidance and asteroid destruction capabilities.
    Can operate in different modes: avoidance only, destroy only, or automatic
    selection based on threat assessment.

    Attributes:
        physics_engine: Physics engine for collision detection
        detection_range: Maximum detection range in meters
        avoidance_threshold: Time threshold for avoidance in seconds
        weapon_range: Maximum weapon range in meters
        weapon_cooldown: Time between weapon shots in seconds

    Examples:
        >>> protection = AsteroidProtectionSystem(physics_engine)
        >>> protection.set_mode(ProtectionMode.AUTO)
        >>> status = protection.update(spacecraft, asteroids, delta_time)
    """

    def __init__(
        self,
        physics_engine: PhysicsEngine,
        detection_range: float = 2000.0,
        avoidance_threshold: float = 10.0,
        weapon_range: float = 500.0,
        weapon_cooldown: float = 1.0,
    ) -> None:
        """
        Initialize protection system.

        Args:
            physics_engine: Physics engine instance
            detection_range: Maximum detection range in meters
            avoidance_threshold: Time threshold for avoidance in seconds
            weapon_range: Maximum weapon range in meters
            weapon_cooldown: Time between weapon shots in seconds
        """
        self.physics_engine = physics_engine
        self.detection_range = detection_range
        self.avoidance_threshold = avoidance_threshold
        self.weapon_range = weapon_range
        self.weapon_cooldown = weapon_cooldown

        self.status = ProtectionStatus()
        self._weapon_cooldown_timer = 0.0
        self._threat_asteroids: list[Asteroid] = []

    def set_mode(self, mode: ProtectionMode) -> None:
        """
        Set protection system mode.

        Args:
            mode: Protection mode to activate
        """
        self.status.mode = mode

    def update(
        self, spacecraft: Spacecraft, asteroids: list[Asteroid], delta_time: float
    ) -> ProtectionStatus:
        """
        Update protection system and handle threats.

        Args:
            spacecraft: Spacecraft to protect
            asteroids: List of asteroids in the area
            delta_time: Time elapsed since last update in seconds

        Returns:
            Updated protection status
        """
        # Update cooldown timer
        self._weapon_cooldown_timer = max(0.0, self._weapon_cooldown_timer - delta_time)
        self.status.weapons_ready = self._weapon_cooldown_timer <= 0.0

        if self.status.mode == ProtectionMode.OFF:
            self.status.active_threats = 0
            self.status.avoidance_active = False
            return self.status

        # Detect nearby asteroids
        nearby = self.physics_engine.detect_nearby_asteroids(
            spacecraft.position, asteroids, self.detection_range
        )

        # Identify threats (on collision course)
        self._threat_asteroids = []
        for asteroid in nearby:
            time_to_collision = asteroid.get_time_to_collision(
                spacecraft.position, spacecraft.velocity, 5.0
            )
            if (
                time_to_collision is not None
                and time_to_collision <= self.avoidance_threshold
            ):
                self._threat_asteroids.append(asteroid)

        self.status.active_threats = len(self._threat_asteroids)

        # Handle threats based on mode
        if self.status.mode == ProtectionMode.AVOIDANCE_ONLY:
            self._handle_avoidance(spacecraft)
        elif self.status.mode == ProtectionMode.DESTROY_ONLY:
            self._handle_destruction(spacecraft, delta_time)
        elif self.status.mode == ProtectionMode.AUTO:
            self._handle_auto(spacecraft, delta_time)

        return self.status

    def _handle_avoidance(self, spacecraft: Spacecraft) -> None:
        """Handle avoidance-only mode."""
        if not self._threat_asteroids:
            self.status.avoidance_active = False
            return

        # Get avoidance vector for nearest threat
        nearest = self._threat_asteroids[0]
        avoidance = self.physics_engine.calculate_avoidance_vector(spacecraft, nearest)

        if avoidance is not None:
            # Apply avoidance thrust
            self.status.avoidance_active = True
            # Note: Actual thrust application would be handled by controls system
            # This just indicates that avoidance is active

    def _handle_destruction(self, spacecraft: Spacecraft, delta_time: float) -> None:
        """Handle destruction-only mode."""
        if not self._threat_asteroids or not self.status.weapons_ready:
            return

        # Target nearest destroyable asteroid within weapon range
        for asteroid in self._threat_asteroids:
            distance = asteroid.get_distance_to(spacecraft.position)
            if distance <= self.weapon_range and asteroid.is_destroyable:
                self._fire_weapon(asteroid, delta_time)
                break

    def _handle_auto(self, spacecraft: Spacecraft, delta_time: float) -> None:
        """Handle automatic mode (choose best method)."""
        if not self._threat_asteroids:
            self.status.avoidance_active = False
            return

        # For each threat, decide: avoid or destroy
        for asteroid in self._threat_asteroids:
            distance = asteroid.get_distance_to(spacecraft.position)
            time_to_collision = asteroid.get_time_to_collision(
                spacecraft.position, spacecraft.velocity, 5.0
            )

            # Prefer destruction if:
            # - Asteroid is destroyable
            # - Within weapon range
            # - Weapons are ready
            # - Enough time before collision
            if (
                asteroid.is_destroyable
                and distance <= self.weapon_range
                and self.status.weapons_ready
                and time_to_collision is not None
                and time_to_collision > 2.0
            ):
                self._fire_weapon(asteroid, delta_time)
            else:
                # Use avoidance
                avoidance = self.physics_engine.calculate_avoidance_vector(
                    spacecraft, asteroid
                )
                if avoidance is not None:
                    self.status.avoidance_active = True

    def _fire_weapon(self, asteroid: Asteroid, delta_time: float) -> None:
        """
        Fire weapon at asteroid (marks for destruction).

        Args:
            asteroid: Asteroid to target
            delta_time: Time elapsed
        """
        if not self.status.weapons_ready:
            return

        # Mark asteroid as destroyed (in real implementation, this would
        # trigger destruction animation/effects and remove from simulation)
        # For now, we just track the count
        self.status.asteroids_destroyed += 1
        self._weapon_cooldown_timer = self.weapon_cooldown

    def get_avoidance_vector(self, spacecraft: Spacecraft) -> Vector3D | None:
        """
        Get current avoidance vector for spacecraft control.

        Args:
            spacecraft: Spacecraft to get avoidance for

        Returns:
            Avoidance direction vector, or None if no avoidance needed
        """
        if not self._threat_asteroids:
            return None

        nearest = self._threat_asteroids[0]
        return self.physics_engine.calculate_avoidance_vector(spacecraft, nearest)

    def get_target_asteroid(self) -> Asteroid | None:
        """
        Get currently targeted asteroid for destruction.

        Returns:
            Targeted asteroid, or None if no target
        """
        if not self._threat_asteroids or not self.status.weapons_ready:
            return None

        # Return nearest destroyable asteroid within range
        for asteroid in self._threat_asteroids:
            if asteroid.is_destroyable:
                return asteroid

        return None

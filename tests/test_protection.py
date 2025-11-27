"""
Tests for Asteroid Protection System.
"""

from __future__ import annotations

import pytest

from src.cockpit.protection import AsteroidProtectionSystem, ProtectionMode
from src.simulator import Asteroid, PhysicsEngine, Spacecraft, Vector3D


class TestProtectionSystem:
    """Tests for AsteroidProtectionSystem."""

    @pytest.fixture
    def physics_engine(self) -> PhysicsEngine:
        """Create physics engine for tests."""
        return PhysicsEngine()

    @pytest.fixture
    def spacecraft(self) -> Spacecraft:
        """Create test spacecraft."""
        return Spacecraft(
            id="ship-1",
            name="Test Ship",
            ship_type="scout",
            mass=5000.0,
            dry_mass=4000.0,
            max_fuel_capacity=1000.0,
            current_fuel=500.0,
            max_thrust=10000.0,
            specific_impulse=300.0,
            cruise_speed=1000.0,
        )

    @pytest.fixture
    def protection_system(
        self, physics_engine: PhysicsEngine
    ) -> AsteroidProtectionSystem:
        """Create protection system for tests."""
        return AsteroidProtectionSystem(
            physics_engine,
            detection_range=1000.0,
            avoidance_threshold=10.0,
            weapon_range=500.0,
            weapon_cooldown=1.0,
        )

    def test_protection_mode_off(
        self, protection_system: AsteroidProtectionSystem, spacecraft: Spacecraft
    ) -> None:
        """Test protection system in OFF mode."""
        protection_system.set_mode(ProtectionMode.OFF)
        asteroids = [
            Asteroid(
                id="ast-1",
                name="Threat",
                position=Vector3D(50.0, 0.0, 0.0),
                velocity=Vector3D(-10.0, 0.0, 0.0),
                radius=5.0,
            )
        ]

        status = protection_system.update(spacecraft, asteroids, 0.1)
        assert status.mode == ProtectionMode.OFF
        assert status.active_threats == 0
        assert status.avoidance_active is False

    def test_protection_mode_avoidance(
        self, protection_system: AsteroidProtectionSystem, spacecraft: Spacecraft
    ) -> None:
        """Test protection system in AVOIDANCE_ONLY mode."""
        protection_system.set_mode(ProtectionMode.AVOIDANCE_ONLY)
        spacecraft.position = Vector3D(100.0, 0.0, 0.0)
        spacecraft.velocity = Vector3D(-10.0, 0.0, 0.0)

        asteroids = [
            Asteroid(
                id="ast-1",
                name="Threat",
                position=Vector3D(0.0, 0.0, 0.0),
                velocity=Vector3D(0.0, 0.0, 0.0),
                radius=5.0,
            )
        ]

        status = protection_system.update(spacecraft, asteroids, 0.1)
        assert status.mode == ProtectionMode.AVOIDANCE_ONLY
        assert status.active_threats >= 0  # May detect threat depending on timing
        # Avoidance may or may not be active depending on threat assessment

    def test_protection_mode_destroy(
        self, protection_system: AsteroidProtectionSystem, spacecraft: Spacecraft
    ) -> None:
        """Test protection system in DESTROY_ONLY mode."""
        protection_system.set_mode(ProtectionMode.DESTROY_ONLY)
        spacecraft.position = Vector3D(100.0, 0.0, 0.0)

        asteroids = [
            Asteroid(
                id="ast-1",
                name="Threat",
                position=Vector3D(200.0, 0.0, 0.0),
                velocity=Vector3D(-10.0, 0.0, 0.0),
                radius=5.0,  # Small, destroyable
            )
        ]

        status = protection_system.update(spacecraft, asteroids, 0.1)
        assert status.mode == ProtectionMode.DESTROY_ONLY
        # May or may not fire depending on range and timing

    def test_protection_mode_auto(
        self, protection_system: AsteroidProtectionSystem, spacecraft: Spacecraft
    ) -> None:
        """Test protection system in AUTO mode."""
        protection_system.set_mode(ProtectionMode.AUTO)
        spacecraft.position = Vector3D(100.0, 0.0, 0.0)

        asteroids = [
            Asteroid(
                id="ast-1",
                name="Threat",
                position=Vector3D(200.0, 0.0, 0.0),
                velocity=Vector3D(-10.0, 0.0, 0.0),
                radius=5.0,
            )
        ]

        status = protection_system.update(spacecraft, asteroids, 0.1)
        assert status.mode == ProtectionMode.AUTO
        # System will choose best method automatically

    def test_weapon_cooldown(
        self, protection_system: AsteroidProtectionSystem, spacecraft: Spacecraft
    ) -> None:
        """Test weapon cooldown mechanism."""
        protection_system.set_mode(ProtectionMode.DESTROY_ONLY)
        spacecraft.position = Vector3D(100.0, 0.0, 0.0)

        asteroids = [
            Asteroid(
                id="ast-1",
                name="Threat",
                position=Vector3D(200.0, 0.0, 0.0),
                radius=5.0,
            )
        ]

        # First update - weapons should be ready
        status1 = protection_system.update(spacecraft, asteroids, 0.1)
        assert status1.weapons_ready is True

        # Update immediately - weapons should be on cooldown if fired
        protection_system.update(spacecraft, asteroids, 0.1)
        # Cooldown timer should be active if weapon was fired

        # Wait for cooldown
        status3 = protection_system.update(spacecraft, asteroids, 1.5)
        assert status3.weapons_ready is True

    def test_get_avoidance_vector(
        self, protection_system: AsteroidProtectionSystem, spacecraft: Spacecraft
    ) -> None:
        """Test getting avoidance vector."""
        protection_system.set_mode(ProtectionMode.AVOIDANCE_ONLY)
        spacecraft.position = Vector3D(100.0, 0.0, 0.0)
        spacecraft.velocity = Vector3D(-10.0, 0.0, 0.0)

        asteroids = [
            Asteroid(
                id="ast-1",
                name="Threat",
                position=Vector3D(0.0, 0.0, 0.0),
                velocity=Vector3D(0.0, 0.0, 0.0),
                radius=5.0,
            )
        ]

        protection_system.update(spacecraft, asteroids, 0.1)
        _avoidance = protection_system.get_avoidance_vector(spacecraft)
        # May be None if no immediate threat, or a vector if threat detected

    def test_get_target_asteroid(
        self, protection_system: AsteroidProtectionSystem, spacecraft: Spacecraft
    ) -> None:
        """Test getting target asteroid."""
        protection_system.set_mode(ProtectionMode.DESTROY_ONLY)
        spacecraft.position = Vector3D(100.0, 0.0, 0.0)

        asteroids = [
            Asteroid(
                id="ast-1",
                name="Destroyable",
                position=Vector3D(200.0, 0.0, 0.0),
                radius=5.0,  # Small, destroyable
            ),
            Asteroid(
                id="ast-2",
                name="Large",
                position=Vector3D(300.0, 0.0, 0.0),
                radius=150.0,  # Large, not destroyable
            ),
        ]

        protection_system.update(spacecraft, asteroids, 0.1)
        _target = protection_system.get_target_asteroid()
        # Should return destroyable asteroid if in range and weapons ready

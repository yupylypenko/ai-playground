"""
Tests for type definitions (Vector3D, Quaternion).
"""

from __future__ import annotations

import math

from src.simulator.types import Quaternion, Vector3D


class TestVector3D:
    """Tests for Vector3D."""

    def test_normalize_zero_magnitude(self) -> None:
        """Test normalizing a zero vector."""
        v = Vector3D(0.0, 0.0, 0.0)
        normalized = v.normalize()
        assert normalized.x == 0.0
        assert normalized.y == 0.0
        assert normalized.z == 0.0

    def test_vector_operations(self) -> None:
        """Test vector operations."""
        v1 = Vector3D(1.0, 2.0, 3.0)
        v2 = Vector3D(4.0, 5.0, 6.0)

        # Addition
        result = v1 + v2
        assert result.x == 5.0
        assert result.y == 7.0
        assert result.z == 9.0

        # Subtraction
        result = v1 - v2
        assert result.x == -3.0
        assert result.y == -3.0
        assert result.z == -3.0

        # Scalar multiplication
        result = v1 * 2.0
        assert result.x == 2.0
        assert result.y == 4.0
        assert result.z == 6.0

        # Right multiplication
        result = 2.0 * v1
        assert result.x == 2.0
        assert result.y == 4.0
        assert result.z == 6.0

        # Negation
        result = -v1
        assert result.x == -1.0
        assert result.y == -2.0
        assert result.z == -3.0

    def test_dot_product(self) -> None:
        """Test dot product calculation."""
        v1 = Vector3D(1.0, 2.0, 3.0)
        v2 = Vector3D(4.0, 5.0, 6.0)

        dot = v1.dot(v2)
        assert dot == 1.0 * 4.0 + 2.0 * 5.0 + 3.0 * 6.0
        assert dot == 32.0

    def test_cross_product(self) -> None:
        """Test cross product calculation."""
        v1 = Vector3D(1.0, 0.0, 0.0)
        v2 = Vector3D(0.0, 1.0, 0.0)

        cross = v1.cross(v2)
        assert abs(cross.x - 0.0) < 1e-10
        assert abs(cross.y - 0.0) < 1e-10
        assert abs(cross.z - 1.0) < 1e-10

    def test_magnitude(self) -> None:
        """Test magnitude calculation."""
        v = Vector3D(3.0, 4.0, 0.0)
        mag = v.magnitude()
        assert abs(mag - 5.0) < 1e-10

    def test_normalize(self) -> None:
        """Test vector normalization."""
        v = Vector3D(3.0, 4.0, 0.0)
        normalized = v.normalize()
        mag = normalized.magnitude()
        assert abs(mag - 1.0) < 1e-10

    def test_repr(self) -> None:
        """Test Vector3D string representation."""
        v = Vector3D(1.23, 4.56, 7.89)
        repr_str = repr(v)
        assert "Vector3D" in repr_str
        assert "1.23" in repr_str or "1.2" in repr_str


class TestQuaternion:
    """Tests for Quaternion."""

    def test_normalize_zero_magnitude(self) -> None:
        """Test normalizing a zero quaternion."""
        q = Quaternion(0.0, 0.0, 0.0, 0.0)
        normalized = q.normalize()
        assert normalized.w == 1.0
        assert normalized.x == 0.0
        assert normalized.y == 0.0
        assert normalized.z == 0.0

    def test_to_euler_identity(self) -> None:
        """Test converting identity quaternion to Euler angles."""
        q = Quaternion(1.0, 0.0, 0.0, 0.0)  # Identity
        pitch, yaw, roll = q.to_euler()
        assert abs(pitch) < 1e-10
        assert abs(yaw) < 1e-10
        assert abs(roll) < 1e-10

    def test_from_euler(self) -> None:
        """Test creating quaternion from Euler angles."""
        pitch = math.pi / 4  # 45 degrees
        yaw = math.pi / 6  # 30 degrees
        roll = math.pi / 3  # 60 degrees

        q = Quaternion.from_euler(pitch, yaw, roll)
        assert q.w is not None
        assert q.x is not None
        assert q.y is not None
        assert q.z is not None

        # Convert back and verify
        p2, y2, r2 = q.to_euler()
        assert abs(pitch - p2) < 1e-6
        assert abs(yaw - y2) < 1e-6
        assert abs(roll - r2) < 1e-6

    def test_normalize(self) -> None:
        """Test quaternion normalization."""
        q = Quaternion(2.0, 2.0, 2.0, 2.0)
        normalized = q.normalize()
        mag = math.sqrt(
            normalized.w**2 + normalized.x**2 + normalized.y**2 + normalized.z**2
        )
        assert abs(mag - 1.0) < 1e-10

    def test_repr(self) -> None:
        """Test Quaternion string representation."""
        q = Quaternion(1.0, 0.5, 0.3, 0.2)
        repr_str = repr(q)
        assert "Quaternion" in repr_str

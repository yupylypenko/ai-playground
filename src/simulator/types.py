"""
Type definitions and supporting data structures.

Contains Vector3D, Quaternion, and other foundational types used throughout
the simulator.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class Vector3D:
    """
    3D vector for position, velocity, and acceleration.

    Attributes:
        x: X component
        y: Y component
        z: Z component

    Examples:
        >>> v1 = Vector3D(1.0, 2.0, 3.0)
        >>> v2 = Vector3D(4.0, 5.0, 6.0)
        >>> v1 + v2
        Vector3D(x=5.0, y=7.0, z=9.0)
        >>> v1 * 2.0
        Vector3D(x=2.0, y=4.0, z=6.0)
    """

    x: float
    y: float
    z: float

    def magnitude(self) -> float:
        """Calculate vector magnitude (length)."""
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def normalize(self) -> Vector3D:
        """Return normalized vector (unit length)."""
        mag = self.magnitude()
        if mag == 0.0:
            return Vector3D(0.0, 0.0, 0.0)
        return Vector3D(self.x / mag, self.y / mag, self.z / mag)

    def dot(self, other: Vector3D) -> float:
        """Calculate dot product with another vector."""
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: Vector3D) -> Vector3D:
        """Calculate cross product with another vector."""
        return Vector3D(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def __add__(self, other: Vector3D) -> Vector3D:
        """Add two vectors."""
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: Vector3D) -> Vector3D:
        """Subtract two vectors."""
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: float) -> Vector3D:
        """Multiply vector by scalar."""
        return Vector3D(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar: float) -> Vector3D:
        """Right multiply by scalar."""
        return self.__mul__(scalar)

    def __neg__(self) -> Vector3D:
        """Negate vector."""
        return Vector3D(-self.x, -self.y, -self.z)

    def __repr__(self) -> str:
        return f"Vector3D(x={self.x:.2f}, y={self.y:.2f}, z={self.z:.2f})"


@dataclass
class Quaternion:
    """
    Quaternion for 3D rotation (orientation).

    Represents rotation using w, x, y, z components where w is the scalar
    part and (x, y, z) is the vector part.

    Attributes:
        w: Scalar part
        x: I component
        y: J component
        z: K component

    Examples:
        >>> q = Quaternion(1.0, 0.0, 0.0, 0.0)  # Identity rotation
        >>> pitch, yaw, roll = q.to_euler()
    """

    w: float  # scalar part
    x: float  # i component
    y: float  # j component
    z: float  # k component

    def to_euler(self) -> tuple[float, float, float]:
        """
        Convert to Euler angles (pitch, yaw, roll) in radians.

        Returns:
            Tuple of (pitch, yaw, roll) angles in radians
        """
        # Extract angles
        pitch = math.asin(2 * (self.w * self.y - self.z * self.x))
        yaw = math.atan2(
            2 * (self.w * self.z + self.x * self.y), 1 - 2 * (self.y**2 + self.z**2)
        )
        roll = math.atan2(
            2 * (self.w * self.x + self.y * self.z), 1 - 2 * (self.x**2 + self.y**2)
        )
        return pitch, yaw, roll

    @classmethod
    def from_euler(cls, pitch: float, yaw: float, roll: float) -> Quaternion:
        """
        Create quaternion from Euler angles.

        Args:
            pitch: Pitch angle in radians
            yaw: Yaw angle in radians
            roll: Roll angle in radians

        Returns:
            Quaternion representing the rotation
        """
        cy = math.cos(yaw * 0.5)
        sy = math.sin(yaw * 0.5)
        cp = math.cos(pitch * 0.5)
        sp = math.sin(pitch * 0.5)
        cr = math.cos(roll * 0.5)
        sr = math.sin(roll * 0.5)

        return Quaternion(
            w=cy * cp * cr + sy * sp * sr,
            x=cy * cp * sr - sy * sp * cr,
            y=sy * cp * sr + cy * sp * cr,
            z=sy * cp * cr - cy * sp * sr,
        )

    def normalize(self) -> Quaternion:
        """Normalize quaternion to unit length."""
        mag = math.sqrt(self.w**2 + self.x**2 + self.y**2 + self.z**2)
        if mag == 0.0:
            return Quaternion(1.0, 0.0, 0.0, 0.0)
        return Quaternion(self.w / mag, self.x / mag, self.y / mag, self.z / mag)

    def __repr__(self) -> str:
        return f"Quaternion(w={self.w:.3f}, x={self.x:.3f}, y={self.y:.3f}, z={self.z:.3f})"

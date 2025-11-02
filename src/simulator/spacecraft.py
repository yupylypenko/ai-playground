"""
Spacecraft Models and Classes

Defines spacecraft types and their characteristics, including state management.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from .types import Vector3D, Quaternion


@dataclass
class Spacecraft:
    """
    Spacecraft with physical properties and operational state.
    
    Represents a player's or AI-controlled spacecraft with attributes including
    position, orientation, fuel, thrust, and life support systems.
    
    Attributes:
        id: Unique identifier (UUID)
        name: Display name
        ship_type: Type: "scout", "freighter", "fighter"
        mass: Total mass in kg (dry + fuel)
        dry_mass: Mass without fuel in kg
        max_fuel_capacity: Maximum fuel in L
        current_fuel: Current fuel in L
        max_thrust: Maximum thrust in N
        specific_impulse: Isp in seconds
        cruise_speed: Cruising speed in m/s
        position: Position in meters (x, y, z)
        velocity: Velocity in m/s (vx, vy, vz)
        acceleration: Acceleration in m/s²
        orientation: Rotation quaternion
        angular_velocity: Angular speed in rad/s
        thrust_level: Current thrust 0.0-1.0
        thrust_vector: Thrust direction
        throttle: Throttle 0-100%
        boost_active: Boost mode enabled
        shields_active: Shield status
        hull_integrity: 0.0-1.0 (damage)
        oxygen_level: 0-100%
        cabin_pressure: kPa
        cabin_temp: Celsius
        life_support_status: "nominal", "warning", "critical"
    
    Examples:
        >>> ship = Spacecraft(
        ...     id="ship-001",
        ...     name="Explorer",
        ...     ship_type="scout",
        ...     mass=5000.0,
        ...     dry_mass=4000.0,
        ...     max_fuel_capacity=1000.0,
        ...     current_fuel=500.0
        ... )
        >>> fuel_percent = ship.get_fuel_percent()
    """
    
    # Identity
    id: str
    name: str
    ship_type: str  # "scout", "freighter", "fighter"
    
    # Mass & Propulsion
    mass: float  # kg
    dry_mass: float  # kg
    max_fuel_capacity: float  # L
    current_fuel: float  # L
    max_thrust: float  # N
    specific_impulse: float  # seconds
    cruise_speed: float  # m/s
    
    # Position & Orientation
    position: Vector3D = field(default_factory=lambda: Vector3D(0.0, 0.0, 0.0))
    velocity: Vector3D = field(default_factory=lambda: Vector3D(0.0, 0.0, 0.0))
    acceleration: Vector3D = field(default_factory=lambda: Vector3D(0.0, 0.0, 0.0))
    orientation: Quaternion = field(default_factory=lambda: Quaternion(1.0, 0.0, 0.0, 0.0))
    angular_velocity: Vector3D = field(default_factory=lambda: Vector3D(0.0, 0.0, 0.0))
    
    # Operational State
    thrust_level: float = 0.0  # 0.0-1.0
    thrust_vector: Vector3D = field(default_factory=lambda: Vector3D(1.0, 0.0, 0.0))
    throttle: float = 0.0  # 0-100%
    boost_active: bool = False
    shields_active: bool = False
    hull_integrity: float = 1.0  # 0.0-1.0
    
    # Life Support
    oxygen_level: float = 100.0  # 0-100%
    cabin_pressure: float = 101.3  # kPa
    cabin_temp: float = 20.0  # Celsius
    life_support_status: str = "nominal"  # "nominal", "warning", "critical"
    
    def get_current_mass(self) -> float:
        """
        Calculate total mass including fuel.
        
        Returns:
            Total mass in kg
        """
        # Assume fuel density of 0.75 kg/L (typical for liquid fuel)
        return self.dry_mass + (self.current_fuel * 0.75)
    
    def get_fuel_percent(self) -> float:
        """
        Get fuel as percentage.
        
        Returns:
            Fuel percentage (0-100)
        """
        if self.max_fuel_capacity == 0.0:
            return 0.0
        return (self.current_fuel / self.max_fuel_capacity) * 100.0
    
    def consume_fuel(self, delta_time: float) -> float:
        """
        Consume fuel based on thrust level and time.
        
        Args:
            delta_time: Time elapsed in seconds
        
        Returns:
            Fuel consumed in L
        """
        if self.thrust_level <= 0.0:
            return 0.0
        
        # Fuel consumption proportional to thrust level
        # Simplified model: max fuel consumption at max thrust
        fuel_per_second = (self.thrust_level * self.max_thrust) / (self.specific_impulse * 9.81)
        fuel_consumed = fuel_per_second * delta_time
        
        # Apply boost multiplier if active
        if self.boost_active:
            fuel_consumed *= 2.0
        
        # Cap at available fuel
        fuel_consumed = min(fuel_consumed, self.current_fuel)
        self.current_fuel -= fuel_consumed
        
        return fuel_consumed
    
    def update_life_support(self, delta_time: float) -> None:
        """
        Update life support systems based on time.
        
        Args:
            delta_time: Time elapsed in seconds
        """
        # Simple life support consumption model
        oxygen_consumption = 0.1 * delta_time  # 0.1% per second
        self.oxygen_level = max(0.0, self.oxygen_level - oxygen_consumption)
        
        # Update status based on oxygen level
        if self.oxygen_level > 50.0:
            self.life_support_status = "nominal"
        elif self.oxygen_level > 20.0:
            self.life_support_status = "warning"
        else:
            self.life_support_status = "critical"
    
    def set_throttle(self, percentage: float) -> None:
        """
        Set throttle level.
        
        Args:
            percentage: Throttle 0-100%
        """
        self.throttle = max(0.0, min(100.0, percentage))
        self.thrust_level = self.throttle / 100.0
    
    def __repr__(self) -> str:
        return f"Spacecraft(id='{self.id}', name='{self.name}', type='{self.ship_type}')"
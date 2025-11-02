# Data Structures

This document defines the core data structures for the Cosmic Flight Simulator.

## Overview

The simulator manages complex state through several key data structures:
- **Spacecraft**: Ship attributes, position, and state
- **CelestialBody**: Planetary bodies and their properties
- **Mission**: Objectives, parameters, and progression
- **User**: Profile and preferences

## 1. Spacecraft

Represents a player's or AI-controlled spacecraft with physical attributes, position, orientation, and operational state.

### Core Properties

| Property | Type | Description |
|----------|------|-------------|
| `id` | `str` | Unique identifier (UUID) |
| `name` | `str` | Display name |
| `ship_type` | `str` | Type: "scout", "freighter", "fighter" |
| `mass` | `float` | Total mass in kg |
| `dry_mass` | `float` | Mass without fuel in kg |
| `max_fuel_capacity` | `float` | Maximum fuel in L |
| `current_fuel` | `float` | Current fuel in L |
| `max_thrust` | `float` | Maximum thrust in N |
| `specific_impulse` | `float` | Isp in seconds |
| `cruise_speed` | `float` | Cruising speed in m/s |

### Position & Orientation

| Property | Type | Description |
|----------|------|-------------|
| `position` | `Vector3D` | Position in meters (x, y, z) |
| `velocity` | `Vector3D` | Velocity in m/s (vx, vy, vz) |
| `acceleration` | `Vector3D` | Acceleration in m/s² |
| `orientation` | `Quaternion` | Rotation (pitch, yaw, roll) |
| `angular_velocity` | `Vector3D` | Angular speed in rad/s |

### Operational State

| Property | Type | Description |
|----------|------|-------------|
| `thrust_level` | `float` | Current thrust 0.0-1.0 |
| `thrust_vector` | `Vector3D` | Thrust direction |
| `throttle` | `float` | Throttle 0-100% |
| `boost_active` | `bool` | Boost mode enabled |
| `shields_active` | `bool` | Shield status |
| `hull_integrity` | `float` | 0.0-1.0 (damage) |

### Life Support

| Property | Type | Description |
|----------|------|-------------|
| `oxygen_level` | `float` | 0-100% |
| `cabin_pressure` | `float` | kPa |
| `cabin_temp` | `float` | Celsius |
| `life_support_status` | `str` | "nominal", "warning", "critical" |

### Python Structure

```python
from dataclasses import dataclass
from typing import Optional
from .physics import Vector3D

@dataclass
class Spacecraft:
    """Spacecraft with physical properties and operational state."""
    
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
    position: Vector3D
    velocity: Vector3D
    acceleration: Vector3D
    orientation: Quaternion
    angular_velocity: Vector3D
    
    # Operational State
    thrust_level: float  # 0.0-1.0
    thrust_vector: Vector3D
    throttle: float  # 0-100%
    boost_active: bool
    shields_active: bool
    hull_integrity: float  # 0.0-1.0
    
    # Life Support
    oxygen_level: float  # 0-100%
    cabin_pressure: float  # kPa
    cabin_temp: float  # Celsius
    life_support_status: str
    
    def get_mass(self) -> float:
        """Calculate total mass including fuel."""
        return self.dry_mass + (self.current_fuel * 0.75)  # 0.75 kg/L
    
    def get_fuel_percent(self) -> float:
        """Get fuel as percentage."""
        return (self.current_fuel / self.max_fuel_capacity) * 100.0
```

## 2. CelestialBody

Represents planets, moons, stars, and other astronomical objects.

### Core Properties

| Property | Type | Description |
|----------|------|-------------|
| `id` | `str` | Unique identifier (e.g., "earth", "mars") |
| `name` | `str` | Common name |
| `type` | `str` | "star", "planet", "moon", "asteroid" |
| `mass` | `float` | Mass in kg |
| `radius` | `float` | Radius in meters |
| `atmosphere_pressure` | `float` | Surface pressure in kPa |
| `atmosphere_depth` | `float` | Atmospheric height in meters |
| `temperature` | `float` | Surface temperature in Kelvin |
| `has_atmosphere` | `bool` | Atmosphere flag |
| `has_water` | `bool` | Surface water flag |

### Orbital Mechanics

| Property | Type | Description |
|----------|------|-------------|
| `parent_id` | `Optional[str]` | Parent body (None for Sun) |
| `semi_major_axis` | `float` | A in meters |
| `eccentricity` | `float` | Eccentricity 0-1 |
| `inclination` | `float` | Inclination in radians |
| `orbital_period` | `float` | Period in seconds |
| `rotation_period` | `float` | Sidereal day in seconds |
| `orbital_velocity` | `float` | Mean velocity in m/s |
| `position` | `Vector3D` | Current position |
| `velocity` | `Vector3D` | Current velocity |

### Python Structure

```python
from dataclasses import dataclass
from typing import Optional
from .physics import Vector3D

@dataclass
class CelestialBody:
    """Planetary body with physical and orbital properties."""
    
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
    parent_id: Optional[str]  # None for Sun
    semi_major_axis: float  # meters
    eccentricity: float  # 0-1
    inclination: float  # radians
    orbital_period: float  # seconds
    rotation_period: float  # seconds
    orbital_velocity: float  # m/s
    position: Vector3D
    velocity: Vector3D
    
    def get_surface_gravity(self) -> float:
        """Calculate surface gravity in m/s²."""
        G = 6.67430e-11  # Gravitational constant
        return (G * self.mass) / (self.radius ** 2)
    
    def is_in_atmosphere(self, position: Vector3D) -> bool:
        """Check if position is within atmosphere."""
        if not self.has_atmosphere:
            return False
        distance = (position - self.position).magnitude()
        return distance <= (self.radius + self.atmosphere_depth)
```

## 3. Mission

Represents a mission with objectives, constraints, and progression tracking.

### Core Properties

| Property | Type | Description |
|----------|------|-------------|
| `id` | `str` | Unique identifier |
| `name` | `str` | Mission title |
| `type` | `str` | "tutorial", "free_flight", "challenge" |
| `difficulty` | `str` | "beginner", "intermediate", "advanced" |
| `description` | `str` | Brief description |
| `estimated_time` | `float` | Duration in seconds |
| `status` | `str` | "not_started", "in_progress", "completed", "failed" |

### Objectives

| Property | Type | Description |
|----------|------|-------------|
| `objectives` | `List[Objective]` | List of mission objectives |
| `current_objective_index` | `int` | Active objective (0-based) |
| `completion_criteria` | `dict` | Success conditions |

### Constraints & Setup

| Property | Type | Description |
|----------|------|-------------|
| `start_position` | `Vector3D` | Initial position |
| `target_body_id` | `Optional[str]` | Target celestial body |
| `max_fuel` | `float` | Starting fuel in L |
| `time_limit` | `Optional[float]` | Time limit in seconds |
| `allowed_ship_types` | `List[str]` | Permitted ship types |
| `failure_conditions` | `List[str]` | What causes failure |

### Tracking

| Property | Type | Description |
|----------|------|-------------|
| `start_time` | `Optional[float]` | Mission start timestamp |
| `elapsed_time` | `float` | Time since start |
| `distance_traveled` | `float` | Total distance in m |
| `fuel_consumed` | `float` | Fuel used in L |
| `objectives_completed` | `int` | Count of completed objectives |

### Python Structure

```python
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime
from .physics import Vector3D

@dataclass
class Objective:
    """Single mission objective."""
    id: str
    description: str
    type: str  # "reach", "collect", "maintain", "avoid"
    target_id: Optional[str] = None
    position: Optional[Vector3D] = None
    completed: bool = False

@dataclass
class Mission:
    """Mission with objectives, constraints, and tracking."""
    
    # Identity
    id: str
    name: str
    type: str  # "tutorial", "free_flight", "challenge"
    difficulty: str  # "beginner", "intermediate", "advanced"
    description: str
    
    # Objectives
    objectives: List[Objective] = field(default_factory=list)
    current_objective_index: int = 0
    completion_criteria: Dict[str, any] = field(default_factory=dict)
    
    # Constraints & Setup
    start_position: Vector3D = field(default_factory=Vector3D)
    target_body_id: Optional[str] = None
    max_fuel: float = 1000.0  # L
    time_limit: Optional[float] = None  # seconds
    allowed_ship_types: List[str] = field(default_factory=list)
    failure_conditions: List[str] = field(default_factory=list)
    
    # Tracking
    start_time: Optional[float] = None
    elapsed_time: float = 0.0
    distance_traveled: float = 0.0
    fuel_consumed: float = 0.0
    objectives_completed: int = 0
    
    # Status
    status: str = "not_started"  # "not_started", "in_progress", "completed", "failed"
    estimated_time: float = 3600.0  # seconds
    
    def start(self) -> None:
        """Start the mission."""
        self.start_time = datetime.now().timestamp()
        self.status = "in_progress"
    
    def complete_objective(self, objective_id: str) -> None:
        """Mark an objective as completed."""
        for obj in self.objectives:
            if obj.id == objective_id and not obj.completed:
                obj.completed = True
                self.objectives_completed += 1
                break
    
    def check_completion(self) -> bool:
        """Check if all objectives are completed."""
        return all(obj.completed for obj in self.objectives)
```

## 4. User

Represents user profile, preferences, and statistics.

### Identity

| Property | Type | Description |
|----------|------|-------------|
| `id` | `str` | Unique identifier (UUID) |
| `username` | `str` | Login username |
| `email` | `str` | Email address |
| `display_name` | `str` | Display name |

### Preferences

| Property | Type | Description |
|----------|------|-------------|
| `screen_width` | `int` | Display width |
| `screen_height` | `int` | Display height |
| `fullscreen` | `bool` | Fullscreen mode |
| `font_scale` | `float` | Text scaling 0.75-2.0 |
| `high_contrast` | `bool` | High contrast mode |
| `enable_sounds` | `bool` | Audio enabled |
| `master_volume` | `float` | 0.0-1.0 |
| `music_volume` | `float` | 0.0-1.0 |
| `sfx_volume` | `float` | 0.0-1.0 |

### Statistics

| Property | Type | Description |
|----------|------|-------------|
| `total_flight_time` | `float` | Total hours |
| `missions_completed` | `int` | Completed missions |
| `missions_attempted` | `int` | Total attempts |
| `distance_traveled` | `float` | Total distance in km |
| `fuel_consumed` | `float` | Total fuel in L |
| `ship_types_used` | `List[str]` | Unique ship types flown |

### Progression

| Property | Type | Description |
|----------|------|-------------|
| `unlocked_ships` | `List[str]` | Available ship IDs |
| `completed_missions` | `List[str]` | Completed mission IDs |
| `best_times` | `Dict[str, float]` | Best time per mission |
| `achievements` | `List[str]` | Earned achievement IDs |

### Python Structure

```python
from dataclasses import dataclass, field
from typing import List, Dict
from datetime import datetime

@dataclass
class User:
    """User profile with preferences and statistics."""
    
    # Identity
    id: str
    username: str
    email: str
    display_name: str
    
    # Preferences
    screen_width: int = 1280
    screen_height: int = 720
    fullscreen: bool = False
    font_scale: float = 1.0  # 0.75-2.0
    high_contrast: bool = False
    enable_sounds: bool = True
    master_volume: float = 0.8  # 0.0-1.0
    music_volume: float = 0.6  # 0.0-1.0
    sfx_volume: float = 0.8  # 0.0-1.0
    
    # Statistics
    total_flight_time: float = 0.0  # hours
    missions_completed: int = 0
    missions_attempted: int = 0
    distance_traveled: float = 0.0  # km
    fuel_consumed: float = 0.0  # L
    ship_types_used: List[str] = field(default_factory=list)
    
    # Progression
    unlocked_ships: List[str] = field(default_factory=list)
    completed_missions: List[str] = field(default_factory=list)
    best_times: Dict[str, float] = field(default_factory=dict)
    achievements: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    
    def update_statistics(
        self,
        flight_time: float,
        distance: float,
        fuel: float,
        ship_type: str
    ) -> None:
        """Update statistics after a flight session."""
        self.total_flight_time += flight_time
        self.distance_traveled += distance
        self.fuel_consumed += fuel
        if ship_type not in self.ship_types_used:
            self.ship_types_used.append(ship_type)
        self.last_login = datetime.now()
    
    def add_completed_mission(self, mission_id: str, time: float) -> None:
        """Record a completed mission."""
        if mission_id not in self.completed_missions:
            self.completed_missions.append(mission_id)
        self.missions_completed += 1
        if mission_id not in self.best_times or time < self.best_times[mission_id]:
            self.best_times[mission_id] = time
```

## Supporting Types

### Vector3D

```python
from dataclasses import dataclass
import math

@dataclass
class Vector3D:
    """3D vector for position, velocity, acceleration."""
    x: float
    y: float
    z: float
    
    def magnitude(self) -> float:
        """Calculate vector magnitude."""
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)
    
    def normalize(self) -> 'Vector3D':
        """Return normalized vector."""
        mag = self.magnitude()
        return Vector3D(self.x/mag, self.y/mag, self.z/mag) if mag > 0 else Vector3D(0,0,0)
    
    def __add__(self, other: 'Vector3D') -> 'Vector3D':
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other: 'Vector3D') -> 'Vector3D':
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar: float) -> 'Vector3D':
        return Vector3D(self.x * scalar, self.y * scalar, self.z * scalar)
```

### Quaternion

```python
from dataclasses import dataclass
import math

@dataclass
class Quaternion:
    """Quaternion for 3D rotation (orientation)."""
    w: float  # scalar part
    x: float  # i component
    y: float  # j component
    z: float  # k component
    
    def to_euler(self) -> tuple[float, float, float]:
        """Convert to Euler angles (pitch, yaw, roll) in radians."""
        # Extract angles
        pitch = math.asin(2 * (self.w * self.y - self.z * self.x))
        yaw = math.atan2(2 * (self.w * self.z + self.x * self.y),
                        1 - 2 * (self.y**2 + self.z**2))
        roll = math.atan2(2 * (self.w * self.x + self.y * self.z),
                        1 - 2 * (self.x**2 + self.y**2))
        return pitch, yaw, roll
```

## Data Relationships

```
User
 ├── Has many Missions (attempts/completions)
 ├── Has many Statistics (flight records)
 └── Has Preferences (settings)

Mission
 ├── Has many Objectives
 ├── References Target CelestialBody
 └── Tracks Spacecraft State

Spacecraft
 ├── At Position (relative to CelestialBody)
 ├── Has Orientation (Quaternion)
 └── Has Operational State

CelestialBody
 ├── Has Parent (orbital hierarchy)
 └── Has Orbital Parameters
```

## Future Considerations

- **Save System**: JSON serialization for User, Mission progress
- **Network State**: Multiplayer spacecraft position sync
- **Replay Data**: Record vector/state snapshots
- **Physics Cache**: Precomputed gravitational constants
- **Resource Limits**: Cargo, power, damage states

## References

- **Physics Units**: SI (meters, kg, seconds, Newtons)
- **Time**: Unix timestamps, seconds for durations
- **Angles**: Radians for internal calculations
- **Position**: Heliocentric coordinate system

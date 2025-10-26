# Cosmic Flight Simulator - Visual Diagrams

This document contains all PlantUML diagrams for the Cosmic Flight Simulator project.

## System Architecture Diagram

This diagram shows the overall system architecture with all modules and their relationships.

```plantuml
@startuml System Overview
!theme plain

package "Cosmic Flight Simulator" {
    
    package "User Interface Layer" {
        [User Input] as input
        [Cockpit View] as cockpit
        [HUD Display] as hud
    }
    
    package "Cockpit Module" {
        [Control Panel] as controls
        [Instrument Panel] as instruments
    }
    
    package "Simulator Module" {
        [Physics Engine] as physics
        [Spacecraft] as spacecraft
        [Solar System] as solar
    }
    
    package "Visualization Module" {
        [Renderer] as renderer
        [Camera] as camera
        [3D Models] as models
    }
    
    ' Data Flow
    input --> controls
    controls --> spacecraft
    spacecraft --> physics
    physics --> solar
    physics --> instruments
    instruments --> hud
    hud --> cockpit
    
    physics --> renderer
    solar --> renderer
    spacecraft --> renderer
    renderer --> camera
    camera --> cockpit
    models --> renderer
}

@enduml
```

## Class Diagram

This diagram defines the core classes and their relationships in the system.

```plantuml
@startuml Class Diagram
!theme plain
skinparam classAttributeIconSize 0

class PhysicsEngine {
    - current_time: float
    - gravitational_constant: float
    --
    + calculate_orbital_mechanics()
    + apply_thrust()
    + calculate_gravity()
    + update_fuel()
    + get_position()
}

class Spacecraft {
    - position: Vector3D
    - velocity: Vector3D
    - mass: float
    - fuel: float
    - thrust_power: float
    --
    + get_position() -> Vector3D
    + get_velocity() -> Vector3D
    + apply_thrust(thrust: Vector3D)
    + consume_fuel(amount: float)
    + get_status() -> dict
}

class CelestialBody {
    - name: str
    - mass: float
    - radius: float
    - position: Vector3D
    - orbital_period: float
    --
    + get_position(time: float) -> Vector3D
    + get_gravity_vector(target: Vector3D) -> Vector3D
    + is_in_atmosphere(position: Vector3D) -> bool
}

class ControlPanel {
    - keyboard_state: dict
    - mouse_state: dict
    --
    + get_thrust_input() -> Vector3D
    + get_rotation_input() -> Vector3D
    + get_boost() -> bool
}

class HUD {
    - font: Font
    - display_surface: Surface
    --
    + render_speed(speed: float)
    + render_altitude(altitude: float)
    + render_fuel(fuel: float)
    + render_targeting(target: Vector3D)
}

class Renderer {
    - window: Surface
    - camera: Camera
    --
    + initialize(width: int, height: int)
    + render_spacecraft(spacecraft: Spacecraft)
    + render_celestial_body(body: CelestialBody)
    + render_starfield()
    + update_frame()
}

class Camera {
    - position: Vector3D
    - target: Vector3D
    - view_mode: str
    --
    + set_view(mode: str)
    + update_position(position: Vector3D)
    + get_view_matrix() -> Matrix4x4
}

class SolarSystem {
    - bodies: list[CelestialBody]
    - time_acceleration: float
    --
    + add_body(body: CelestialBody)
    + update_simulation(delta_time: float)
    + get_all_bodies() -> list
}

' Relationships
PhysicsEngine --> Spacecraft : updates
PhysicsEngine --> CelestialBody : queries
SolarSystem --> CelestialBody : contains
ControlPanel --> Spacecraft : controls
HUD --> Spacecraft : displays
Renderer --> Camera : uses
Renderer --> Spacecraft : renders
Renderer --> CelestialBody : renders

@enduml
```

## Data Flow Sequence Diagram

This diagram shows the sequence of operations when a user interacts with the simulator.

```plantuml
@startuml Data Flow Sequence
!theme plain

actor User
participant ControlPanel
participant Spacecraft
participant PhysicsEngine
participant SolarSystem
participant HUD
participant Renderer
participant Camera

User -> ControlPanel: Input (WASD, Mouse)
ControlPanel -> Spacecraft: Apply Thrust/Rotation
Spacecraft -> PhysicsEngine: Request Physics Update
PhysicsEngine -> SolarSystem: Get Gravity Forces
SolarSystem --> PhysicsEngine: Return Gravity Vector
PhysicsEngine -> Spacecraft: Update Position/Velocity
Spacecraft -> HUD: Update Telemetry
HUD -> Renderer: Render Display
Renderer -> Camera: Get View Matrix
Camera --> Renderer: Return View Matrix
Renderer -> User: Render Frame to Screen

@enduml
```

## Component Interaction Diagram

This diagram shows how different components interact with each other during runtime.

```plantuml
@startuml Component Interaction
!theme plain

package CockpitModule {
    component ControlInput as control
    component HUDSystem as hud
    component Instruments as inst
}

package SimulatorModule {
    component PhysicsEngine as physics
    component Spacecraft as ship
    component SolarSystem as system
}

package VisualizationModule {
    component Renderer as renderer
    component Camera as camera
    component Models as models
}

control --> ship
ship --> physics
physics --> system
physics --> hud
hud --> renderer
ship --> renderer
system --> renderer
renderer --> camera
models --> renderer
renderer --> inst

note right of control
    User Commands
end note

note right of physics
    State Query
    Gravity Calculation
end note

note right of hud
    Telemetry Update
end note

note right of renderer
    Render Request
    Position Update
    Visual Feedback
end note

@enduml
```

## Deployment Diagram

This diagram shows the deployment architecture and technology stack.

```plantuml
@startuml Deployment
!theme plain

package "Development Machine" {
    [Python 3.8+] as python
    [NumPy] as numpy
    [Pygame] as pygame
    [PyOpenGL] as opengl
    package "Cosmic Flight Simulator" {
        [Simulator Module] as sim
        [Cockpit Module] as cock
        [Visualization Module] as vis
    }
}

python --> opengl
numpy --> opengl
pygame --> opengl
opengl --> sim
opengl --> cock
opengl --> vis

cloud "Assets" {
    [3D Models] as assets
    [Textures] as textures
    [Sound Effects] as sounds
}

opengl --> assets
opengl --> textures
opengl --> sounds

actor "User" as user
[Monitor] as screen
[Keyboard] as keyboard
[Mouse] as mouse

user --> keyboard
user --> mouse
keyboard --> opengl
mouse --> opengl
opengl --> screen

@enduml
```

## State Diagram for Mission Flow

This diagram shows the state transitions during mission execution.

```plantuml
@startuml Mission State
!theme plain
state "Mission Flow" as MissionFlow {
    [*] --> Initializing
    
    Initializing --> MainMenu : "System Ready"
    MainMenu --> Tutorial : "Start Tutorial"
    MainMenu --> FreeFlight : "Free Flight"
    MainMenu --> Challenge : "Challenge Mode"
    
    Tutorial --> FreeFlight : "Tutorial Complete"
    
    FreeFlight --> Docking : "Approach Station"
    FreeFlight --> Exploration : "Explore Planet"
    
    Docking --> FreeFlight : "Docking Complete"
    Exploration --> FreeFlight : "Exploration Done"
    
    Challenge --> MissionComplete : "Challenge Passed"
    MissionComplete --> MainMenu : "Return to Menu"
    
    FreeFlight --> Emergency : "System Failure"
    Emergency --> Crash : "Unrecoverable"
    Emergency --> FreeFlight : "Recovery Successful"
    
    Crash --> MainMenu : "Restart"
}

@enduml
```

## How to Use These Diagrams

### Prerequisites
To render these PlantUML diagrams, you need:
- Java Runtime Environment (JRE)
- PlantUML jar file
- Or use an online PlantUML renderer

### Online Rendering
1. Copy any diagram code block
2. Visit https://www.plantuml.com/plantuml/uml/
3. Paste the code
4. View the rendered diagram

### Local Rendering
```bash
# Install PlantUML
sudo apt-get install plantuml  # On Ubuntu/Debian

# Or download jar file
wget http://sourceforge.net/projects/plantuml/files/plantuml.jar

# Render diagram
java -jar plantuml.jar DIAGRAMS.md
```

### In VS Code
- Install "PlantUML" extension
- Open any `.puml` or `.md` file with PlantUML code
- Press `Alt+D` to preview
- Or use `Cmd+Shift+P` and select "PlantUML: Preview"

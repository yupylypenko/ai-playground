"""
Mock Configuration Generator

Generates realistic mock configuration data for the Cosmic Flight Simulator.
Supports JSON and .env-style output formats.
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Realistic solar system data
SOLAR_SYSTEM_BODIES = [
    {
        "id": "sun",
        "name": "Sun",
        "type": "star",
        "mass": 1.989e30,  # kg
        "radius": 6.96e8,  # meters
        "atmosphere_pressure": 0.0,
        "atmosphere_depth": 0.0,
        "temperature": 5778.0,  # K
        "has_atmosphere": False,
        "has_water": False,
    },
    {
        "id": "mercury",
        "name": "Mercury",
        "type": "planet",
        "mass": 3.301e23,
        "radius": 2.439e6,
        "atmosphere_pressure": 0.0,
        "atmosphere_depth": 0.0,
        "temperature": 440.0,
        "has_atmosphere": False,
        "has_water": False,
    },
    {
        "id": "venus",
        "name": "Venus",
        "type": "planet",
        "mass": 4.867e24,
        "radius": 6.052e6,
        "atmosphere_pressure": 9200.0,  # kPa
        "atmosphere_depth": 70000.0,
        "temperature": 737.0,
        "has_atmosphere": True,
        "has_water": False,
    },
    {
        "id": "earth",
        "name": "Earth",
        "type": "planet",
        "mass": 5.972e24,
        "radius": 6.371e6,
        "atmosphere_pressure": 101.3,  # kPa
        "atmosphere_depth": 100000.0,
        "temperature": 288.0,
        "has_atmosphere": True,
        "has_water": True,
    },
    {
        "id": "mars",
        "name": "Mars",
        "type": "planet",
        "mass": 6.39e23,
        "radius": 3.390e6,
        "atmosphere_pressure": 0.636,  # kPa
        "atmosphere_depth": 11000.0,
        "temperature": 210.0,
        "has_atmosphere": True,
        "has_water": True,
    },
    {
        "id": "jupiter",
        "name": "Jupiter",
        "type": "gas_giant",
        "mass": 1.898e27,
        "radius": 6.9911e7,
        "atmosphere_pressure": 100000.0,
        "atmosphere_depth": 500000.0,
        "temperature": 165.0,
        "has_atmosphere": True,
        "has_water": False,
    },
    {
        "id": "saturn",
        "name": "Saturn",
        "type": "gas_giant",
        "mass": 5.683e26,
        "radius": 5.8232e7,
        "atmosphere_pressure": 140000.0,
        "atmosphere_depth": 600000.0,
        "temperature": 134.0,
        "has_atmosphere": True,
        "has_water": False,
    },
    {
        "id": "titan",
        "name": "Titan",
        "type": "moon",
        "mass": 1.35e23,
        "radius": 2.575e6,
        "atmosphere_pressure": 146.7,
        "atmosphere_depth": 60000.0,
        "temperature": 93.7,
        "has_atmosphere": True,
        "has_water": True,
    },
    {
        "id": "europa",
        "name": "Europa",
        "type": "moon",
        "mass": 4.8e22,
        "radius": 1.561e6,
        "atmosphere_pressure": 0.0,
        "atmosphere_depth": 0.0,
        "temperature": 102.0,
        "has_atmosphere": False,
        "has_water": True,
    },
]

SPACECRAFT_TYPES = [
    {
        "id": "scout",
        "name": "Scout",
        "mass": 5000.0,  # kg
        "dry_mass": 4000.0,
        "max_fuel_capacity": 1000.0,  # L
        "max_thrust": 10000.0,  # N
        "specific_impulse": 300.0,  # seconds
        "cruise_speed": 1000.0,  # m/s
        "description": "Light reconnaissance vessel",
    },
    {
        "id": "freighter",
        "name": "Freighter",
        "mass": 50000.0,
        "dry_mass": 40000.0,
        "max_fuel_capacity": 10000.0,
        "max_thrust": 50000.0,
        "specific_impulse": 250.0,
        "cruise_speed": 500.0,
        "description": "Heavy cargo transport",
    },
    {
        "id": "fighter",
        "name": "Fighter",
        "mass": 3000.0,
        "dry_mass": 2500.0,
        "max_fuel_capacity": 500.0,
        "max_thrust": 15000.0,
        "specific_impulse": 350.0,
        "cruise_speed": 1500.0,
        "description": "Fast combat vessel",
    },
    {
        "id": "explorer",
        "name": "Explorer",
        "mass": 15000.0,
        "dry_mass": 12000.0,
        "max_fuel_capacity": 3000.0,
        "max_thrust": 20000.0,
        "specific_impulse": 400.0,
        "cruise_speed": 800.0,
        "description": "Long-range exploration vessel",
    },
]

MISSION_TYPES = [
    {
        "type": "tutorial",
        "difficulty": "beginner",
        "name_template": "Tutorial: {name}",
        "time_limit": 1800.0,  # 30 minutes
        "max_fuel": 500.0,
    },
    {
        "type": "free_flight",
        "difficulty": "beginner",
        "name_template": "Free Flight: {name}",
        "time_limit": None,
        "max_fuel": 1000.0,
    },
    {
        "type": "challenge",
        "difficulty": "intermediate",
        "name_template": "Challenge: {name}",
        "time_limit": 3600.0,  # 1 hour
        "max_fuel": 750.0,
    },
    {
        "type": "challenge",
        "difficulty": "advanced",
        "name_template": "Advanced: {name}",
        "time_limit": 7200.0,  # 2 hours
        "max_fuel": 500.0,
    },
]


def generate_user_config(count: int = 5) -> List[Dict[str, Any]]:
    """
    Generate mock user configurations.

    Args:
        count: Number of users to generate

    Returns:
        List of user configuration dictionaries
    """
    users = []
    usernames = [
        "space_pilot_01",
        "cosmic_explorer",
        "mars_rover",
        "jupiter_jumper",
        "stellar_navigator",
        "nebula_runner",
        "quasar_quest",
        "orbit_master",
    ]

    for i in range(count):
        username = usernames[i % len(usernames)] + (f"_{i}" if i >= len(usernames) else "")
        user = {
            "id": f"user-{uuid.uuid4().hex[:8]}",
            "username": username,
            "email": f"{username}@spaceflight.example",
            "display_name": username.replace("_", " ").title(),
            "screen_width": 1920 if i % 2 == 0 else 1280,
            "screen_height": 1080 if i % 2 == 0 else 720,
            "fullscreen": i % 3 == 0,
            "font_scale": 1.0 + (i % 3) * 0.25,
            "high_contrast": i % 4 == 0,
            "enable_sounds": True,
            "master_volume": 0.7 + (i % 3) * 0.1,
            "music_volume": 0.5 + (i % 3) * 0.1,
            "sfx_volume": 0.8 + (i % 2) * 0.1,
            "total_flight_time": float(i * 10.5),  # hours
            "missions_completed": i * 3,
            "missions_attempted": i * 3 + (i % 2),
            "distance_traveled": float(i * 50000.0),  # km
            "fuel_consumed": float(i * 5000.0),  # L
            "ship_types_used": ["scout", "fighter"] if i % 2 == 0 else ["scout"],
            "unlocked_ships": ["scout"] + (["fighter"] if i >= 2 else []),
            "completed_missions": [f"mission-{j:03d}" for j in range(i * 3)],
            "best_times": {
                f"mission-{j:03d}": float(300 + j * 50) for j in range(i * 3)
            },
            "achievements": ["first_flight", "mars_visitor"] if i >= 2 else ["first_flight"],
            "created_at": datetime.now().isoformat(),
            "last_login": datetime.now().isoformat(),
        }
        users.append(user)

    return users


def generate_mission_config(count: int = 10) -> List[Dict[str, Any]]:
    """
    Generate mock mission configurations.

    Args:
        count: Number of missions to generate

    Returns:
        List of mission configuration dictionaries
    """
    missions = []
    mission_names = [
        "First Steps",
        "Mars Approach",
        "Jupiter Flyby",
        "Titan Landing",
        "Europa Exploration",
        "Asteroid Mining",
        "Satellite Repair",
        "Deep Space Probe",
        "Orbital Rendezvous",
        "Emergency Rescue",
    ]

    objectives_templates = [
        [
            {"description": "Reach orbit", "type": "reach", "target_id": "earth"},
            {"description": "Maintain altitude", "type": "maintain", "target_id": "earth"},
        ],
        [
            {"description": "Navigate to Mars", "type": "reach", "target_id": "mars"},
            {"description": "Enter stable orbit", "type": "reach", "target_id": "mars"},
            {"description": "Collect samples", "type": "collect", "target_id": "mars"},
        ],
        [
            {"description": "Fly by Jupiter", "type": "reach", "target_id": "jupiter"},
            {"description": "Avoid radiation zones", "type": "avoid", "target_id": "jupiter"},
        ],
        [
            {"description": "Land on Titan", "type": "reach", "target_id": "titan"},
            {"description": "Survey surface", "type": "collect", "target_id": "titan"},
            {"description": "Return to orbit", "type": "reach", "target_id": "titan"},
        ],
    ]

    for i in range(count):
        mission_type_config = MISSION_TYPES[i % len(MISSION_TYPES)]
        mission_name = mission_names[i % len(mission_names)]
        objectives_template = objectives_templates[i % len(objectives_templates)]

        mission = {
            "id": f"mission-{i:03d}",
            "name": mission_type_config["name_template"].format(name=mission_name),
            "type": mission_type_config["type"],
            "difficulty": mission_type_config["difficulty"],
            "description": f"Complete the {mission_name.lower()} mission",
            "objectives": [
                {
                    "id": f"obj-{i:03d}-{j:02d}",
                    "description": obj["description"],
                    "type": obj["type"],
                    "target_id": obj.get("target_id"),
                    "completed": False,
                }
                for j, obj in enumerate(objectives_template)
            ],
            "current_objective_index": 0,
            "completion_criteria": {"all_objectives": True},
            "start_position": [0.0, 0.0, 0.0],
            "target_body_id": "mars" if i % 2 == 0 else "earth",
            "max_fuel": mission_type_config["max_fuel"],
            "time_limit": mission_type_config["time_limit"],
            "allowed_ship_types": ["scout", "fighter"] if i % 2 == 0 else ["scout"],
            "failure_conditions": ["fuel_depleted", "crash"],
            "status": "not_started",
            "estimated_time": 1800.0 + (i * 300.0),
        }
        missions.append(mission)

    return missions


def generate_solar_system_config() -> Dict[str, Any]:
    """
    Generate solar system configuration.

    Returns:
        Solar system configuration dictionary
    """
    return {
        "solar_system": {
            "name": "Sol System",
            "bodies": SOLAR_SYSTEM_BODIES,
        }
    }


def generate_spacecraft_config() -> Dict[str, Any]:
    """
    Generate spacecraft configuration.

    Returns:
        Spacecraft configuration dictionary
    """
    return {
        "spacecraft": {
            "types": SPACECRAFT_TYPES,
        }
    }


def generate_mongodb_config() -> Dict[str, Any]:
    """
    Generate MongoDB configuration.

    Returns:
        MongoDB configuration dictionary
    """
    return {
        "mongodb": {
            "host": "localhost",
            "port": 27017,
            "database": "cosmic_flight_sim",
            "username": None,
            "password": None,
        }
    }


def generate_game_config() -> Dict[str, Any]:
    """
    Generate game configuration.

    Returns:
        Game configuration dictionary
    """
    return {
        "game": {
            "name": "Cosmic Flight Simulator",
            "version": "1.0.0",
            "default_screen_width": 1280,
            "default_screen_height": 720,
            "default_fps": 60,
            "physics_time_step": 0.016,  # ~60 FPS
            "gravity_constant": 6.67430e-11,  # m³/kg/s²
            "speed_of_light": 299792458.0,  # m/s
        }
    }


def output_json(data: Dict[str, Any], output_file: Path, indent: int = 2) -> None:
    """
    Output data as JSON file.

    Args:
        data: Data to output
        output_file: Output file path
        indent: JSON indentation
    """
    with open(output_file, "w") as f:
        json.dump(data, f, indent=indent)
    print(f"✓ Generated JSON: {output_file}")


def output_env(data: Dict[str, Any], output_file: Path, prefix: str = "") -> None:
    """
    Output data as .env-style file.

    Args:
        data: Data to output
        output_file: Output file path
        prefix: Prefix for environment variable names
    """
    with open(output_file, "w") as f:
        f.write(f"# Generated mock configuration\n")
        f.write(f"# Generated at: {datetime.now().isoformat()}\n\n")

        def flatten_dict(d: Dict[str, Any], parent_key: str = "") -> List[tuple[str, str]]:
            """Flatten nested dictionary for .env format."""
            items: List[tuple[str, str]] = []
            for key, value in d.items():
                new_key = f"{parent_key}_{key}" if parent_key else key
                new_key = new_key.upper().replace("-", "_")
                if isinstance(value, dict):
                    items.extend(flatten_dict(value, new_key))
                elif isinstance(value, list):
                    # Store as JSON string for complex lists
                    items.append((new_key, json.dumps(value)))
                elif isinstance(value, bool):
                    items.append((new_key, str(value).lower()))
                elif value is None:
                    items.append((new_key, ""))
                else:
                    items.append((new_key, str(value)))
            return items

        if prefix:
            items = flatten_dict({prefix: data})
        else:
            items = flatten_dict(data)

        for key, value in items:
            if prefix:
                key = f"{prefix.upper()}_{key}"
            f.write(f"{key}={value}\n")

    print(f"✓ Generated .env file: {output_file}")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate mock configuration for Cosmic Flight Simulator"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="mock_config.json",
        help="Output file path (default: mock_config.json)",
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["json", "env", "both"],
        default="json",
        help="Output format: json, env, or both (default: json)",
    )
    parser.add_argument(
        "--users",
        type=int,
        default=5,
        help="Number of users to generate (default: 5)",
    )
    parser.add_argument(
        "--missions",
        type=int,
        default=10,
        help="Number of missions to generate (default: 10)",
    )
    parser.add_argument(
        "--include",
        choices=["all", "users", "missions", "system", "spacecraft", "game", "mongodb"],
        nargs="+",
        default=["all"],
        help="What to include in output (default: all)",
    )

    args = parser.parse_args()

    # Generate all configurations
    config: Dict[str, Any] = {}

    if "all" in args.include or "users" in args.include:
        config["users"] = generate_user_config(args.users)

    if "all" in args.include or "missions" in args.include:
        config["missions"] = generate_mission_config(args.missions)

    if "all" in args.include or "system" in args.include:
        config.update(generate_solar_system_config())

    if "all" in args.include or "spacecraft" in args.include:
        config.update(generate_spacecraft_config())

    if "all" in args.include or "game" in args.include:
        config.update(generate_game_config())

    if "all" in args.include or "mongodb" in args.include:
        config.update(generate_mongodb_config())

    # Output files
    output_path = Path(args.output)

    if args.format in ["json", "both"]:
        json_path = output_path.with_suffix(".json")
        output_json(config, json_path)

    if args.format in ["env", "both"]:
        env_path = output_path.with_suffix(".env")
        output_env(config, env_path)

    print(f"\n✓ Generated mock configuration with:")
    print(f"  - {len(config.get('users', []))} users")
    print(f"  - {len(config.get('missions', []))} missions")
    print(f"  - {len(config.get('solar_system', {}).get('bodies', []))} celestial bodies")
    print(f"  - {len(config.get('spacecraft', {}).get('types', []))} spacecraft types")

    return 0


if __name__ == "__main__":
    sys.exit(main())


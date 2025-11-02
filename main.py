"""
Cosmic Flight Simulator - Main Entry Point

Launches the cosmic flight simulator with specified configuration.

Usage:
    python main.py
    python main.py --mission "Mars Mission"
    python main.py --ship Scout
"""

from __future__ import annotations

import sys
import argparse
from typing import Optional

try:
    import pygame
except ImportError:
    pygame = None

# Import simulator modules
try:
    from src.simulator import (
        PhysicsEngine,
        Vector3D,
        Quaternion,
        Spacecraft,
        SolarSystem,
        CelestialBody,
    )
    from src.models import User, Mission, Objective
    from src.screens.main_menu import MainMenuScreen, MenuOption
    IMPORTS_OK = True
except ImportError as e:
    print(f"Import error: {e}")
    IMPORTS_OK = False


def test_data_structures() -> bool:
    """
    Test all data structures work together.
    
    Returns:
        True if all tests pass
    """
    print("Testing data structures...")
    
    try:
        # Test Vector3D
        v1 = Vector3D(1.0, 2.0, 3.0)
        v2 = Vector3D(4.0, 5.0, 6.0)
        v3 = v1 + v2
        assert v3.x == 5.0 and v3.y == 7.0 and v3.z == 9.0
        print("  ✓ Vector3D operations work")
        
        # Test Quaternion
        q = Quaternion.from_euler(0.0, 0.0, 0.0)
        pitch, yaw, roll = q.to_euler()
        assert abs(pitch) < 0.001 and abs(yaw) < 0.001 and abs(roll) < 0.001
        print("  ✓ Quaternion operations work")
        
        # Test Spacecraft
        ship = Spacecraft(
            id="test-ship",
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
        assert ship.get_fuel_percent() == 50.0
        assert ship.get_current_mass() > 4000.0
        print("  ✓ Spacecraft model works")
        
        # Test CelestialBody
        earth = CelestialBody(
            id="earth",
            name="Earth",
            type="planet",
            mass=5.972e24,
            radius=6.371e6,
            atmosphere_pressure=101.3,
            atmosphere_depth=100000.0,
            temperature=288.0,
            has_atmosphere=True,
            has_water=True,
        )
        gravity = earth.get_surface_gravity()
        assert 9.0 < gravity < 11.0  # Earth's gravity ~9.81 m/s²
        print("  ✓ CelestialBody model works")
        
        # Test SolarSystem
        system = SolarSystem()
        assert system.get_body("sun") is not None
        print("  ✓ SolarSystem works")
        
        # Test PhysicsEngine
        engine = PhysicsEngine()
        force = engine.calculate_gravity(ship, earth)
        assert isinstance(force, Vector3D)
        print("  ✓ PhysicsEngine works")
        
        # Test User
        user = User(
            id="user-001",
            username="testuser",
            email="test@example.com",
            display_name="Test User",
        )
        user.update_statistics(flight_time=1.0, distance=1000.0, fuel=50.0, ship_type="scout")
        assert user.total_flight_time == 1.0
        assert "scout" in user.ship_types_used
        print("  ✓ User model works")
        
        # Test Mission
        mission = Mission(
            id="mission-001",
            name="Test Mission",
            type="tutorial",
            difficulty="beginner",
            description="A test mission",
        )
        mission.start()
        assert mission.status == "in_progress"
        print("  ✓ Mission model works")
        
        # Test Objective
        obj = Objective(
            id="obj-001",
            description="Reach orbit",
            type="reach",
            target_id="earth",
        )
        mission.objectives.append(obj)
        mission.complete_objective("obj-001")
        assert mission.objectives_completed == 1
        print("  ✓ Objective model works")
        
        print("\n✓ All data structure tests passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_menu_test() -> None:
    """Run a basic menu test if pygame is available."""
    if not pygame:
        print("\nPygame not available, skipping menu test")
        return
    
    print("\nTesting main menu...")
    pygame.init()
    
    try:
        # Create a small window for testing
        screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Cosmic Flight Simulator - Test")
        
        # Create menu
        menu = MainMenuScreen(width=800, height=600)
        menu.start_fade_in()
        
        print("  ✓ Menu initialized")
        
        # Test basic rendering
        clock = pygame.time.Clock()
        running = True
        frames = 0
        max_frames = 60  # Run for ~1 second at 60 FPS
        
        while running and frames < max_frames:
            dt = clock.tick(60) / 1000.0  # Delta time in seconds
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEMOTION:
                    menu.handle_mouse_move(event.pos)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    selected = menu.handle_click(event.pos)
                    if selected:
                        print(f"  ✓ Menu option selected: {selected.value}")
            
            # Update transitions
            menu.update_transition(int(dt * 1000))
            
            # Render
            menu.render(screen)
            pygame.display.flip()
            
            frames += 1
        
        print("  ✓ Menu rendering works")
        print("  ✓ Menu interaction works")
        
    except Exception as e:
        print(f"  ✗ Menu test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Cosmic Flight Simulator")
    parser.add_argument(
        "--mission",
        type=str,
        help="Start with a specific mission",
    )
    parser.add_argument(
        "--ship",
        type=str,
        help="Use a specific ship type",
    )
    parser.add_argument(
        "--test-only",
        action="store_true",
        help="Run tests only, don't start full application",
    )
    args = parser.parse_args()
    
    print("=" * 60)
    print("Cosmic Flight Simulator")
    print("=" * 60)
    print()
    
    if not IMPORTS_OK:
        print("✗ Failed to import required modules")
        print("Please ensure all dependencies are installed:")
        print("  pip install -r requirements.txt")
        return 1
    
    print("✓ All imports successful")
    print()
    
    # Test data structures
    if not test_data_structures():
        print("\n✗ Data structure tests failed")
        return 1
    
    # Run menu test if requested or in test mode
    if args.test_only:
        run_menu_test()
        return 0
    
    # Full application launch (placeholder for future)
    print("\n🚀 Starting application...")
    print("🌌 Full simulator launch coming soon")
    print("\nNote: Currently only tests are implemented.")
    print("To test the menu, run: python main.py --test-only")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
"""
Heads-Up Display (HUD)

Displays real-time information overlay during flight.

TODO: Implement HUD rendering
TODO: Implement speed display
TODO: Implement orientation indicators
TODO: Implement targeting system
TODO: Implement navigation displays
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .protection import ProtectionStatus


def format_protection_status(status: ProtectionStatus) -> dict[str, str]:
    """
    Format protection status for HUD display.

    Args:
        status: Current protection status

    Returns:
        Dictionary with formatted status strings for display
    """
    mode_display = {
        "off": "OFF",
        "avoidance_only": "AVOID",
        "destroy_only": "DESTROY",
        "auto": "AUTO",
    }

    threat_level = "NONE"
    if status.active_threats > 0:
        if status.active_threats >= 3:
            threat_level = "CRITICAL"
        elif status.active_threats >= 2:
            threat_level = "HIGH"
        else:
            threat_level = "MODERATE"

    return {
        "mode": mode_display.get(status.mode.value, "UNKNOWN"),
        "threats": f"{status.active_threats}",
        "threat_level": threat_level,
        "avoidance": "ACTIVE" if status.avoidance_active else "INACTIVE",
        "weapons": "READY" if status.weapons_ready else "COOLDOWN",
        "destroyed": f"{status.asteroids_destroyed}",
    }


def get_asteroid_warning(status: ProtectionStatus) -> str | None:
    """
    Get asteroid warning message for HUD.

    Args:
        status: Current protection status

    Returns:
        Warning message string, or None if no warning
    """
    if status.active_threats == 0:
        return None

    if status.active_threats >= 3:
        return "⚠️ CRITICAL: Multiple asteroids on collision course!"
    elif status.active_threats >= 2:
        return "⚠️ WARNING: Multiple asteroids detected!"
    else:
        return "⚠️ CAUTION: Asteroid on collision course"

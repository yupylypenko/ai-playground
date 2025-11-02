"""
Cockpit Control System

Interactive cockpit with HUD, controls, and instruments.
"""

from .controls import ControlPanel
from .hud import HUD
from .instruments import InstrumentPanel

__all__ = ["ControlPanel", "HUD", "InstrumentPanel"]

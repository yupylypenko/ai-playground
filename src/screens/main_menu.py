"""
Main Menu Screen

The primary menu screen for the Cosmic Flight Simulator.
Provides navigation to missions, settings, and game modes.

TODO: Implement full screen rendering
TODO: Add button click handlers
TODO: Implement screen transitions
TODO: Add background animation/starfield
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

import pygame


class MenuOption(Enum):
    """Available menu options"""
    FREE_FLIGHT = "Free Flight"
    TUTORIAL = "Tutorial"
    MISSIONS = "Missions"
    SETTINGS = "Settings"
    QUIT = "Quit"


class MainMenuScreen:
    """
    Main menu screen for the Cosmic Flight Simulator.
    
    Displays menu options and handles user selection. Designed to respond
    within 0.1 seconds to user clicks per performance requirements.
    
    Attributes:
        width: Screen width in pixels
        height: Screen height in pixels
        selected_option: Currently selected menu option
        font: Font for rendering text
    """
    
    def __init__(self, width: int = 1280, height: int = 720) -> None:
        """
        Initialize the main menu screen.
        
        Args:
            width: Screen width in pixels
            height: Screen height in pixels
        """
        self.width = width
        self.height = height
        self.selected_option: Optional[MenuOption] = None
        self.font: Optional[pygame.font.Font] = None
        self.title_font: Optional[pygame.font.Font] = None
        self._initialize_fonts()
    
    def _initialize_fonts(self) -> None:
        """Initialize pygame fonts for menu rendering."""
        try:
            pygame.font.init()
            self.font = pygame.font.Font(None, 36)
            self.title_font = pygame.font.Font(None, 72)
        except Exception as e:
            print(f"Warning: Could not initialize fonts: {e}")
            self.font = None
            self.title_font = None
    
    def render(self, surface: pygame.Surface) -> None:
        """
        Render the main menu screen to the given surface.
        
        Args:
            surface: Pygame surface to render to
        """
        # Clear screen with dark space background
        surface.fill((5, 5, 15))
        
        if not self.font or not self.title_font:
            return
        
        # Render title
        title_text = self.title_font.render(
            "Cosmic Flight Simulator", 
            True, 
            (255, 255, 255)
        )
        title_rect = title_text.get_rect(center=(self.width // 2, 150))
        surface.blit(title_text, title_rect)
        
        # Render menu options
        menu_options = [
            MenuOption.FREE_FLIGHT,
            MenuOption.TUTORIAL,
            MenuOption.MISSIONS,
            MenuOption.SETTINGS,
            MenuOption.QUIT
        ]
        
        start_y = 350
        spacing = 60
        
        for i, option in enumerate(menu_options):
            y_pos = start_y + (i * spacing)
            
            # Highlight selected option
            color = (100, 200, 255) if option == self.selected_option else (200, 200, 200)
            
            option_text = self.font.render(option.value, True, color)
            option_rect = option_text.get_rect(center=(self.width // 2, y_pos))
            surface.blit(option_text, option_rect)
    
    def handle_click(self, pos: tuple[int, int]) -> Optional[MenuOption]:
        """
        Handle mouse click on the menu screen.
        
        Designed to respond within 0.1 seconds per performance requirements.
        
        Args:
            pos: Mouse position (x, y)
            
        Returns:
            Selected MenuOption if click was on a menu item, None otherwise
        """
        x, y = pos
        
        menu_options = [
            MenuOption.FREE_FLIGHT,
            MenuOption.TUTORIAL,
            MenuOption.MISSIONS,
            MenuOption.SETTINGS,
            MenuOption.QUIT
        ]
        
        start_y = 350
        spacing = 60
        option_width = 200
        option_height = 40
        
        for i, option in enumerate(menu_options):
            option_y = start_y + (i * spacing)
            
            # Check if click is within option bounds
            if (self.width // 2 - option_width // 2 <= x <= self.width // 2 + option_width // 2 and
                option_y - option_height // 2 <= y <= option_y + option_height // 2):
                self.selected_option = option
                return option
        
        return None
    
    def handle_keyboard(self, key: int) -> Optional[MenuOption]:
        """
        Handle keyboard input for menu navigation.
        
        Args:
            key: Pygame key code
            
        Returns:
            Selected MenuOption if Enter was pressed, None otherwise
        """
        if key == pygame.K_RETURN or key == pygame.K_SPACE:
            return self.selected_option if self.selected_option else MenuOption.FREE_FLIGHT
        return None
    
    def get_selected_option(self) -> Optional[MenuOption]:
        """
        Get the currently selected menu option.
        
        Returns:
            Currently selected MenuOption or None
        """
        return self.selected_option

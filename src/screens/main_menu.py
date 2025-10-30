"""
Main Menu Screen

The primary menu screen for the Cosmic Flight Simulator.
Provides navigation to missions, settings, and game modes.

This implementation adds:
- Full-screen support and responsive layout
- Hover/click visual feedback for options
- Simple animated starfield background
- Theme (colors/fonts) + accessibility toggles (font scale, high contrast)
- Basic transition hooks (fade-in/out alpha overlay)
"""

from __future__ import annotations

from enum import Enum
from typing import Optional, List, Tuple

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
    
    def __init__(
        self,
        width: int = 1280,
        height: int = 720,
        *,
        fullscreen: bool = False,
        font_scale: float = 1.0,
        high_contrast: bool = False,
        enable_sounds: bool = False,
    ) -> None:
        """
        Initialize the main menu screen.
        
        Args:
            width: Screen width in pixels
            height: Screen height in pixels
        """
        self.fullscreen = fullscreen
        self.width = width
        self.height = height
        self.selected_option: Optional[MenuOption] = None
        self.hover_option: Optional[MenuOption] = None
        self.font: Optional[pygame.font.Font] = None
        self.title_font: Optional[pygame.font.Font] = None
        self.font_scale = max(0.75, min(2.0, font_scale))
        self.high_contrast = high_contrast
        self.enable_sounds = enable_sounds

        # Theme colors
        if self.high_contrast:
            self.bg_color = (0, 0, 0)
            self.title_color = (255, 255, 0)
            self.text_color = (255, 255, 255)
            self.highlight_color = (0, 255, 255)
        else:
            self.bg_color = (5, 5, 15)
            self.title_color = (240, 240, 255)
            self.text_color = (200, 200, 200)
            self.highlight_color = (100, 200, 255)

        # Transition alpha (0=opaque content, 255=black overlay)
        self.fade_alpha = 0

        # Starfield background: (x, y, speed)
        self.stars: List[Tuple[float, float, float]] = []
        self._initialize_fonts()
        self._initialize_starfield()
        self._initialize_audio()
    
    def _initialize_fonts(self) -> None:
        """Initialize pygame fonts for menu rendering."""
        try:
            pygame.font.init()
            base_small = int(32 * self.font_scale)
            base_large = int(72 * self.font_scale)
            self.font = pygame.font.Font(None, base_small)
            self.title_font = pygame.font.Font(None, base_large)
        except Exception as e:
            print(f"Warning: Could not initialize fonts: {e}")
            self.font = None
            self.title_font = None

    def _initialize_starfield(self) -> None:
        """Create a simple starfield with varying speeds for parallax."""
        import random

        num_stars = max(100, (self.width * self.height) // 15000)
        self.stars = [
            (
                random.uniform(0, self.width),
                random.uniform(0, self.height),
                random.uniform(0.3, 1.2),
            )
            for _ in range(num_stars)
        ]

    def _initialize_audio(self) -> None:
        """Initialize audio system optionally for click/hover sounds."""
        if not self.enable_sounds:
            self.click_sound = None
            self.hover_sound = None
            return
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self.click_sound = None  # Placeholder for future asset
            self.hover_sound = None  # Placeholder for future asset
        except Exception as e:
            print(f"Warning: Could not initialize audio: {e}")
            self.click_sound = None
            self.hover_sound = None
    
    def render(self, surface: pygame.Surface) -> None:
        """
        Render the main menu screen to the given surface.
        
        Args:
            surface: Pygame surface to render to
        """
        # Background
        surface.fill(self.bg_color)
        self._render_starfield(surface)
        
        if not self.font or not self.title_font:
            return
        
        # Render title
        title_text = self.title_font.render(
            "Cosmic Flight Simulator", 
            True, 
            self.title_color
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
        spacing = int(60 * self.font_scale)
        
        for i, option in enumerate(menu_options):
            y_pos = start_y + (i * spacing)
            
            # Hover/selection feedback
            if option == self.selected_option:
                color = self.highlight_color
            elif option == self.hover_option:
                color = (
                    min(self.highlight_color[0] + 20, 255),
                    min(self.highlight_color[1] + 20, 255),
                    min(self.highlight_color[2] + 20, 255),
                )
            else:
                color = self.text_color
            
            option_text = self.font.render(option.value, True, color)
            option_rect = option_text.get_rect(center=(self.width // 2, y_pos))
            surface.blit(option_text, option_rect)

        # Fade overlay for transitions
        if self.fade_alpha > 0:
            overlay = pygame.Surface((self.width, self.height))
            overlay.set_alpha(self.fade_alpha)
            overlay.fill((0, 0, 0))
            surface.blit(overlay, (0, 0))

    def _render_starfield(self, surface: pygame.Surface) -> None:
        """Render and update a simple starfield background."""
        for idx, (x, y, speed) in enumerate(self.stars):
            # Star brightness scales with speed
            c = max(120, min(255, int(180 + speed * 60)))
            surface.fill((c, c, c), rect=pygame.Rect(int(x), int(y), 2, 2))

            # Move star downward for a subtle drift
            y += speed
            if y >= self.height:
                y = 0
            self.stars[idx] = (x, y, speed)
    
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
        spacing = int(60 * self.font_scale)
        option_width = int(260 * self.font_scale)
        option_height = int(44 * self.font_scale)
        
        for i, option in enumerate(menu_options):
            option_y = start_y + (i * spacing)
            
            # Check if click is within option bounds
            if (self.width // 2 - option_width // 2 <= x <= self.width // 2 + option_width // 2 and
                option_y - option_height // 2 <= y <= option_y + option_height // 2):
                self.selected_option = option
                if self.click_sound:
                    try:
                        self.click_sound.play()
                    except Exception:
                        pass
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

    def handle_mouse_move(self, pos: tuple[int, int]) -> None:
        """Update hover state based on mouse position."""
        x, y = pos
        menu_options = [
            MenuOption.FREE_FLIGHT,
            MenuOption.TUTORIAL,
            MenuOption.MISSIONS,
            MenuOption.SETTINGS,
            MenuOption.QUIT,
        ]
        start_y = 350
        spacing = int(60 * self.font_scale)
        option_width = int(260 * self.font_scale)
        option_height = int(44 * self.font_scale)

        new_hover: Optional[MenuOption] = None
        for i, option in enumerate(menu_options):
            option_y = start_y + (i * spacing)
            if (
                self.width // 2 - option_width // 2 <= x <= self.width // 2 + option_width // 2
                and option_y - option_height // 2 <= y <= option_y + option_height // 2
            ):
                new_hover = option
                break
        self.hover_option = new_hover

    def set_fullscreen(self, surface: pygame.Surface, enable: bool) -> pygame.Surface:
        """Toggle fullscreen, returning the new display surface."""
        if enable == self.fullscreen:
            return surface
        self.fullscreen = enable
        flags = pygame.FULLSCREEN if enable else 0
        display_info = pygame.display.Info()
        self.width = display_info.current_w if enable else self.width
        self.height = display_info.current_h if enable else self.height
        return pygame.display.set_mode((self.width, self.height), flags)

    def start_fade_in(self) -> None:
        """Begin a fade-in effect."""
        self.fade_alpha = 255

    def update_transition(self, dt_ms: int) -> None:
        """Update transition alpha based on elapsed time in ms."""
        if self.fade_alpha <= 0:
            return
        # Fade in over ~250ms
        self.fade_alpha = max(0, self.fade_alpha - int(255 * (dt_ms / 250.0)))
    
    def get_selected_option(self) -> Optional[MenuOption]:
        """
        Get the currently selected menu option.
        
        Returns:
            Currently selected MenuOption or None
        """
        return self.selected_option

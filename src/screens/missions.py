"""
Missions Screen

Mission selection screen for the Cosmic Flight Simulator.
Displays available missions and allows players to select and start missions.

This implementation:
- Mirrors MainMenuScreen pattern for consistency
- Displays mission list with details
- Provides visual feedback for selections
- Uses the same theme and starfield background
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple

import pygame


class MissionAction(Enum):
    """Available mission actions"""

    START = "Start Mission"
    BACK = "Back to Main Menu"


@dataclass
class MissionInfo:
    """Mission information for display"""

    id: str
    name: str
    description: str
    difficulty: str
    type: str
    completed: bool = False


class MissionsScreen:
    """
    Missions screen for the Cosmic Flight Simulator.

    Displays available missions and handles mission selection.
    Designed to respond within 0.1 seconds per performance requirements.

    Attributes:
        width: Screen width in pixels
        height: Screen height in pixels
        selected_mission: Currently selected mission index
        font: Font for rendering text
        title_font: Font for rendering the title
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
        missions: Optional[List[MissionInfo]] = None,
    ) -> None:
        """
        Initialize the missions screen.

        Args:
            width: Screen width in pixels
            height: Screen height in pixels
            fullscreen: Whether screen is in fullscreen mode
            font_scale: Font scaling factor (0.75-2.0)
            high_contrast: Enable high contrast colors
            enable_sounds: Enable audio feedback
            missions: Optional list of missions to display
        """
        self.fullscreen = fullscreen
        self.width = width
        self.height = height
        self.selected_mission_index: Optional[int] = None
        self.hover_mission_index: Optional[int] = None
        self.hover_action: Optional[MissionAction] = None
        self.font: Optional[pygame.font.Font] = None
        self.title_font: Optional[pygame.font.Font] = None
        self.body_font: Optional[pygame.font.Font] = None
        self.font_scale = max(0.75, min(2.0, font_scale))
        self.high_contrast = high_contrast
        self.enable_sounds = enable_sounds

        # Default missions if none provided
        self.missions: List[MissionInfo] = missions or [
            MissionInfo(
                id="mission-001",
                name="First Flight",
                description="Learn the basics of spacecraft control",
                difficulty="Beginner",
                type="Tutorial",
            ),
            MissionInfo(
                id="mission-002",
                name="Orbit Earth",
                description="Achieve stable orbit around Earth",
                difficulty="Intermediate",
                type="Orbital",
            ),
            MissionInfo(
                id="mission-003",
                name="Mars Transfer",
                description="Navigate to Mars using efficient transfer orbit",
                difficulty="Advanced",
                type="Interplanetary",
                completed=True,
            ),
        ]

        # Theme colors
        if self.high_contrast:
            self.bg_color = (0, 0, 0)
            self.title_color = (255, 255, 0)
            self.text_color = (255, 255, 255)
            self.highlight_color = (0, 255, 255)
            self.body_color = (255, 255, 255)
            self.completed_color = (0, 255, 0)
        else:
            self.bg_color = (5, 5, 15)
            self.title_color = (240, 240, 255)
            self.text_color = (200, 200, 200)
            self.highlight_color = (100, 200, 255)
            self.body_color = (180, 180, 200)
            self.completed_color = (100, 255, 100)

        # Transition alpha (0=opaque content, 255=black overlay)
        self.fade_alpha = 0

        # Starfield background: (x, y, speed)
        self.stars: List[Tuple[float, float, float]] = []
        self._initialize_fonts()
        self._initialize_starfield()
        self._initialize_audio()

    def _initialize_fonts(self) -> None:
        """Initialize pygame fonts for missions rendering."""
        try:
            pygame.font.init()
            base_small = int(32 * self.font_scale)
            base_medium = int(24 * self.font_scale)
            base_large = int(72 * self.font_scale)
            self.font = pygame.font.Font(None, base_small)
            self.body_font = pygame.font.Font(None, base_medium)
            self.title_font = pygame.font.Font(None, base_large)
        except Exception as e:
            print(f"Warning: Could not initialize fonts: {e}")
            self.font = None
            self.body_font = None
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
        Render the missions screen to the given surface.

        Args:
            surface: Pygame surface to render to
        """
        # Background
        surface.fill(self.bg_color)
        self._render_starfield(surface)

        if not self.font or not self.title_font or not self.body_font:
            return

        # Render title
        title_text = self.title_font.render("Missions", True, self.title_color)
        title_rect = title_text.get_rect(center=(self.width // 2, 80))
        surface.blit(title_text, title_rect)

        # Render mission list
        mission_start_y = 180
        mission_spacing = int(100 * self.font_scale)
        mission_width = int(800 * self.font_scale)
        mission_height = int(80 * self.font_scale)

        visible_missions = min(4, len(self.missions))  # Show up to 4 missions
        start_index = max(
            0,
            min(
                (self.selected_mission_index or 0) - 1,
                len(self.missions) - visible_missions,
            ),
        )

        for i in range(visible_missions):
            mission_idx = start_index + i
            if mission_idx >= len(self.missions):
                break

            mission = self.missions[mission_idx]
            y_pos = mission_start_y + (i * mission_spacing)

            # Selection/hover feedback
            is_selected = mission_idx == self.selected_mission_index
            is_hovered = mission_idx == self.hover_mission_index

            if is_selected:
                bg_color = (
                    self.highlight_color[0] // 4,
                    self.highlight_color[1] // 4,
                    self.highlight_color[2] // 4,
                )
                border_color = self.highlight_color
            elif is_hovered:
                bg_color = (
                    self.highlight_color[0] // 8,
                    self.highlight_color[1] // 8,
                    self.highlight_color[2] // 8,
                )
                border_color = (
                    min(self.highlight_color[0] + 20, 255),
                    min(self.highlight_color[1] + 20, 255),
                    min(self.highlight_color[2] + 20, 255),
                )
            else:
                bg_color = (
                    self.bg_color[0] + 10,
                    self.bg_color[1] + 10,
                    self.bg_color[2] + 10,
                )
                border_color = self.text_color

            # Draw mission box
            mission_rect = pygame.Rect(
                (self.width - mission_width) // 2,
                y_pos - mission_height // 2,
                mission_width,
                mission_height,
            )
            pygame.draw.rect(surface, bg_color, mission_rect)
            pygame.draw.rect(surface, border_color, mission_rect, 2)

            # Mission name
            name_color = self.completed_color if mission.completed else self.text_color
            name_text = self.font.render(mission.name, True, name_color)
            name_rect = name_text.get_rect(
                midleft=(mission_rect.left + 20, mission_rect.centery - 15)
            )
            surface.blit(name_text, name_rect)

            # Mission details
            details = f"{mission.type} • {mission.difficulty}"
            if mission.completed:
                details += " • ✓ Completed"
            details_text = self.body_font.render(details, True, self.body_color)
            details_rect = details_text.get_rect(
                midleft=(mission_rect.left + 20, mission_rect.centery + 15)
            )
            surface.blit(details_text, details_rect)

        # Render action buttons
        actions = []
        if self.selected_mission_index is not None:
            actions.append(MissionAction.START)
        actions.append(MissionAction.BACK)

        button_start_y = self.height - 100
        button_spacing = int(200 * self.font_scale)
        button_start_x = self.width // 2 - ((len(actions) - 1) * button_spacing // 2)

        for i, action in enumerate(actions):
            x_pos = button_start_x + (i * button_spacing)

            # Hover/selection feedback
            if action == self.hover_action:
                color = (
                    min(self.highlight_color[0] + 20, 255),
                    min(self.highlight_color[1] + 20, 255),
                    min(self.highlight_color[2] + 20, 255),
                )
            else:
                color = self.text_color

            action_text = self.font.render(action.value, True, color)
            action_rect = action_text.get_rect(center=(x_pos, button_start_y))
            surface.blit(action_text, action_rect)

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

    def handle_click(self, pos: tuple[int, int]) -> Optional[MissionAction]:
        """
        Handle mouse click on the missions screen.

        Designed to respond within 0.1 seconds per performance requirements.

        Args:
            pos: Mouse position (x, y)

        Returns:
            Selected MissionAction if click was on an action button,
            or None if a mission was selected
        """
        x, y = pos

        # Check mission list clicks
        mission_start_y = 180
        mission_spacing = int(100 * self.font_scale)
        mission_width = int(800 * self.font_scale)
        mission_height = int(80 * self.font_scale)

        visible_missions = min(4, len(self.missions))
        start_index = max(
            0,
            min(
                (self.selected_mission_index or 0) - 1,
                len(self.missions) - visible_missions,
            ),
        )

        for i in range(visible_missions):
            mission_idx = start_index + i
            if mission_idx >= len(self.missions):
                break

            y_pos = mission_start_y + (i * mission_spacing)
            mission_rect = pygame.Rect(
                (self.width - mission_width) // 2,
                y_pos - mission_height // 2,
                mission_width,
                mission_height,
            )

            if mission_rect.collidepoint(x, y):
                self.selected_mission_index = mission_idx
                if self.click_sound:
                    try:
                        self.click_sound.play()
                    except Exception:
                        pass
                return None

        # Check action button clicks
        actions = []
        if self.selected_mission_index is not None:
            actions.append(MissionAction.START)
        actions.append(MissionAction.BACK)

        button_start_y = self.height - 100
        button_spacing = int(200 * self.font_scale)
        button_start_x = self.width // 2 - ((len(actions) - 1) * button_spacing // 2)
        button_width = int(180 * self.font_scale)
        button_height = int(44 * self.font_scale)

        for i, action in enumerate(actions):
            button_x = button_start_x + (i * button_spacing)

            if (
                button_x - button_width // 2 <= x <= button_x + button_width // 2
                and button_start_y - button_height // 2
                <= y
                <= button_start_y + button_height // 2
            ):
                if self.click_sound:
                    try:
                        self.click_sound.play()
                    except Exception:
                        pass
                return action

        return None

    def handle_keyboard(self, key: int) -> Optional[MissionAction]:
        """
        Handle keyboard input for missions navigation.

        Args:
            key: Pygame key code

        Returns:
            Selected MissionAction if Enter/Space/Escape was pressed, None otherwise
        """
        if key == pygame.K_UP:
            if self.selected_mission_index is None:
                self.selected_mission_index = 0
            else:
                self.selected_mission_index = max(0, self.selected_mission_index - 1)
            if self.hover_sound:
                try:
                    self.hover_sound.play()
                except Exception:
                    pass
        elif key == pygame.K_DOWN:
            if self.selected_mission_index is None:
                self.selected_mission_index = 0
            else:
                self.selected_mission_index = min(
                    len(self.missions) - 1, self.selected_mission_index + 1
                )
            if self.hover_sound:
                try:
                    self.hover_sound.play()
                except Exception:
                    pass
        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            if self.selected_mission_index is not None:
                return MissionAction.START
        elif key == pygame.K_ESCAPE:
            return MissionAction.BACK

        return None

    def handle_mouse_move(self, pos: tuple[int, int]) -> None:
        """Update hover state based on mouse position."""
        x, y = pos

        # Check mission list hover
        mission_start_y = 180
        mission_spacing = int(100 * self.font_scale)
        mission_width = int(800 * self.font_scale)
        mission_height = int(80 * self.font_scale)

        visible_missions = min(4, len(self.missions))
        start_index = max(
            0,
            min(
                (self.selected_mission_index or 0) - 1,
                len(self.missions) - visible_missions,
            ),
        )

        new_hover: Optional[int] = None
        for i in range(visible_missions):
            mission_idx = start_index + i
            if mission_idx >= len(self.missions):
                break

            y_pos = mission_start_y + (i * mission_spacing)
            mission_rect = pygame.Rect(
                (self.width - mission_width) // 2,
                y_pos - mission_height // 2,
                mission_width,
                mission_height,
            )

            if mission_rect.collidepoint(x, y):
                new_hover = mission_idx
                break

        self.hover_mission_index = new_hover

        # Check action button hover
        actions = []
        if self.selected_mission_index is not None:
            actions.append(MissionAction.START)
        actions.append(MissionAction.BACK)

        button_start_y = self.height - 100
        button_spacing = int(200 * self.font_scale)
        button_start_x = self.width // 2 - ((len(actions) - 1) * button_spacing // 2)
        button_width = int(180 * self.font_scale)
        button_height = int(44 * self.font_scale)

        new_hover_action: Optional[MissionAction] = None
        for i, action in enumerate(actions):
            button_x = button_start_x + (i * button_spacing)
            if (
                button_x - button_width // 2 <= x <= button_x + button_width // 2
                and button_start_y - button_height // 2
                <= y
                <= button_start_y + button_height // 2
            ):
                new_hover_action = action
                break
        self.hover_action = new_hover_action

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

    def get_selected_mission(self) -> Optional[MissionInfo]:
        """
        Get the currently selected mission.

        Returns:
            Selected MissionInfo or None
        """
        if self.selected_mission_index is None:
            return None
        if 0 <= self.selected_mission_index < len(self.missions):
            return self.missions[self.selected_mission_index]
        return None

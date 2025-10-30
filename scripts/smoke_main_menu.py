import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import sys
import time
import pygame

# Allow running from repo root or script dir
REPO_ROOT = os.path.dirname(os.path.dirname(__file__))
SRC_DIR = os.path.join(REPO_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from screens.main_menu import MainMenuScreen, MenuOption  # noqa: E402


def main() -> int:
    pygame.init()
    try:
        width, height = 800, 600
        screen = pygame.display.set_mode((width, height))
        menu = MainMenuScreen(width=width, height=height, font_scale=1.0, high_contrast=False)

        # Initial render
        menu.start_fade_in()
        menu.update_transition(0)
        menu.render(screen)

        # Simulate mouse move to hover over first option
        menu.handle_mouse_move((width // 2, 350))
        menu.render(screen)

        # Simulate click on first option
        selected = menu.handle_click((width // 2, 350))
        assert selected in (MenuOption.FREE_FLIGHT, None)

        # Update fade for 250ms worth
        menu.update_transition(250)
        menu.render(screen)

        # Save a screenshot artifact in tmp
        out_path = os.path.join(REPO_ROOT, "smoke_main_menu.png")
        pygame.image.save(screen, out_path)
        print(f"Smoke test OK. Screenshot saved to: {out_path}")
        return 0
    finally:
        pygame.quit()


if __name__ == "__main__":
    raise SystemExit(main())

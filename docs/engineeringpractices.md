# Engineering Practices

This document outlines the technical standards, conventions, and practices for the Cosmic Flight Simulator project, derived from analysis of the existing codebase.

## Technology Stack

### Core Technologies
- **Python**: 3.11+ (primary language)
- **Pygame**: 2.6+ (UI framework, input handling, rendering surface)
- **PyOpenGL**: 3.1+ (3D graphics and rendering)
- **NumPy**: 1.20+ (mathematical computations, vectors)
- **Pillow**: 8.0+ (image processing)

### Testing & Quality
- **pytest**: 6.2+ (testing framework)
- **pytest-cov**: 2.12+ (coverage reporting)

### Future Considerations
- **Matplotlib**: 3.3+ (data visualization)
- **SciPy**: 1.6+ (scientific computing)

## Code Style Guidelines

### Python Style
- **Formatter**: Black (line length 88)
- **Linter**: Ruff with rules: `E,F,W,I,UP,PL,PT,B,SIM,ISC,PERF,COM,ANN`
- **Type Checking**: MyPy + Pyright
- **Import Style**: `from __future__ import annotations` in all new modules

### Import Organization
```python
# Standard library
import os
import sys
from typing import Optional, List, Tuple

# Third-party
import pygame
import numpy as np

# First-party
from screens.main_menu import MainMenuScreen
```
One blank line between groups; no wildcard imports.

### Naming Conventions

#### Files & Directories
- **Files**: `snake_case.py` (e.g., `main_menu.py`, `settings.py`)
- **Directories**: `snake_case` (e.g., `src/`, `tests/`, `docs/`)
- **Scripts**: `snake_case.py` in `scripts/` (e.g., `smoke_main_menu.py`)

#### Python Identifiers
- **Classes**: `PascalCase` (e.g., `MainMenuScreen`, `SettingsScreen`)
- **Functions/Methods**: `snake_case` (e.g., `handle_click`, `update_transition`)
- **Private Methods**: `_snake_case` (e.g., `_initialize_fonts`, `_render_starfield`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `SALT_LENGTH`, `SCREEN_WIDTH`)
- **Enums**: `PascalCase` (e.g., `MenuOption`, `SettingsCategory`)
- **Enum Members**: `UPPER_SNAKE_CASE` (e.g., `FREE_FLIGHT`, `DISPLAY`)

### Documentation Standards

#### Module Docstrings
```python
"""
Module Title

Brief description of the module's purpose and functionality.

Key features/patterns documented here.
"""
```

#### Class Docstrings
```python
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
```

#### Function Docstrings
```python
def handle_click(self, pos: tuple[int, int]) -> Optional[MenuOption]:
    """
    Handle mouse click on the menu screen.
    
    Designed to respond within 0.1 seconds per performance requirements.
    
    Args:
        pos: Mouse position (x, y)
        
    Returns:
        Selected MenuOption if click was on a menu item, None otherwise
    """
```

All public functions/classes must have:
- Complete type hints
- Short Google-style docstrings
- Args/Returns documentation

### Function/Class Guidelines
- **Function Length**: ≤ 40 lines (extract helpers if longer)
- **Class Size**: Keep focused and cohesive
- **Complexity**: Prefer early returns, avoid deeply nested logic
- **No Global State**: Pass settings/clients explicitly via dependency injection
- **Logging**: Use `logging` module; `print` only in CLIs and temporary diagnostics

## Architecture Patterns

### Layered Architecture
```
visualization → cockpit → simulator (one-way inward)
```

#### Domain Layer (`src/simulator/`)
- Pure business logic only
- No IO or rendering
- Standard library + safe math libs only
- Files: `physics.py`, `spacecraft.py`, `solar_system.py`

#### Application Layer (`src/cockpit/`)
- Control orchestration, HUD logic
- Exposes use-cases/services/DTOs
- No rendering
- Files: `controls.py`, `hud.py`, `instruments.py`

#### Adapters (`src/visualization/`, `assets/`)
- Implements ports
- May perform IO and framework calls
- No business rules
- Files: `renderer.py`, `camera.py`, `models.py`

#### Entry Point
- `main.py` wires layers together
- Dependency injection at composition root

### Screen Pattern (UI)
All screen classes follow this pattern:

```python
class XxxScreen:
    def __init__(self, width: int, height: int, *, 
                 fullscreen: bool, font_scale: float, 
                 high_contrast: bool, enable_sounds: bool) -> None:
        # Initialize dimensions, fonts, theme colors
        
    def render(self, surface: pygame.Surface) -> None:
        # Render screen content
        
    def handle_click(self, pos: tuple[int, int]) -> Optional[Enum]:
        # Handle mouse clicks (response within 0.1s)
        
    def handle_keyboard(self, key: int) -> Optional[Enum]:
        # Handle keyboard input
        
    def handle_mouse_move(self, pos: tuple[int, int]) -> None:
        # Update hover state
        
    def _private_helpers(self) -> None:
        # Private initialization/render helpers
```

### Common Patterns

#### Enums for State
```python
class MenuOption(Enum):
    """Available menu options"""
    FREE_FLIGHT = "Free Flight"
    TUTORIAL = "Tutorial"
    MISSIONS = "Missions"
    SETTINGS = "Settings"
    QUIT = "Quit"
```

#### Theme Colors
```python
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
```

#### Error Handling
```python
try:
    # Operation
except Exception as e:
    print(f"Warning: Could not initialize X: {e}")
    # Set to safe default
    self.value = None
```

#### Transition Management
```python
# Fade alpha: 0 = opaque content, 255 = black overlay
self.fade_alpha = 0

def update_transition(self, dt_ms: int) -> None:
    """Update transition alpha based on elapsed time in ms."""
    if self.fade_alpha <= 0:
        return
    # Fade in over ~250ms
    self.fade_alpha = max(0, self.fade_alpha - int(255 * (dt_ms / 250.0)))
```

## Testing Practices

### Framework & Coverage
- **Framework**: pytest with coverage
- **Markers**: `@pytest.mark.slow`, `@pytest.mark.integration`
- **Coverage Goals**:
  - Overall: 80% minimum
  - `src/simulator/*`: 90% minimum

### Smoke Tests
Headless UI tests using SDL dummy video driver:

```python
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import sys
from screens.main_menu import MainMenuScreen

REPO_ROOT = os.path.dirname(os.path.dirname(__file__))
SRC_DIR = os.path.join(REPO_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

def main() -> int:
    pygame.init()
    try:
        # Test initialization, rendering, interaction
        return 0
    finally:
        pygame.quit()

if __name__ == "__main__":
    raise SystemExit(main())
```

### Test Organization
```
tests/
├── test_physics.py        # Domain logic tests
├── test_spacecraft.py     # Simulator tests
└── test_cockpit.py        # Application layer tests
```

### Test Patterns
- Unit tests avoid network/filesystem
- Use fixtures/factories for test data
- Deterministic RNG/clock injection
- Test all error paths and edge cases

## Performance Requirements

### Critical Constraints
- **Response Time**: 0.1 seconds (100ms) per user interaction
- **Frame Rate**: 30-60 FPS for smooth gameplay
- **Compatibility**: Runs on standard laptop with integrated GPU
- **Memory**: Minimal footprint, efficient rendering

### Optimization Guidelines
- Prefer fast path operations in hot loops
- Cache expensive computations
- Batch rendering operations
- Profile before optimizing

## Security Practices

### Secrets Management
- No secrets in code, commits, or docs
- Use environment variables or secrets manager
- Provide `.env.example` as template only

### Input Validation
- Validate external inputs at adapter boundaries
- Never use `eval()` or `exec()`
- Sanitize user-provided data

### Logging
- Redact PII in logs
- Avoid dumping raw objects containing sensitive data
- Use appropriate log levels

## Version Control

### Branch Strategy
- `main`: Production-ready code
- `feature/*`: Feature development
- `fix/*`: Bug fixes
- `docs/*`: Documentation updates

### Commit Messages
Conventional Commits format:
- `feat(scope): description`
- `fix(scope): description`
- `docs(scope): description`
- `refactor(scope): description`
- `test(scope): description`
- `chore(scope): description`

Examples:
```
feat(ui): add Settings screen with smoke test
fix(physics): correct orbital mechanics calculation
docs(arch): update component interaction diagram
refactor(cockpit): extract common screen pattern
test(ui): add headless smoke test for main menu
chore(deps): bump pygame to 2.6.1
```

### Pull Request Template
See `prompts-samples/pr-description-template.md` for PR structure:
- Summary
- Changes
- Type of change
- Description (What/Why/How to test)
- Screenshots/Demo
- Checklist

## File Organization

### Directory Structure
```
ai-playground/
├── main.py                 # Entry point
├── requirements.txt        # Python dependencies
├── README.md              # Project overview
├── engineeringpractices.md # This file
├── userflows.md           # User flow documentation
├── docs/                   # Documentation
│   ├── ARCHITECTURE.md    # System architecture
│   ├── DIAGRAMS.md        # PlantUML diagrams
│   ├── IMPLEMENTATION.md  # Implementation guide
│   ├── REQUIREMENTS.md    # Requirements spec
│   └── SETUP.md           # Setup instructions
├── src/
│   ├── simulator/         # Domain layer
│   ├── cockpit/           # Application layer
│   ├── visualization/     # Adapter layer
│   └── screens/           # UI screens
├── assets/                # Game assets
│   ├── models/           # 3D models
│   ├── textures/         # Textures
│   └── sounds/           # Sound effects
├── missions/              # Mission definitions
├── tests/                 # Test suites
├── scripts/               # Utility scripts
│   ├── smoke_*.py        # Smoke tests
│   └── find_*.py         # Development tools
└── prompts-samples/       # Templates and examples
```

### File Naming
- Python modules: `snake_case.py`
- Test files: `test_<module>.py`
- Documentation: `UPPER_SNAKE_CASE.md`
- Scripts: `snake_case.py` (descriptive name)

## Tooling Configuration

### Required Files
- `pyproject.toml` - Project metadata
- `.pre-commit-config.yaml` - Git hooks
- `mypy.ini` - Type checking config
- `pyrightconfig.json` - Pyright config
- `.editorconfig` - Editor settings
- `pytest.ini` - Test configuration
- `.vscode/settings.json` - IDE settings
- `.gitignore` - Git exclusions
- `.github/workflows/ci.yml` - CI pipeline

### CI Pipeline
Must run in order:
1. `ruff check`
2. `black --check`
3. `mypy`
4. `pyright`
5. `pytest --cov`
6. `safety` or `pip-audit`

### Editor Setup
- Auto-fix lint/format on save
- Organize imports with Ruff
- Type checking on save

## Common Pitfalls

### To Avoid
1. **Breaking Layering**: Don't import `simulator` from `visualization`
2. **Business Logic in UI**: Keep rendering separate from domain logic
3. **Missing Type Hints**: Always type public APIs
4. **Untested Code**: Maintain coverage thresholds
5. **Breaking APIs**: Preserve public APIs unless explicitly allowed
6. **Large Commits**: Prefer small, reviewable diffs
7. **Mass Edits**: Don't auto-rewrite large files without explicit request

### Best Practices
1. Ask up to 3 focused questions if task is ambiguous
2. Generate matching tests for new code
3. Update docs for architectural changes
4. Move files in separate commits (structure → behavior → cleanup)
5. Leave meaningful comments for complex logic
6. Keep functions under 40 lines
7. Use early returns to reduce nesting

## Resources

### External Documentation
- [Python PEP 8](https://pep8.org/)
- [Black Style Guide](https://black.readthedocs.io/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Pygame Documentation](https://www.pygame.org/docs/)
- [Conventional Commits](https://www.conventionalcommits.org/)

### Internal Documentation
- [Architecture Documentation](docs/ARCHITECTURE.md)
- [Implementation Guide](docs/IMPLEMENTATION.md)
- [Requirements Specification](docs/REQUIREMENTS.md)
- [User Flows](userflows.md)

---

**Last Updated**: Generated via AI analysis of existing codebase
**Maintained By**: Development Team

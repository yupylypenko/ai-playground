# Setup Guide

## Prerequisites

### System Requirements
- Python 3.8 or higher
- pip 20.0 or higher
- 4GB RAM minimum
- Graphics card with OpenGL 3.3 support

### Development Requirements
- Git
- Code editor (VS Code, PyCharm, etc.)
- Optional: Virtual environment tools

## Installation Steps

### 1. Clone the Repository
```bash
git clone <repository-url>
cd ai-playground
```

### 2. Create Virtual Environment (Recommended)
```bash
# On Linux/Mac
python -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Verify Installation
```bash
python -c "import pygame; import numpy; print('Installation successful!')"
```

## Running the Simulator

### Basic Run
```bash
python main.py
```

### With Options
```bash
# Run specific mission
python main.py --mission "Mars Mission"

# Select spacecraft
python main.py --ship Scout

# Enable debug mode
python main.py --debug
```

## Development Setup

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_physics.py
```

### Code Quality
```bash
# Check code style
pylint src/

# Format code
black src/
```

## Troubleshooting

### Import Errors
- Ensure virtual environment is activated
- Verify all dependencies are installed
- Check Python version compatibility

### Graphics Issues
- Update graphics drivers
- Verify OpenGL support
- Check system requirements

### Performance Issues
- Reduce render quality settings
- Close other applications
- Check system resources

## Next Steps

1. Read REQUIREMENTS.md for feature details
2. Review ARCHITECTURE.md for system design
3. Start with IMPLEMENTATION.md for development
4. Run tests to verify setup

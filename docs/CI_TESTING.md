# CI Testing Guide

This guide explains how to test the GitHub Actions CI pipeline locally.

## Method 1: Using Act (GitHub Actions Locally)

`act` is a tool that runs GitHub Actions workflows locally using Docker.

### Prerequisites

1. **Docker** must be installed:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install docker.io
   sudo systemctl start docker
   sudo systemctl enable docker

   # Or via snap
   snap install docker
   ```

2. **Act** tool:
   ```bash
   # Install act
   curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash
   # Or
   snap install act
   ```

### Using Act

#### List available workflows:
```bash
cd /mnt/d/git/ai-playground
act --list
```

#### Run a specific job:
```bash
# Run prepare job
act -j prepare

# Run lint job
act -j lint

# Run test job (unit tests)
act -j test -e test-type=unit

# Run test job (integration tests)
act -j test -e test-type=integration

# Run build job
act -j build
```

#### Run entire workflow:
```bash
# Run all jobs
act

# Run with specific event
act push

# Run specific workflow file
act -W .github/workflows/ci.yml
```

#### Run with custom environment:
```bash
# Use specific Python version
act -j prepare -e PYTHON_VERSION=3.11

# Dry run (show what would run)
act --dry-run
```

### Act Configuration

Create `.actrc` file in project root:
```
-P ubuntu-latest=catthehacker/ubuntu:act-latest
-W .github/workflows
```

### Common Act Issues

1. **Docker not running**: Start Docker service
   ```bash
   sudo systemctl start docker
   ```

2. **Permission denied**: Add user to docker group
   ```bash
   sudo usermod -aG docker $USER
   newgrp docker
   ```

3. **Large image downloads**: Act downloads Docker images on first run
   - This can take several minutes
   - Images are cached for subsequent runs

## Method 2: Local Test Script (No Docker)

Use the provided local test script that simulates CI without Docker:

```bash
cd /mnt/d/git/ai-playground
./scripts/test_ci_local.sh
```

This script:
- ✅ Checks Python and pip versions
- ✅ Installs dependencies
- ✅ Runs linting (Black, Ruff, MyPy, Pyright)
- ✅ Runs unit tests
- ✅ Runs integration tests
- ✅ Tests build verification
- ✅ Provides summary report

### Running Individual Checks

You can also run individual checks manually:

```bash
# Linting
ruff check src/ tests/ scripts/*.py main.py
black --check src/ tests/ scripts/*.py main.py
mypy src/ --ignore-missing-imports

# Tests
pytest tests/ -v
pytest tests/test_integration.py -v

# Build verification
python main.py --help
python -c "from src.simulator import *; from src.models import *; print('OK')"
```

## Method 3: VS Code Extension

### GitHub Actions Extension

Install the "GitHub Actions" extension for VS Code:
1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search for "GitHub Actions"
4. Install by GitHub

Features:
- View workflow runs
- Check workflow syntax
- View logs
- Manual workflow triggers (if you have permissions)

### Act Extension for VS Code

Install "act" extension:
1. Install the "act" extension in VS Code
2. Configure Docker connection
3. Right-click on `.github/workflows/ci.yml`
4. Select "Run with act"

## CI Pipeline Jobs

### 1. Prepare Job
- Sets up Python 3.11
- Installs dependencies
- Caches packages

### 2. Lint Job
- Black: Code formatting
- Ruff: Code quality
- MyPy: Type checking
- Pyright: Type checking

### 3. Test Job
- **Unit Tests**: Fast, isolated tests
- **Integration Tests**: Component interaction tests

### 4. Build Job
- Verifies imports
- Tests application startup
- Validates dependencies

## Debugging Failed CI

If CI fails locally:

1. **Check dependencies**:
   ```bash
   pip list | grep -E "(pytest|black|ruff|mypy)"
   ```

2. **Run specific test**:
   ```bash
   pytest tests/test_physics.py -v
   ```

3. **Check linting**:
   ```bash
   ruff check src/ --output-format=github
   ```

4. **Test imports**:
   ```bash
   python -c "from src.simulator import *"
   ```

## Best Practices

1. **Run local tests before pushing**:
   ```bash
   ./scripts/test_ci_local.sh
   ```

2. **Fix linting issues locally**:
   ```bash
   black src/ tests/ scripts/*.py main.py
   ruff check --fix src/ tests/
   ```

3. **Test specific changes**:
   ```bash
   pytest tests/test_physics.py::TestPhysicsEngine::test_calculate_gravity -v
   ```

4. **Check workflow syntax**:
   ```bash
   act --dry-run
   ```

## Troubleshooting

### Act Issues

**Problem**: `act` can't connect to Docker
**Solution**:
```bash
sudo systemctl start docker
sudo usermod -aG docker $USER
newgrp docker
```

**Problem**: Act downloads large images
**Solution**: First run downloads images (~1GB), subsequent runs use cache

**Problem**: Tests fail in act but work locally
**Solution**: Check environment variables, paths, and dependencies

### Local Test Script Issues

**Problem**: Python not found
**Solution**: Use `python3` explicitly or set alias

**Problem**: Dependencies not installed
**Solution**:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

**Problem**: Tests fail with display errors
**Solution**: Set `SDL_VIDEODRIVER=dummy` and `DISPLAY=:99`

## Additional Resources

- [Act Documentation](https://github.com/nektos/act)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Pytest Documentation](https://docs.pytest.org/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)

---

**Last Updated**: November 2024

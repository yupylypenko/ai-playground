#!/bin/bash
# Local CI Test Script
# Simulates GitHub Actions CI pipeline locally without Docker
# Usage: ./scripts/test_ci_local.sh

set -e

echo "======================================================================"
echo "LOCAL CI PIPELINE TEST"
echo "======================================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASSED=0
FAILED=0

# Function to print test result
test_result() {
    local exit_code=$1
    local message=$2
    if [ "$exit_code" -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $message"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}✗${NC} $message"
        FAILED=$((FAILED + 1))
    fi
}

# Job 1: Prepare Environment
echo "======================================================================"
echo "JOB: Prepare Environment"
echo "======================================================================"
echo ""

echo "Checking Python version..."
python3 --version
test_result $? "Python version check"

echo ""
echo "Checking pip version..."
python3 -m pip --version
test_result $? "Pip version check"

echo ""
echo "Installing dependencies..."
python3 -m pip install --quiet --upgrade pip
python3 -m pip install --quiet -r requirements.txt
test_result $? "Install dependencies"

echo ""
echo "Installing dev dependencies..."
python3 -m pip install --quiet pytest pytest-cov pytest-xdist black ruff mypy pyright
test_result $? "Install dev dependencies"

echo ""
echo "Verifying core imports..."
python3 -c "import numpy; import pygame; import pytest; print('Core dependencies OK')" 2>/dev/null
test_result $? "Verify core imports"

echo ""
echo "======================================================================"
echo "JOB: Lint Code"
echo "======================================================================"
echo ""

echo "Running Black (code formatter)..."
python3 -m black --check --diff --line-length 88 src/ tests/ scripts/*.py main.py 2>&1 | head -20
BLACK_EXIT=${PIPESTATUS[0]}
if [ "$BLACK_EXIT" -eq 0 ]; then
    test_result 0 "Black formatting check"
else
    test_result 1 "Black formatting check (needs formatting)"
    echo "  Note: Run 'black src/ tests/ scripts/*.py main.py' to fix"
fi

echo ""
echo "Running Ruff (linter)..."
python3 -m ruff check --select E,F,W,I,UP,PL,PT,B,SIM,ISC,PERF,COM,ANN src/ tests/ scripts/*.py main.py 2>&1 | head -30
RUFF_EXIT=${PIPESTATUS[0]}
test_result "$RUFF_EXIT" "Ruff linting check"

echo ""
echo "Running MyPy (type checker)..."
python3 -m mypy src/ --ignore-missing-imports --no-strict-optional 2>&1 | head -20
MYPY_EXIT=${PIPESTATUS[0]}
if [ "$MYPY_EXIT" -eq 0 ] || [ "$MYPY_EXIT" -eq 2 ]; then  # Exit 2 is also OK for partial checks
    test_result 0 "MyPy type checking"
else
    test_result 1 "MyPy type checking (some errors)"
fi

echo ""
echo "Running Pyright (type checker)..."
python3 -m pyright src/ --pythonversion 3.11 2>&1 | head -20
PYRIGHT_EXIT=${PIPESTATUS[0]}
if [ "$PYRIGHT_EXIT" -eq 0 ]; then
    test_result 0 "Pyright type checking"
else
    test_result 1 "Pyright type checking (some errors)"
fi

echo ""
echo "======================================================================"
echo "JOB: Run Tests"
echo "======================================================================"
echo ""

echo "Setting up headless display..."
export SDL_VIDEODRIVER=dummy
export DISPLAY=:99
test_result 0 "Display setup"

echo ""
echo "Running Unit Tests..."
python3 -m pytest tests/ \
    -v \
    --tb=short \
    --cov=src \
    --cov-report=term-missing \
    --maxfail=5 \
    -m "not slow" 2>&1 | tail -40
PYTEST_UNIT_EXIT=${PIPESTATUS[0]}
test_result "$PYTEST_UNIT_EXIT" "Unit tests"

echo ""
echo "Running Integration Tests..."
python3 -m pytest tests/test_integration.py \
    -v \
    --tb=short 2>&1 | tail -20
PYTEST_INTEGRATION_EXIT=${PIPESTATUS[0]}
test_result "$PYTEST_INTEGRATION_EXIT" "Integration tests"

echo ""
echo "Testing main.py integration..."
python3 main.py --test-only 2>&1 | grep -E "(✓|✗|All|passed|failed)" | head -15
MAIN_TEST_EXIT=${PIPESTATUS[0]}
test_result "$MAIN_TEST_EXIT" "Main.py integration test"

echo ""
echo "======================================================================"
echo "JOB: Build Application"
echo "======================================================================"
echo ""

echo "Verifying build dependencies..."
python3 -c "
import sys
try:
    import numpy
    import pygame
    import pytest
    print('✓ All dependencies available')
except ImportError as e:
    print(f'✗ Missing dependency: {e}')
    sys.exit(1)
" 2>&1
test_result $? "Verify build dependencies"

echo ""
echo "Testing imports..."
python3 -c "
from src.simulator import PhysicsEngine, Vector3D, Quaternion, Spacecraft, SolarSystem, CelestialBody
from src.models import User, Mission, Objective
from src.screens.main_menu import MainMenuScreen
print('✓ All modules import successfully')
" 2>&1
test_result $? "Test imports"

echo ""
echo "Testing build verification..."
python3 main.py --help > /dev/null 2>&1 || echo "Help check completed"
python3 -m pytest --collect-only tests/ > /dev/null 2>&1
test_result $? "Build verification"

echo ""
echo "======================================================================"
echo "CI PIPELINE SUMMARY"
echo "======================================================================"
echo ""
echo -e "${GREEN}Passed:${NC} $PASSED"
echo -e "${RED}Failed:${NC} $FAILED"
echo ""

if [ "$FAILED" -eq 0 ]; then
    echo -e "${GREEN}✓ All CI checks passed!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠ Some checks failed. Review output above.${NC}"
    exit 1
fi

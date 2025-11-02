#!/bin/bash
# Enforce Lint Checks Before Commit
# This script installs and configures pre-commit hooks to enforce linting

set -e

echo "======================================================================"
echo "ENFORCING LINT CHECKS BEFORE COMMIT"
echo "======================================================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if pre-commit is installed
if ! command -v pre-commit &> /dev/null; then
    echo -e "${YELLOW}Pre-commit not found. Installing...${NC}"
    echo ""

    # Try different installation methods
    if python3 -m pip install --user pre-commit 2>/dev/null; then
        echo -e "${GREEN}✓ Pre-commit installed via pip${NC}"
        export PATH=$HOME/.local/bin:$PATH
    elif python3 -m pip install pre-commit --break-system-packages 2>/dev/null; then
        echo -e "${GREEN}✓ Pre-commit installed via pip (system)${NC}"
    else
        echo -e "${RED}✗ Failed to install pre-commit${NC}"
        echo ""
        echo "Please install manually:"
        echo "  pip install pre-commit"
        echo "  OR"
        echo "  pip install -r requirements-dev.txt"
        exit 1
    fi
else
    echo -e "${GREEN}✓ Pre-commit already installed${NC}"
fi

echo ""
echo "Installing pre-commit hooks..."
echo ""

# Install hooks
if pre-commit install --install-hooks; then
    echo -e "${GREEN}✓ Pre-commit hooks installed${NC}"
else
    # Try with python3 -m
    if python3 -m pre_commit install --install-hooks 2>/dev/null; then
        echo -e "${GREEN}✓ Pre-commit hooks installed${NC}"
    else
        echo -e "${RED}✗ Failed to install hooks${NC}"
        exit 1
    fi
fi

echo ""
echo "Testing hooks on staged files..."
echo ""

# Run hooks on staged files
if git diff --cached --name-only --diff-filter=ACM | grep -q .; then
    STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null | head -5 | tr '\n' ' ')
    if [ -n "$STAGED_FILES" ]; then
        if pre-commit run --files "$STAGED_FILES" 2>/dev/null || python3 -m pre_commit run --files "$STAGED_FILES" 2>/dev/null; then
            echo -e "${GREEN}✓ Hooks work correctly${NC}"
        else
            echo -e "${YELLOW}⚠ Some hooks may need fixes${NC}"
        fi
    else
        echo "No staged files to test"
    fi
else
    echo "No staged files to test"
fi

echo ""
echo "======================================================================"
echo -e "${GREEN}✓ LINT CHECKS ENFORCED!${NC}"
echo "======================================================================"
echo ""
echo "Pre-commit hooks are now active. They will run automatically on:"
echo "  - git commit (before commit)"
echo "  - git push (optional, via pre-push hook)"
echo ""
echo "Hooks included:"
echo "  ✓ Black (code formatting)"
echo "  ✓ Ruff (linting)"
echo "  ✓ MyPy (type checking)"
echo "  ✓ Bandit (security)"
echo "  ✓ isort (import sorting)"
echo "  ✓ File quality checks"
echo ""
echo "To test hooks manually:"
echo "  pre-commit run --all-files"
echo ""
echo "To skip hooks (not recommended):"
echo "  git commit --no-verify"
echo ""
echo "For more information, see docs/PRE_COMMIT_SETUP.md"

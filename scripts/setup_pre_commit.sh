#!/bin/bash
# Setup Pre-commit Hooks
# Usage: ./scripts/setup_pre_commit.sh

set -e

echo "======================================================================"
echo "PRE-COMMIT HOOKS SETUP"
echo "======================================================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "Step 1: Installing pre-commit..."
python3 -m pip install --upgrade pip
python3 -m pip install pre-commit || python3 -m pip install -r requirements-dev.txt

echo ""
echo "Step 2: Installing hooks..."
pre-commit install
pre-commit install --hook-type commit-msg || echo "Note: commit-msg hook optional"

echo ""
echo "Step 3: Testing hooks..."
echo "Running pre-commit on all files (may take a few minutes)..."
pre-commit run --all-files || echo -e "${YELLOW}Some hooks failed - this is normal on first run${NC}"

echo ""
echo -e "${GREEN}✓ Pre-commit hooks installed!${NC}"
echo ""
echo "Hooks will now run automatically on git commit."
echo ""
echo "To test manually:"
echo "  pre-commit run --all-files"
echo ""
echo "To skip hooks (not recommended):"
echo "  git commit --no-verify"
echo ""
echo "For more information, see docs/PRE_COMMIT_SETUP.md"

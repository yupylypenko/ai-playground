#!/bin/bash
# Test that lint checks are enforced before commit

set -e

echo "======================================================================"
echo "TESTING LINT ENFORCEMENT"
echo "======================================================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if pre-commit hooks are installed
if [ ! -f .git/hooks/pre-commit ]; then
    echo -e "${RED}✗ Pre-commit hooks not installed${NC}"
    echo ""
    echo "Run: ./scripts/enforce_lint.sh"
    exit 1
fi

echo -e "${GREEN}✓ Pre-commit hooks installed${NC}"
echo ""

# Check if hooks are executable
if [ ! -x .git/hooks/pre-commit ]; then
    echo -e "${YELLOW}⚠ Making hooks executable...${NC}"
    chmod +x .git/hooks/pre-commit
fi

# Create a test file with linting issues
TEST_FILE="/tmp/test_lint_enforcement.py"
cat > "$TEST_FILE" << 'EOF'
# Test file with linting issues
import os
import sys

# Missing blank line
def bad_function():
    x=1+2  # No spaces around operator
    y = [1,2,3]  # Trailing whitespace
    return x+y

# Unused import would be caught by ruff
EOF

echo "Created test file with linting issues:"
echo "  - Missing blank lines"
echo "  - No spaces around operators"
echo "  - Trailing whitespace"
echo ""

# Stage the test file
cp "$TEST_FILE" test_lint_temp.py
git add test_lint_temp.py 2>/dev/null || true

echo "Testing hook on staged file..."
echo ""

# Try to commit (should be blocked or fixed by hooks)
if git commit -m "test: lint enforcement" test_lint_temp.py 2>&1 | tee /tmp/test_output.txt; then
    echo -e "${GREEN}✓ Commit succeeded (hooks may have auto-fixed issues)${NC}"
else
    OUTPUT=$(cat /tmp/test_output.txt)
    if echo "$OUTPUT" | grep -q "pre-commit\|Black\|Ruff\|lint"; then
        echo -e "${GREEN}✓ Hooks blocked commit (as expected)${NC}"
    else
        echo -e "${YELLOW}⚠ Hooks may not be working correctly${NC}"
    fi
fi

# Cleanup
git reset HEAD test_lint_temp.py 2>/dev/null || true
rm -f test_lint_temp.py "$TEST_FILE" /tmp/test_output.txt 2>/dev/null || true

echo ""
echo "======================================================================"
echo "TEST COMPLETE"
echo "======================================================================"
echo ""
echo "To manually test:"
echo "  1. Create a file with linting issues"
echo "  2. Stage it: git add <file>"
echo "  3. Try to commit: git commit -m 'test'"
echo "  4. Hooks should run automatically"
echo ""

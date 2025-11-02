# Pre-commit Hooks Setup Guide

This guide explains how to set up and use pre-commit hooks to ensure code quality before commits.

## What are Pre-commit Hooks?

Pre-commit hooks run automatically before each commit to check your code for:
- Code formatting (Black)
- Linting (Ruff, flake8)
- Type checking (MyPy)
- Security issues (Bandit)
- Import sorting (isort)
- File quality checks
- And more!

## Quick Setup

### 1. Install Pre-commit

```bash
# Install via pip
pip install pre-commit

# Or via requirements
pip install -r requirements-dev.txt
```

### 2. Install Hooks

```bash
# Install git hooks
pre-commit install

# Also install commit message hook (optional)
pre-commit install --hook-type commit-msg
```

### 3. Test It Works

```bash
# Test on all files
pre-commit run --all-files

# Test on staged files only (automatic on commit)
pre-commit run
```

## Available Hooks

### Code Formatting
- **Black**: Automatically formats Python code
  - Line length: 88 characters
  - Auto-fixes formatting issues

- **Ruff Format**: Additional formatter (faster)

### Linting
- **Ruff**: Fast Python linter (replaces flake8)
  - Checks for errors, style issues
  - Auto-fixes common problems
  - Rules: E,F,W,I,UP,PL,PT,B,SIM,ISC,PERF,COM,ANN

- **Flake8**: Traditional Python linter (optional)

### Type Checking
- **MyPy**: Static type checker
  - Validates type hints
  - Checks for type errors
  - Only runs on `src/` directory

### Security
- **Bandit**: Security vulnerability scanner
  - Checks for common security issues
  - Excludes test files

### Import Sorting
- **isort**: Sorts Python imports
  - Black-compatible profile
  - Groups imports correctly

### File Quality
- **Trailing Whitespace**: Removes trailing spaces
- **End of File**: Ensures files end with newline
- **Large Files**: Prevents committing files >500KB
- **Merge Conflicts**: Prevents committing conflict markers
- **YAML/JSON/TOML**: Validates syntax
- **Shell Scripts**: Lints with shellcheck

### Documentation
- **Markdownlint**: Lints Markdown files
- **YAMLlint**: Lints YAML files

## Usage

### Automatic (Recommended)

Hooks run automatically when you commit:

```bash
git add .
git commit -m "feat: add new feature"
# Pre-commit hooks run automatically
```

If checks fail, fix the issues and commit again.

### Manual

Run hooks manually:

```bash
# Run on all files
pre-commit run --all-files

# Run on specific files
pre-commit run --files src/simulator/physics.py

# Run specific hook
pre-commit run black --all-files
pre-commit run ruff --all-files
```

### Skip Hooks (Not Recommended)

Skip hooks if absolutely necessary:

```bash
git commit --no-verify -m "emergency fix"
```

**Warning**: Only skip hooks in emergencies!

## Configuration

### Customize Hooks

Edit `.pre-commit-config.yaml` to:
- Add/remove hooks
- Change hook versions
- Modify hook arguments
- Add custom hooks

### Example: Add Custom Hook

```yaml
- repo: local
  hooks:
    - id: my-custom-check
      name: My Custom Check
      entry: ./scripts/my_check.sh
      language: system
      files: \.py$
```

### Update Hooks

Update all hooks to latest versions:

```bash
pre-commit autoupdate
```

## Integration with CI/CD

The CI pipeline also runs pre-commit checks:

```yaml
# In .github/workflows/ci.yml
- name: Run pre-commit
  run: |
    pip install pre-commit
    pre-commit run --all-files
```

This ensures consistency between local and CI.

## Troubleshooting

### Hooks Not Running

**Problem**: Hooks don't run on commit

**Solution**:
```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install

# Verify installation
ls -la .git/hooks/pre-commit
```

### Hook Takes Too Long

**Problem**: Pre-commit slows down commits

**Solution**:
1. Hooks only run on changed files by default
2. Use `SKIP` environment variable:
   ```bash
   SKIP=black git commit -m "temp commit"
   ```
3. Optimize hook configuration

### Hook Fails But Code Looks Fine

**Problem**: Hook fails on apparently correct code

**Solution**:
```bash
# See detailed error
pre-commit run --verbose

# Run specific hook to debug
pre-commit run black --all-files -v
```

### Update Hook Issues

**Problem**: Hook version incompatible

**Solution**:
```bash
# Update all hooks
pre-commit autoupdate

# Or update specific hook in .pre-commit-config.yaml
```

### Permission Issues

**Problem**: Can't run hooks

**Solution**:
```bash
# Check permissions
chmod +x .git/hooks/pre-commit

# Reinstall hooks
pre-commit install --install-hooks
```

## Best Practices

1. **Always install hooks**: Run `pre-commit install` after clone
2. **Run before push**: Test with `pre-commit run --all-files`
3. **Fix issues locally**: Don't skip hooks unless emergency
4. **Keep hooks updated**: Run `pre-commit autoupdate` regularly
5. **Use in CI**: Ensure CI also runs pre-commit checks

## Excluded Files

These files/directories are excluded:
- `.git/`
- `venv/`, `.venv/`
- `__pycache__/`
- `.pytest_cache/`
- `.mypy_cache/`
- `dist/`, `build/`
- `*.pyc`, `*.pyo`

## Example Workflow

```bash
# 1. Install pre-commit (one time)
pip install pre-commit
pre-commit install

# 2. Make changes
vim src/simulator/physics.py

# 3. Stage changes
git add src/simulator/physics.py

# 4. Commit (hooks run automatically)
git commit -m "feat: add gravity calculation"

# If hooks fail:
# - Fix issues automatically (Black, isort, ruff --fix)
# - Fix issues manually (type errors, security issues)
# - Stage fixes
git add .
git commit -m "feat: add gravity calculation"
```

## Hook Details

### Black (Formatting)
- **What**: Formats Python code
- **Auto-fix**: Yes
- **Time**: Fast (< 1 second)

### Ruff (Linting)
- **What**: Fast Python linter
- **Auto-fix**: Yes (with --fix)
- **Time**: Very fast (< 1 second)
- **Replaces**: flake8, pylint, isort (formatting mode)

### MyPy (Type Checking)
- **What**: Validates type hints
- **Auto-fix**: No (requires code changes)
- **Time**: Moderate (5-10 seconds)

### Bandit (Security)
- **What**: Security vulnerability scanner
- **Auto-fix**: No
- **Time**: Moderate (2-5 seconds)

### isort (Import Sorting)
- **What**: Sorts and groups imports
- **Auto-fix**: Yes
- **Time**: Fast (< 1 second)

## Additional Resources

- [Pre-commit Documentation](https://pre-commit.com/)
- [Black Documentation](https://black.readthedocs.io/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [MyPy Documentation](https://mypy.readthedocs.io/)
- [Bandit Documentation](https://bandit.readthedocs.io/)

---

**Last Updated**: November 2024

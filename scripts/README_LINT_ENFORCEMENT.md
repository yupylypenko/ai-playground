# Lint Enforcement Guide

Quick guide to enforce lint checks locally before every commit.

## Quick Setup (One Command)

```bash
./scripts/enforce_lint.sh
```

This will:
1. Install pre-commit if needed
2. Install all lint hooks
3. Configure git hooks to run automatically
4. Test that everything works

## What Gets Enforced

When you commit, these checks run automatically:

### Code Formatting
- ✅ **Black**: Formats Python code (line length 88)
- ✅ **Ruff Format**: Additional formatting

### Linting
- ✅ **Ruff**: Fast Python linter (replaces flake8)
- ✅ **Shellcheck**: Shell script linting
- ✅ **Markdownlint**: Markdown linting
- ✅ **YAMLlint**: YAML linting

### Type Checking
- ✅ **MyPy**: Static type checking

### Security
- ✅ **Bandit**: Security vulnerability scanning

### Import Management
- ✅ **isort**: Sorts and groups imports

### File Quality
- ✅ Trailing whitespace removal
- ✅ End of file fixer
- ✅ Large file check (>500KB)
- ✅ Merge conflict detection
- ✅ YAML/JSON/TOML validation
- ✅ No debug statements (pdb, print debugging)

## How It Works

### Automatic (Recommended)

Hooks run automatically on commit:

```bash
git add .
git commit -m "feat: add feature"
# Pre-commit hooks run automatically!
```

If hooks fail:
- Fix the issues
- Stage fixes: `git add .`
- Commit again: `git commit -m "feat: add feature"`

### Manual Testing

Test hooks manually:

```bash
# Test on all files
pre-commit run --all-files

# Test on specific files
pre-commit run --files src/simulator/physics.py

# Test specific hook
pre-commit run black --all-files
```

### Skip Hooks (Not Recommended)

Only skip in emergencies:

```bash
git commit --no-verify -m "emergency fix"
```

**Warning**: Only use `--no-verify` in true emergencies!

## Verification

### Check if hooks are installed:

```bash
ls -la .git/hooks/pre-commit
```

Should show: `.git/hooks/pre-commit` (symlink to pre-commit)

### Test enforcement:

```bash
./scripts/test_lint_enforcement.sh
```

## Troubleshooting

### Hooks Not Running

**Problem**: Hooks don't run on commit

**Solution**:
```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install --install-hooks

# Or run setup script
./scripts/enforce_lint.sh
```

### Hook Takes Too Long

**Problem**: Hooks slow down commits

**Solution**:
1. Hooks only run on changed files (by default)
2. Use `SKIP` to skip specific hooks:
   ```bash
   SKIP=bandit git commit -m "temp"
   ```

### Hook Fails But Code Looks Fine

**Problem**: Hook fails on apparently correct code

**Solution**:
```bash
# See detailed error
pre-commit run --verbose

# Run specific hook to debug
pre-commit run black --all-files -v
```

### Pre-commit Not Found

**Problem**: `pre-commit: command not found`

**Solution**:
```bash
# Install pre-commit
pip install pre-commit

# Or use requirements
pip install -r requirements-dev.txt

# Add to PATH if needed
export PATH=$HOME/.local/bin:$PATH
```

## Integration with IDE

### VS Code

Install "Pre-commit" extension:
1. Open VS Code
2. Extensions (Ctrl+Shift+X)
3. Search for "Pre-commit"
4. Install

### PyCharm

Pre-commit hooks work automatically if installed via:
```bash
pre-commit install
```

## Best Practices

1. ✅ **Always install hooks** after cloning
2. ✅ **Run `pre-commit run --all-files`** before pushing
3. ✅ **Fix issues locally** before committing
4. ✅ **Don't skip hooks** unless emergency
5. ✅ **Keep hooks updated**: `pre-commit autoupdate`

## Expected Behavior

### On Commit

```bash
$ git commit -m "feat: add feature"
[INFO] Initializing environment for https://github.com/psf/black.
[INFO] Installing environment for https://github.com/psf/black.
[INFO] Once installed this environment will be reused.
[INFO] This may take a few minutes...
black....................................................................Passed
ruff.....................................................................Passed
mypy.....................................................................Passed
[feature/add-ci-pipeline abc1234] feat: add feature
```

### If Hooks Fail

```bash
$ git commit -m "feat: add feature"
black....................................................................Failed
- hook id: black
- files were modified by this hook

files were modified by this hook
```

**What to do**:
1. Stage the auto-fixed files: `git add .`
2. Commit again: `git commit -m "feat: add feature"`

## Files

- `.pre-commit-config.yaml` - Pre-commit configuration
- `scripts/enforce_lint.sh` - Setup script
- `scripts/test_lint_enforcement.sh` - Test script
- `docs/PRE_COMMIT_SETUP.md` - Detailed documentation

## Additional Resources

- [Pre-commit Documentation](https://pre-commit.com/)
- [Black Documentation](https://black.readthedocs.io/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [MyPy Documentation](https://mypy.readthedocs.io/)

---

**Last Updated**: November 2024

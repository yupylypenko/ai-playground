# Python 3.12 Migration Guide

## Overview

This document describes the migration of the Cosmic Flight Simulator backend
from Python 3.11 to Python 3.12, including version-specific differences,
deprecated APIs, and syntax changes.

## Migration Date

**Date**: 2024
**From**: Python 3.11
**To**: Python 3.12

## Key Changes

### 1. Type Hint Syntax Modernization

#### Before (Python 3.11)

```python
from typing import Optional, List, Dict

def get_user(user_id: str) -> Optional[User]:
    ...

users: List[User] = []
data: Dict[str, Any] = {}
```

#### After (Python 3.12)

```python
# No imports needed for basic types

def get_user(user_id: str) -> User | None:
    ...

users: list[User] = []
data: dict[str, Any] = {}
```

**Changes Made**:

- `Optional[T]` → `T | None` (PEP 604)
- `List[T]` → `list[T]` (PEP 585)
- `Dict[K, V]` → `dict[K, V]` (PEP 585)
- Removed unnecessary `typing` imports for built-in types

**Files Updated**:

- `src/models.py`
- `src/api/app.py`
- `src/api/errors.py`
- `src/cockpit/services.py`
- `src/cockpit/memory.py`
- `src/simulator/solar_system.py`
- And other files throughout the codebase

### 2. Configuration Updates

#### CI/CD Pipeline

- **File**: `.github/workflows/ci.yml`
- **Change**: Updated `PYTHON_VERSION` from `'3.11'` to `'3.12'`

#### Project Configuration

- **File**: `.cursorrules`
- **Change**: Updated language requirement from `Python 3.11+` to `Python 3.12+`

#### Documentation

- **File**: `docs/SETUP.md`
- **Change**: Updated minimum Python version from `3.8 or higher` to `3.12 or higher`

### 3. Python 3.12 Features Available

#### Improved Error Messages

Python 3.12 includes enhanced error messages that provide better context for debugging. No code changes required - benefits are automatic.

#### Performance Improvements

- Faster startup time
- Improved performance for many built-in functions
- Better memory efficiency

#### New Features (Available but not yet used)

- **Type Parameter Syntax** (PEP 695): Can be used for generic classes
  and functions
- **Improved f-string parsing**: Better error messages for f-strings
- **Enhanced traceback formatting**: More readable error traces

### 4. Deprecated APIs

#### None Deprecated in This Migration

No APIs used in this codebase were deprecated between Python 3.11 and 3.12.
The migration focused on modernizing type hints to use the newer syntax.

### 5. Breaking Changes

#### None

This migration maintains full backward compatibility. All changes are
syntactic improvements that don't affect runtime behavior.

### 6. Dependencies

#### No Changes Required

All dependencies in `requirements.txt` are compatible with Python 3.12:

- `fastapi>=0.110.0` ✓
- `numpy>=1.20.0` ✓
- `pygame>=2.0.0` ✓
- `pymongo>=4.0.0` ✓
- `PyOpenGL>=3.1.0` ✓
- All other dependencies ✓

### 7. Testing

#### Verification Steps

1. **Type Checking**: Run `mypy src/` and `pyright src/` to verify type hints
2. **Linting**: Run `ruff check src/` to ensure code style compliance
3. **Tests**: Run `pytest` to verify all tests pass
4. **CI Pipeline**: Verify GitHub Actions passes with Python 3.12

#### Test Results

- ✅ All type hints migrated successfully
- ✅ No breaking changes introduced
- ✅ All existing tests pass
- ✅ CI pipeline updated and verified

### 8. Migration Checklist

- [x] Update CI/CD pipeline to use Python 3.12
- [x] Update project documentation
- [x] Migrate `Optional[T]` to `T | None`
- [x] Migrate `List[T]` to `list[T]`
- [x] Migrate `Dict[K, V]` to `dict[K, V]`
- [x] Remove unnecessary `typing` imports
- [x] Verify all tests pass
- [x] Update documentation

### 9. Benefits of Migration

1. **Modern Syntax**: Uses Python 3.12's built-in type hint syntax
2. **Better Performance**: Python 3.12 includes performance improvements
3. **Improved Error Messages**: Enhanced debugging experience
4. **Future-Proof**: Aligns with latest Python standards
5. **Cleaner Code**: Less verbose type hints, fewer imports

### 10. Rollback Plan

If issues arise, rollback steps:

1. Revert CI configuration: Change `PYTHON_VERSION` back to `'3.11'`
2. Revert type hints: Use `git revert` or manually change back
3. Re-add `typing` imports where needed

**Note**: The type hint changes are purely syntactic and don't affect runtime, so rollback is safe.

### 11. Future Considerations

#### Potential Future Migrations

- **Type Parameter Syntax** (PEP 695): Consider using for generic classes
- **Exception Groups** (PEP 654): For better exception handling
- **Structural Pattern Matching**: Already available, consider for complex conditionals

### 12. References

- [Python 3.12 Release Notes](https://docs.python.org/3.12/whatsnew/3.12.html)
- [PEP 604 - Allow writing union types as X | Y](https://peps.python.org/pep-0604/)
- [PEP 585 - Type Hinting Generics In Standard Collections](https://peps.python.org/pep-0585/)
- [PEP 695 - Type Parameter Syntax](https://peps.python.org/pep-0695/)

## Summary

The migration to Python 3.12 was primarily a modernization of type hint
syntax. All changes are backward-compatible and improve code readability
without affecting functionality. The codebase now uses modern Python 3.12
syntax while maintaining full compatibility with existing functionality.

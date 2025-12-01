## Summary
Migrate backend from Python 3.11 to Python 3.12 with modern type hint syntax

## Changes
- ✅ Updated Python version requirement from 3.11 to 3.12
- ✅ Migrated type hints to modern syntax (Optional[T] → T | None, etc.)
- ✅ Removed unnecessary typing imports
- ✅ Updated CI/CD pipeline configuration
- ✅ Updated project documentation
- ✅ Added comprehensive migration guide

## Type of Change
- [x] Refactoring
- [x] Documentation update
- [x] Configuration change

## Description

### What Changed?

**Python Version Update:**
- CI/CD pipeline now uses Python 3.12
- Project requirements updated to Python 3.12+
- Setup documentation reflects new minimum version

**Type Hint Modernization:**
- `Optional[T]` → `T | None` (PEP 604)
- `List[T]` → `list[T]` (PEP 585)
- `Dict[K, V]` → `dict[K, V]` (PEP 585)
- Removed unnecessary `typing` module imports

**Files Modified:**
- `.cursorrules` - Updated Python version requirement
- `.github/workflows/ci.yml` - Updated CI Python version
- `docs/SETUP.md` - Updated minimum Python version
- `src/models.py` - Migrated type hints
- `src/api/app.py` - Migrated type hints
- `src/api/errors.py` - Migrated type hints
- `src/cockpit/services.py` - Migrated type hints
- `src/cockpit/memory.py` - Migrated type hints
- `src/simulator/solar_system.py` - Migrated type hints

**Documentation Added:**
- `docs/PYTHON_3_12_MIGRATION.md` - Comprehensive migration guide

### Why These Changes?

- **Modern Syntax**: Uses Python 3.12's built-in type hint syntax
- **Better Performance**: Python 3.12 includes performance improvements
- **Improved Error Messages**: Enhanced debugging experience
- **Future-Proof**: Aligns with latest Python standards
- **Cleaner Code**: Less verbose type hints, fewer imports

### How to Test?

1. **Verify Python Version:**
   ```bash
   python --version  # Should show Python 3.12.x
   ```

2. **Run Type Checking:**
   ```bash
   mypy src/
   pyright src/
   ```

3. **Run Linting:**
   ```bash
   ruff check src/
   black --check src/
   ```

4. **Run Tests:**
   ```bash
   pytest
   ```

5. **Verify CI Pipeline:**
   - Check that GitHub Actions passes with Python 3.12
   - Verify all checks pass

## Screenshots/Demo

N/A - Code refactoring with no visual changes

## Checklist
- [x] Code follows project style guidelines
- [x] Self-review completed
- [x] Documentation updated
- [x] No breaking changes
- [x] All tests pass
- [x] Type checking passes
- [x] Linting passes

## Related Issues
N/A - Proactive modernization

## Additional Notes

**Migration Benefits:**
- All changes are backward-compatible
- No runtime behavior changes
- Improved code readability
- Better IDE support with modern syntax
- Access to Python 3.12 performance improvements

**Rollback Plan:**
If issues arise, the changes can be easily reverted as they are purely
syntactic. The type hint changes don't affect runtime behavior.

**Future Considerations:**
- Consider using Type Parameter Syntax (PEP 695) for generic classes
- Explore Exception Groups (PEP 654) for better error handling
- Evaluate Structural Pattern Matching for complex conditionals

See `docs/PYTHON_3_12_MIGRATION.md` for detailed migration notes and
references.


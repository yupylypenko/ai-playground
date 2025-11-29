# Edge Cases for POST /missions Endpoint

This document identifies non-obvious edge cases for the mission creation endpoint that should be tested to ensure robust error handling and correct behavior.

## Overview

The `POST /missions` endpoint allows creating missions either from scratch or from a project template. It has complex validation logic, optional field handling, and template inheritance behavior that can lead to subtle bugs.

## Non-Obvious Edge Cases

### 1. **Project Template with Null/Empty Objectives**

**Scenario**: Creating a mission from a project template that has an empty `objectives` array or `null` objectives.

**Why it's non-obvious**: The code assumes project objectives exist and iterates over them. An empty list might create a mission with no objectives, which could be valid but unexpected.

**Expected Behavior**:

- Mission should be created successfully with empty objectives list
- No errors should occur during objective conversion

**Test Case**:

```python
def test_create_mission_from_project_with_empty_objectives():
    """Test creating mission from project with empty objectives array."""
    # Project has objectives: []
    # Mission should be created with objectives: []
```

---

### 2. **Conflicting Fields: project_id + objectives Provided**

**Scenario**: Request includes both `project_id` (to use template) AND `objectives` array.

**Why it's non-obvious**: Documentation says objectives are "ignored" when using project_id, but the code still processes them before discarding. This could lead to:

- Unnecessary processing overhead
- Potential validation errors from objectives that won't be used
- Confusion about which objectives are actually used

**Expected Behavior**:

- Objectives from request should be silently ignored
- Mission should use objectives from project template
- No validation errors should occur for request objectives

**Test Case**:

```python
def test_create_mission_with_project_id_and_objectives_conflict():
    """Test that objectives are ignored when project_id is provided."""
    # Request has both project_id and objectives
    # Mission should use project objectives, not request objectives
```

---

### 3. **Extremely Large start_position Values (Near Float Limits)**

**Scenario**: `start_position` contains values near Python float limits (e.g., `1e308`, `-1e308`).

**Why it's non-obvious**: While validation checks `ge=0.0` for `max_fuel`, there's no explicit validation on position coordinates. Extremely large values could:

- Cause overflow in physics calculations
- Break distance calculations
- Create missions that are impossible to navigate

**Expected Behavior**:

- Should either validate reasonable position bounds (e.g., within solar system scale)
- Or gracefully handle overflow in downstream systems

**Test Case**:

```python
def test_create_mission_with_extreme_start_position():
    """Test mission creation with near-limit float values for position."""
    # start_position: [1e300, 1e300, 1e300]
    # Should either validate or handle gracefully
```

---

### 4. **Project Template Belongs to Different User (Access Control)**

**Scenario**: User A tries to create a mission from User B's private project template.

**Why it's non-obvious**: The code checks if project exists but may not verify:

- If project is public (if private, should only be accessible to owner)
- If current user has permission to use the project
- Cross-user access control

**Expected Behavior**:

- Should check project visibility (public vs private)
- Should verify user has access to the project
- Should return 403 Forbidden or 404 Not Found appropriately

**Test Case**:

```python
def test_create_mission_from_other_users_private_project():
    """Test creating mission from another user's private project."""
    # User A tries to use User B's private project
    # Should return 403 or 404
```

---

### 5. **Circular Reference: Project References Itself**

**Scenario**: A project's `objectives` contain a reference to the same project ID (if objectives support project references).

**Why it's non-obvious**: While objectives may not directly reference projects, if the system evolves to support nested project references, this could create infinite loops during mission creation.

**Expected Behavior**:

- Should detect and prevent circular references
- Should return validation error if circular reference detected

**Test Case**:

```python
def test_create_mission_with_circular_project_reference():
    """Test handling of circular project references (future-proofing)."""
    # Project A references Project A in objectives
    # Should detect and prevent infinite loop
```

---

### 6. **Concurrent Mission Creation with Same Name**

**Scenario**: Two users simultaneously create missions with identical names.

**Why it's non-obvious**: Mission names might not be unique constraints, but if they are used for display/identification, duplicate names could cause:

- UI confusion
- Ambiguity in mission selection
- Potential data integrity issues

**Expected Behavior**:

- Should allow duplicate names (if not enforced)
- Or should enforce uniqueness and return conflict error
- Should handle race conditions gracefully

**Test Case**:

```python
def test_concurrent_mission_creation_same_name():
    """Test concurrent creation of missions with identical names."""
    # Two requests with same name at same time
    # Should handle race condition appropriately
```

---

### 7. **Unicode and Special Characters in Text Fields**

**Scenario**: Mission name/description contains:

- Emoji (🚀🌌)
- Unicode characters (中文, العربية)
- Control characters (\n, \t, \r)
- SQL injection attempts ('; DROP TABLE--')
- XSS attempts (<script>alert('xss')</script>)

**Why it's non-obvious**: Text fields may not properly sanitize or handle special characters, leading to:

- Database errors
- Display issues
- Security vulnerabilities
- Encoding problems

**Expected Behavior**:

- Should sanitize or escape special characters
- Should preserve valid Unicode
- Should prevent injection attacks
- Should handle control characters appropriately

**Test Case**:

```python
def test_create_mission_with_special_characters():
    """Test mission creation with Unicode, emoji, and special characters."""
    # name: "🚀 Mars Mission 中文"
    # description: "Land on <script>alert('xss')</script> Mars"
    # Should handle safely
```

---

### 8. **Time Limit Zero vs None Distinction**

**Scenario**: Request includes `time_limit: 0.0` vs `time_limit: null`.

**Why it's non-obvious**: Zero and null have different semantic meanings:

- `0.0` might mean "no time limit" or "instant failure"
- `null` clearly means "no time limit"
- The code may not distinguish between these cases

**Expected Behavior**:

- Should clarify if `0.0` is valid (instant failure) or should be treated as `null`
- Should document the distinction clearly

**Test Case**:

```python
def test_create_mission_with_zero_time_limit():
    """Test mission creation with time_limit = 0.0 vs None."""
    # time_limit: 0.0 should either be rejected or mean instant failure
    # time_limit: None should mean no time limit
```

---

### 9. **Allowed Ship Types with Invalid/Non-existent Types**

**Scenario**: `allowed_ship_types` contains ship type identifiers that don't exist in the system (e.g., `["unicorn", "dragon"]`).

**Why it's non-obvious**: The code accepts any string list without validating against known ship types. This could:

- Create missions that are impossible to start
- Cause runtime errors when selecting ships
- Lead to confusing error messages later

**Expected Behavior**:

- Should validate ship types against known types
- Should return validation error for invalid types
- Or should allow any types and validate at mission start

**Test Case**:

```python
def test_create_mission_with_invalid_ship_types():
    """Test mission creation with non-existent ship type identifiers."""
    # allowed_ship_types: ["unicorn", "dragon"]
    # Should validate or document that validation happens later
```

---

### 10. **Objective Position with NaN or Infinity**

**Scenario**: Objective `position` contains `float('nan')` or `float('inf')`.

**Why it's non-obvious**: Python allows NaN and Infinity as float values, but they can break:

- Distance calculations
- Physics simulations
- Database storage (some DBs reject NaN)

**Expected Behavior**:

- Should validate that position values are finite numbers
- Should reject NaN and Infinity values
- Should return validation error

**Test Case**:

```python
def test_create_mission_with_nan_infinity_in_objectives():
    """Test mission creation with NaN/Infinity in objective positions."""
    # position: [float('nan'), 0.0, 0.0]
    # Should reject with validation error
```

---

### 11. **Project Template Deleted Between Check and Use**

**Scenario**: Race condition where project exists when checked but is deleted before mission creation completes.

**Why it's non-obvious**: The code checks project existence, but if another request deletes it between the check and use, the mission creation could fail with unclear error.

**Expected Behavior**:

- Should handle project deletion gracefully
- Should return clear error message
- Should use transaction/isolation to prevent race condition

**Test Case**:

```python
def test_create_mission_project_deleted_during_creation():
    """Test handling when project is deleted between check and use."""
    # Thread 1: Check project exists
    # Thread 2: Delete project
    # Thread 1: Try to create mission
    # Should handle gracefully
```

---

### 12. **Very Long Lists: 1000+ Objectives or Ship Types**

**Scenario**: Request contains extremely large arrays (e.g., 10,000 objectives or ship types).

**Why it's non-obvious**: No explicit limits on array sizes could lead to:

- Performance degradation
- Memory exhaustion
- Timeout errors
- Database query issues

**Expected Behavior**:

- Should enforce reasonable limits (e.g., max 100 objectives)
- Should return validation error for excessive sizes
- Should document maximum limits

**Test Case**:

```python
def test_create_mission_with_excessive_objectives():
    """Test mission creation with extremely large objectives array."""
    # objectives: [10000 objective objects]
    # Should reject or enforce limit
```

---

## Summary

These edge cases cover:

- **Null/Empty handling**: Empty objectives, null values
- **Conflicting inputs**: project_id + objectives
- **Boundary values**: Float limits, zero vs null
- **Access control**: Cross-user project access
- **Concurrency**: Race conditions, concurrent requests
- **Security**: Injection attacks, special characters
- **Data validation**: Invalid ship types, NaN/Infinity
- **Performance**: Large arrays, resource limits
- **Future-proofing**: Circular references

Each edge case should have corresponding test coverage to ensure the endpoint handles these scenarios correctly.

# Missions API Documentation

## Overview

The Missions API allows authenticated users to create and manage mission
instances. Missions can be created from scratch or from project templates,
providing flexibility in mission configuration and execution.

## Endpoints

### POST /missions

Create a new mission instance.

**Authentication**: Required (Bearer token)

**Request Body**:

```json
{
  "name": "Mars Landing Mission",
  "description": "Land safely on Mars surface",
  "mission_type": "challenge",
  "difficulty": "intermediate",
  "target_body_id": "mars",
  "start_position": [0.0, 0.0, 0.0],
  "max_fuel": 1500.0,
  "time_limit": 3600.0,
  "allowed_ship_types": ["explorer", "cargo"],
  "failure_conditions": ["Out of fuel", "Collision detected"],
  "objectives": [
    {
      "description": "Reach Mars orbit",
      "type": "reach",
      "target_id": "mars",
      "position": [100.0, 200.0, 300.0]
    }
  ]
}
```

**Required Fields**:

- `name` (string, 1-100 characters): Mission name/title
- `description` (string, 1-1000 characters): Mission description
- `mission_type` (string): One of `"tutorial"`, `"free_flight"`,
  `"challenge"`
- `difficulty` (string): One of `"beginner"`, `"intermediate"`,
  `"advanced"`

**Optional Fields**:

- `project_id` (string, nullable): Project template ID to create mission
  from. If provided, mission inherits all configuration from the project
  (except name which can be overridden). The `objectives` field is ignored
  when using a project template.
- `target_body_id` (string, nullable): Target celestial body ID
- `start_position` (array[float, float, float]): Initial position (x, y, z)
  in meters. Default: `[0.0, 0.0, 0.0]`
- `max_fuel` (float, >= 0): Maximum fuel capacity in liters.
  Default: `1000.0`
- `time_limit` (float, >= 0, nullable): Time limit in seconds
- `allowed_ship_types` (array[string]): List of permitted ship type
  identifiers. Default: `[]`
- `failure_conditions` (array[string]): List of failure condition
  descriptions. Default: `[]`
- `objectives` (array[ObjectiveCreate]): List of mission objectives.
  Ignored if `project_id` is provided. Default: `[]`

**Objective Fields**:

- `description` (string, 1-500 characters): Objective description
- `type` (string): Objective type - `"reach"`, `"collect"`, `"maintain"`,
  or `"avoid"`. Default: `"reach"`
- `target_id` (string, nullable): Optional target body/ship ID
- `position` (array[float, float, float], nullable): Optional target
  position (x, y, z)

**Response** (201 Created):

```json
{
  "mission_id": "mission-abc123",
  "name": "Mars Landing Mission",
  "description": "Land safely on Mars surface",
  "mission_type": "challenge",
  "difficulty": "intermediate",
  "status": "not_started",
  "target_body_id": "mars",
  "start_position": [0.0, 0.0, 0.0],
  "max_fuel": 1500.0,
  "time_limit": 3600.0,
  "allowed_ship_types": ["explorer", "cargo"],
  "failure_conditions": ["Out of fuel", "Collision detected"],
  "objectives": [
    {
      "id": "obj-xyz789",
      "description": "Reach Mars orbit",
      "type": "reach",
      "target_id": "mars",
      "position": [100.0, 200.0, 300.0],
      "completed": false
    }
  ],
  "objectives_completed": 0,
  "elapsed_time": 0.0,
  "distance_traveled": 0.0,
  "fuel_consumed": 0.0,
  "estimated_time": 3600.0
}
```

**Error Responses**:

- `400 Bad Request`: Invalid request data
  - `VALIDATION_MISSION_TYPE_INVALID`: Invalid mission type
  - `VALIDATION_DIFFICULTY_INVALID`: Invalid difficulty level
  - `VALIDATION_INVALID_FORMAT`: Invalid field format or empty name

- `401 Unauthorized`: Authentication required or invalid token
  - `AUTH_INVALID_TOKEN`: Invalid or missing token
  - `AUTH_EXPIRED_TOKEN`: Token has expired

- `404 Not Found`: Resource not found
  - `RESOURCE_NOT_FOUND`: Project template not found (if `project_id`
    provided)

- `422 Unprocessable Entity`: Validation error from Pydantic
  - Field validation errors (e.g., string length, numeric ranges)

## Creating Missions

### From Scratch

Create a mission with all fields specified:

```bash
curl -X POST "http://localhost:8000/missions" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mars Landing Mission",
    "description": "Land safely on Mars surface",
    "mission_type": "challenge",
    "difficulty": "intermediate",
    "target_body_id": "mars",
    "max_fuel": 1500.0,
    "objectives": [
      {
        "description": "Reach Mars orbit",
        "type": "reach",
        "target_id": "mars"
      }
    ]
  }'
```

### From Project Template

Create a mission from an existing project template:

```bash
curl -X POST "http://localhost:8000/missions" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Mars Mission",
    "description": "Custom mission",
    "mission_type": "challenge",
    "difficulty": "intermediate",
    "project_id": "project-abc123"
  }'
```

When creating from a project template:

- All configuration (fuel, time limits, ship types, etc.) is inherited
  from the project
- Objectives from the project are automatically converted to mission
  objectives
- The mission name can be customized (overrides project name)
- The `objectives` field in the request is ignored

## Data Model

### Mission

A mission represents an executable mission instance with the following
structure:

- **Identity**: `mission_id`, `name`, `description`
- **Configuration**: `mission_type`, `difficulty`, `target_body_id`,
  `start_position`, `max_fuel`, `time_limit`
- **Constraints**: `allowed_ship_types`, `failure_conditions`
- **Objectives**: List of mission objectives with completion status
- **Tracking**: `status`, `objectives_completed`, `elapsed_time`,
  `distance_traveled`, `fuel_consumed`, `estimated_time`

### Mission Types

- `tutorial`: Educational missions for learning
- `free_flight`: Open-ended exploration missions
- `challenge`: Competitive missions with specific goals

### Difficulty Levels

- `beginner`: Suitable for new players
- `intermediate`: Moderate challenge
- `advanced`: High difficulty missions

### Mission Status

- `not_started`: Mission created but not yet started
- `in_progress`: Mission is currently active
- `completed`: Mission successfully completed
- `failed`: Mission failed due to failure conditions

### Objective Types

- `reach`: Navigate to a target location or body
- `collect`: Gather resources or samples
- `maintain`: Sustain a condition (e.g., orbit, speed)
- `avoid`: Prevent specific events or conditions

## Best Practices

1. **Project Templates**: Use project templates for reusable mission
   configurations
2. **Objectives**: Order objectives logically for sequential completion
3. **Constraints**: Set realistic fuel and time limits based on mission
   complexity
4. **Naming**: Use descriptive, clear mission names
5. **Validation**: Ensure all required fields are provided and valid

## Error Handling

All errors follow the standardized API error format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "field_name",
      "value": "invalid_value"
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "path": "/missions"
  }
}
```

See [API_ERROR_HANDLING.md](./API_ERROR_HANDLING.md) for complete error code
reference.

## Improvements Over Previous Endpoint

This endpoint implementation includes several improvements:

1. **Error Mapping Helpers**: Reusable error mapping functions reduce code
   duplication
2. **Project Template Support**: Create missions from existing project
   templates
3. **Better Code Organization**: Cleaner separation of concerns with helper
   functions
4. **Comprehensive Validation**: Enhanced validation with clear error
   messages
5. **Efficient Testing**: Better organized tests with parametrized test
   cases

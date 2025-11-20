# Projects API Documentation

## Overview

The Projects API allows authenticated users to create, manage, and share
custom mission project templates. Projects serve as reusable mission
configurations that define objectives, constraints, and parameters for space
simulation missions.

## Endpoints

### POST /projects

Create a new mission project template.

**Authentication**: Required (Bearer token)

**Request Body**:

```json
{
  "name": "Mars Exploration Mission",
  "description": "A challenging mission to reach Mars orbit",
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
  ],
  "is_public": false
}
```

**Required Fields**:

- `name` (string, 1-100 characters): Project name/title
- `description` (string, 1-1000 characters): Project description
- `mission_type` (string): One of `"tutorial"`, `"free_flight"`,
  `"challenge"`
- `difficulty` (string): One of `"beginner"`, `"intermediate"`,
  `"advanced"`

**Optional Fields**:

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
- `objectives` (array[ObjectiveTemplate]): List of objective templates.
  Default: `[]`
- `is_public` (boolean): Whether project is publicly shareable.
  Default: `false`

**Objective Template Fields**:

- `description` (string, 1-500 characters): Objective description
- `type` (string): Objective type - `"reach"`, `"collect"`, `"maintain"`,
  or `"avoid"`. Default: `"reach"`
- `target_id` (string, nullable): Optional target body/ship ID
- `position` (array[float, float, float], nullable): Optional target
  position (x, y, z)

**Response** (201 Created):

```json
{
  "project_id": "project-abc123",
  "user_id": "user-123",
  "name": "Mars Exploration Mission",
  "description": "A challenging mission to reach Mars orbit",
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
  ],
  "is_public": false,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
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

- `422 Unprocessable Entity`: Validation error from Pydantic
  - Field validation errors (e.g., string length, numeric ranges)

## Examples

### Minimal Project

```bash
curl -X POST "http://localhost:8000/projects" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Simple Tutorial",
    "description": "A basic tutorial mission",
    "mission_type": "tutorial",
    "difficulty": "beginner"
  }'
```

### Complete Project with Objectives

```bash
curl -X POST "http://localhost:8000/projects" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jupiter Exploration",
    "description": "Journey to Jupiter with multiple objectives",
    "mission_type": "challenge",
    "difficulty": "advanced",
    "target_body_id": "jupiter",
    "start_position": [50.0, 100.0, 150.0],
    "max_fuel": 2000.0,
    "time_limit": 7200.0,
    "allowed_ship_types": ["explorer", "cargo", "fighter"],
    "failure_conditions": [
      "Out of fuel",
      "Collision detected",
      "Time limit exceeded"
    ],
    "objectives": [
      {
        "description": "Reach Jupiter orbit",
        "type": "reach",
        "target_id": "jupiter"
      },
      {
        "description": "Collect atmospheric samples",
        "type": "collect",
        "target_id": "jupiter"
      },
      {
        "description": "Maintain stable orbit for 10 minutes",
        "type": "maintain",
        "position": [500.0, 600.0, 700.0]
      }
    ],
    "is_public": true
  }'
```

## Data Model

### Project

A project represents a reusable mission template with the following structure:

- **Identity**: `id`, `user_id`, `name`, `description`
- **Configuration**: `mission_type`, `difficulty`, `target_body_id`,
  `start_position`, `max_fuel`, `time_limit`
- **Constraints**: `allowed_ship_types`, `failure_conditions`
- **Objectives**: List of objective templates
- **Visibility**: `is_public`
- **Metadata**: `created_at`, `updated_at`

### Mission Types

- `tutorial`: Educational missions for learning
- `free_flight`: Open-ended exploration missions
- `challenge`: Competitive missions with specific goals

### Difficulty Levels

- `beginner`: Suitable for new players
- `intermediate`: Moderate challenge
- `advanced`: High difficulty missions

### Objective Types

- `reach`: Navigate to a target location or body
- `collect`: Gather resources or samples
- `maintain`: Sustain a condition (e.g., orbit, speed)
- `avoid`: Prevent specific events or conditions

## Best Practices

1. **Naming**: Use descriptive, clear project names
2. **Descriptions**: Provide detailed mission descriptions
3. **Objectives**: Order objectives logically (sequential completion)
4. **Constraints**: Set realistic fuel and time limits
5. **Public Projects**: Only mark projects as public if they're well-tested and documented

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
    "path": "/projects"
  }
}
```

See [API_ERROR_HANDLING.md](./API_ERROR_HANDLING.md) for complete error code
reference.

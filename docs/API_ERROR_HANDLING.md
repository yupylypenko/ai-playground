# API Error Handling Policy

## Overview

This document defines the error handling strategy for the Cosmic Flight
Simulator API. All API endpoints follow a consistent error response format
to provide clear, actionable feedback to clients.

## Error Response Format

All error responses follow a standardized JSON structure:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "Additional context or field-specific errors"
    },
    "timestamp": "2025-01-15T10:30:00Z",
    "path": "/api/v1/register"
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `error.code` | string | Machine-readable error code (see Error Codes section) |
| `error.message` | string | Human-readable error message |
| `error.details` | object | Optional additional context (field errors, etc.) |
| `error.timestamp` | string | ISO 8601 timestamp of when the error occurred |
| `error.path` | string | API endpoint path where the error occurred |

## HTTP Status Codes

The API uses standard HTTP status codes to indicate the type of error:

| Status Code | Meaning | Usage |
|-------------|---------|-------|
| `400` | Bad Request | Invalid input, validation errors, malformed requests |
| `401` | Unauthorized | Authentication required or failed |
| `403` | Forbidden | Authenticated but insufficient permissions |
| `404` | Not Found | Resource does not exist |
| `409` | Conflict | Resource conflict (e.g., duplicate username) |
| `422` | Unprocessable Entity | Valid format but semantic errors |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Internal Server Error | Unexpected server errors |
| `503` | Service Unavailable | Service temporarily unavailable |

## Error Codes

Error codes are hierarchical and follow the pattern: `CATEGORY_SUBCATEGORY_SPECIFIC`

### Authentication Errors (`AUTH_*`)

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `AUTH_REQUIRED` | 401 | Authentication required but not provided |
| `AUTH_INVALID_TOKEN` | 401 | Invalid or malformed JWT token |
| `AUTH_EXPIRED_TOKEN` | 401 | JWT token has expired |
| `AUTH_INVALID_CREDENTIALS` | 401 | Invalid username or password |
| `AUTH_USER_NOT_FOUND` | 401 | User associated with token not found |

### Validation Errors (`VALIDATION_*`)

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_REQUIRED` | 400 | Required field is missing |
| `VALIDATION_INVALID_FORMAT` | 400 | Field format is invalid |
| `VALIDATION_OUT_OF_RANGE` | 400 | Value is outside allowed range |
| `VALIDATION_PASSWORD_POLICY` | 400 | Password does not meet policy |
| `VALIDATION_EMAIL_INVALID` | 400 | Email address format is invalid |
| `VALIDATION_USERNAME_INVALID` | 400 | Username format is invalid |

### Resource Errors (`RESOURCE_*`)

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `RESOURCE_NOT_FOUND` | 404 | Requested resource does not exist |
| `RESOURCE_ALREADY_EXISTS` | 409 | Resource with same identifier exists |
| `RESOURCE_CONFLICT` | 409 | Resource state conflict |

### Server Errors (`SERVER_*`)

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `SERVER_INTERNAL_ERROR` | 500 | Unexpected internal server error |
| `SERVER_TOKEN_GENERATION_FAILED` | 500 | Failed to generate auth token |
| `SERVER_DATABASE_ERROR` | 500 | Database operation failed |
| `SERVER_SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |

## Error Handling Implementation

### Global Exception Handlers

The API uses FastAPI exception handlers to catch and format errors consistently:

1. **HTTPException Handler**: Formats FastAPI HTTPExceptions with error codes
2. **ValidationError Handler**: Formats Pydantic validation errors
3. **Generic Exception Handler**: Catches unexpected errors and returns 500

### Route-Level Error Handling

Routes should:

1. **Use specific error codes**: Always include an error code when raising errors
2. **Provide context**: Include relevant details in the `details` field
3. **Log errors**: Log all errors with appropriate severity levels
4. **Preserve stack traces**: Log full stack traces for debugging (not in response)

### Example Usage

```python
from src.api.errors import APIError, ErrorCode

# In a route handler
if not user:
    raise APIError(
        code=ErrorCode.AUTH_INVALID_CREDENTIALS,
        message="Invalid username or password",
        status_code=401
    )

# With field validation details
raise APIError(
    code=ErrorCode.VALIDATION_PASSWORD_POLICY,
    message="Password does not meet requirements",
    details={"requirements": ["min_length: 8", "mixed_case", "digit_required"]},
    status_code=400
)
```

## Error Response Examples

### Authentication Error

```json
{
  "error": {
    "code": "AUTH_INVALID_TOKEN",
    "message": "Invalid or expired token",
    "details": null,
    "timestamp": "2025-01-15T10:30:00Z",
    "path": "/api/v1/me"
  }
}
```

### Validation Error

```json
{
  "error": {
    "code": "VALIDATION_PASSWORD_POLICY",
    "message": "Password does not meet requirements",
    "details": {
      "field": "password",
      "requirements": [
        "Minimum 8 characters",
        "Must contain mixed case letters",
        "Must contain at least one digit"
      ]
    },
    "timestamp": "2025-01-15T10:30:00Z",
    "path": "/api/v1/register"
  }
}
```

### Resource Conflict

```json
{
  "error": {
    "code": "RESOURCE_ALREADY_EXISTS",
    "message": "Username already registered",
    "details": {
      "field": "username",
      "value": "existing_user"
    },
    "timestamp": "2025-01-15T10:30:00Z",
    "path": "/api/v1/register"
  }
}
```

### Internal Server Error

```json
{
  "error": {
    "code": "SERVER_INTERNAL_ERROR",
    "message": "An unexpected error occurred",
    "details": null,
    "timestamp": "2025-01-15T10:30:00Z",
    "path": "/api/v1/login"
  }
}
```

## Best Practices

1. **Be Specific**: Use the most specific error code available
2. **Be Helpful**: Provide actionable error messages
3. **Be Secure**: Don't leak sensitive information (passwords, tokens, internal paths)
4. **Be Consistent**: Always use the standardized error format
5. **Log Everything**: Log errors with full context for debugging
6. **Document Changes**: Update this document when adding new error codes

## Error Code Registry

When adding new error codes:

1. Add the code to the `ErrorCode` enum in `src/api/errors.py`
2. Document it in this file with HTTP status and description
3. Update route handlers to use the new code
4. Add tests for the new error scenario

## Migration Notes

For existing endpoints:

- All `HTTPException` calls should be migrated to use `APIError` with error codes
- Validation errors should use appropriate `VALIDATION_*` codes
- Authentication errors should use `AUTH_*` codes
- Resource errors should use `RESOURCE_*` codes

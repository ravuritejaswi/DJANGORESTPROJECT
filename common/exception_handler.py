from rest_framework.views import exception_handler
from rest_framework.exceptions import (
    ValidationError,
    NotAuthenticated,
    AuthenticationFailed,
    PermissionDenied,
    NotFound,
    MethodNotAllowed,
    Throttled,
)


def custom_exception_handler(exc, context):
    # Let DRF generate the standard response first
    response = exception_handler(exc, context)

    # If DRF cannot handle the exception, return None
    # Django will handle unexpected server errors normally.
    if response is None:
        return None

    # Default values
    message = "An error occurred"
    error_code = "API_ERROR"

    # Validation errors
    if isinstance(exc, ValidationError):
        message = "Validation failed"
        error_code = "VALIDATION_ERROR"

    # Authentication errors
    elif isinstance(exc, NotAuthenticated):
        message = "Authentication credentials were not provided"
        error_code = "AUTHENTICATION_REQUIRED"

    elif isinstance(exc, AuthenticationFailed):
        message = "Invalid authentication credentials"
        error_code = "INVALID_CREDENTIALS"

    # Permission errors
    elif isinstance(exc, PermissionDenied):
        message = "You do not have permission to perform this action"
        error_code = "PERMISSION_DENIED"

    # Not found
    elif isinstance(exc, NotFound):
        message = "Resource not found"
        error_code = "NOT_FOUND"

    # Method not allowed
    elif isinstance(exc, MethodNotAllowed):
        message = "HTTP method is not allowed"
        error_code = "METHOD_NOT_ALLOWED"

    # Throttling
    elif isinstance(exc, Throttled):
        message = "Request limit exceeded. Please try again later"
        error_code = "THROTTLED"

    # Use DRF's detail message for other handled exceptions
    else:
        detail = response.data.get("detail")

        if detail:
            message = str(detail)

        error_code = "API_ERROR"

    response.data = {
        "success": False,
        "message": message,
        "error_code": error_code,
    }

    return response
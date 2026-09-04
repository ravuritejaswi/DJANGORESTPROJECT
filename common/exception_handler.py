import logging

from rest_framework.views import exception_handler


logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        logger.error(
            "API error: %s | View: %s",
            str(exc),
            context.get("view").__class__.__name__
            if context.get("view")
            else "Unknown",
        )

        response.data = {
            "success": False,
            "message": "Something went wrong.",
            "error_code": "API_ERROR",
            "data": response.data,
        }

    return response
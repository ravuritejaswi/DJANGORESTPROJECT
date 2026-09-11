import logging
import time
import uuid

from django.utils.deprecation import MiddlewareMixin


logger = logging.getLogger("api")
SLOW_API_THRESHOLD = 1.0

class StructuredLoggingMiddleware(MiddlewareMixin):

    def process_request(self, request):
        # Create a unique ID for every incoming request
        request.request_id = str(uuid.uuid4())

        # Store start time for execution-time calculation
        request.start_time = time.perf_counter()

        # Allow an existing correlation ID to be reused
        correlation_id = request.headers.get("X-Correlation-ID")

        if correlation_id:
            request.correlation_id = correlation_id
        else:
            request.correlation_id = request.request_id

    def process_response(self, request, response):
        start_time = getattr(
            request,
            "start_time",
            time.perf_counter(),
        )

        execution_time = time.perf_counter() - start_time

        request_id = getattr(
            request,
            "request_id",
            "N/A",
        )

        correlation_id = getattr(
            request,
            "correlation_id",
            request_id,
        )

        user_id = "anonymous"

        if hasattr(request, "user") and request.user.is_authenticated:
            user_id = str(request.user.id)

        # Return the request ID to the client
        response["X-Request-ID"] = request_id
        response["X-Correlation-ID"] = correlation_id

        logger.info(
            "API Request | "
            "request_id=%s | "
            "correlation_id=%s | "
            "user_id=%s | "
            "method=%s | "
            "endpoint=%s | "
            "status_code=%s | "
            "execution_time=%.3fs",
            request_id,
            correlation_id,
            user_id,
            request.method,
            request.path,
            response.status_code,
            execution_time,
        )
        if execution_time >= SLOW_API_THRESHOLD:
                logger.warning(
                    "Slow API | "
                    "request_id=%s | "
                    "correlation_id=%s | "
                    "user_id=%s | "
                    "method=%s | "
                    "endpoint=%s | "
                    "status_code=%s | "
                    "execution_time=%.3fs",
                    request_id,
                    correlation_id,
                    user_id,
                    request.method,
                    request.path,
                    response.status_code,
                    execution_time,
                )

        return response

    def process_exception(self, request, exception):
        start_time = getattr(
            request,
            "start_time",
            time.perf_counter(),
        )

        execution_time = time.perf_counter() - start_time

        request_id = getattr(
            request,
            "request_id",
            "N/A",
        )

        correlation_id = getattr(
            request,
            "correlation_id",
            request_id,
        )

        user_id = "anonymous"

        if hasattr(request, "user") and request.user.is_authenticated:
            user_id = str(request.user.id)

        logger.error(
            "API Error | "
            "request_id=%s | "
            "correlation_id=%s | "
            "user_id=%s | "
            "method=%s | "
            "endpoint=%s | "
            "execution_time=%.3fs | "
            "error=%s",
            request_id,
            correlation_id,
            user_id,
            request.method,
            request.path,
            execution_time,
            str(exception),
            exc_info=True,
        )

        return None
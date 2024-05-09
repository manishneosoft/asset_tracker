import logging
import time

class RequestLoggingMiddleware:
    """Logging middleware for Django HTTP requests."""

    def __init__(self, get_response):
        """
        Initialize the request logging middleware.

        :param get_response: The WSGI application.
        """
        self.get_response = get_response
        self.logger = logging.getLogger(__name__)

    def __call__(self, request):
        """
        Log request details and return the response.

        :param request: The HTTP request.
        :return: The HTTP response.
        """
        start_time = time.time()

        response = self.get_response(request)

        # Log request details
        self.logger.info(
            "%s %s - Status: %s Elapsed Time: %.2fs",
            request.method,
            request.path,
            response.status_code,
            time.time() - start_time,
        )

        return response

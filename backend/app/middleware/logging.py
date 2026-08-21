import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware

from backend.app.core.request_context import request_id_context
from backend.app.observability.metrics import (
    ACTIVE_REQUESTS,
    REQUEST_COUNT,
    REQUEST_DURATION,
)

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = str(uuid.uuid4())
        token = request_id_context.set(request_id)

        start = time.perf_counter()

        ACTIVE_REQUESTS.inc()

        logger.info(
            "%s %s started",
            request.method,
            request.url.path,
        )

        response = None

        try:
            response = await call_next(request)
            return response

        finally:
            duration = time.perf_counter() - start

            REQUEST_DURATION.labels(
                request.method,
                request.url.path,
            ).observe(duration)

            REQUEST_COUNT.labels(
                request.method,
                request.url.path,
                response.status_code if response else 500,
            ).inc()

            ACTIVE_REQUESTS.dec()

            logger.info(
                "%s %s completed status=%s duration_ms=%.2f",
                request.method,
                request.url.path,
                response.status_code if response else 500,
                duration * 1000,
            )

            if response:
                response.headers["X-Request-ID"] = request_id

            request_id_context.reset(token)

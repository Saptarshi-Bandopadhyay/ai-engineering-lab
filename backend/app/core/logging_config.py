import logging
import sys

import structlog
from pythonjsonlogger.json import JsonFormatter

from backend.app.core.config import settings
from backend.app.core.request_context import request_id_context


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_context.get()
        return True


def setup_logging():
    log_level = logging.DEBUG if settings.debug else logging.INFO

    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)

    if settings.environment == "development":
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(request_id)s | %(name)s | %(message)s"
        )
    else:
        formatter = JsonFormatter(
            "%(asctime)s %(levelname)s %(request_id)s %(name)s %(message)s"
        )

    handler.setFormatter(formatter)
    handler.addFilter(RequestIdFilter())

    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)

    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    return logging.getLogger("backend")

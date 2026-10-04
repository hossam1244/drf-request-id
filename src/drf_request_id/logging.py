"""Logging integration: a filter that attaches the current request ID to
every record, and a ready-made LOGGING fragment."""

import logging


class RequestIDLogFilter(logging.Filter):
    """Adds ``request_id`` to records from inside a request.

    Usage::

        LOGGING = {
            ...,
            "formatters": {
                "request": {
                    "format": "%(asctime)s [%(request_id)s] %(name)s %(levelname)s %(message)s"
                }
            },
            "filters": {
                "request_id": {"()": "drf_request_id.logging.RequestIDLogFilter"}
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "filters": ["request_id"],
                    "formatter": "request",
                }
            },
        }
    """

    def filter(self, record: logging.LogRecord) -> bool:
        # Imported lazily so the middleware module isn't pulled at import time
        # in settings-less contexts.
        from drf_request_id.middleware import get_request_id

        record.request_id = get_request_id() or "-"
        return True

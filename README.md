# drf-request-id

**Request-ID middleware for Django & DRF** — generate or accept an ID per
request, propagate it through your stack via a `ContextVar`, and echo it on
the response so every log line, error report, and support ticket correlates.

[![CI](https://github.com/hossam1244/drf-request-id/actions/workflows/ci.yml/badge.svg)](https://github.com/hossam1244/drf-request-id/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/badge/pypi-0.1.0-blue)](https://pypi.org/project/drf-request-id/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Why

When a user reports "the app returned 500", the first question is *which
request*. A request ID answers it — if it exists, survives your whole stack,
and lands in the logs next to every message. The pieces people assemble by
hand (middleware + logging filter + header echo + context propagation) are
exactly what this package is:

* **Honors upstream IDs** — load balancers/gateways that already set
  `X-Request-ID` keep theirs (sanitized: safe charset, length-capped, header
  injection impossible).
* **ContextVar propagation** — views, services, and anything spawned with the
  request's context see the ID via `get_request_id()`, no parameter threading.
* **Reset discipline** — the var is set and reset around the request, so
  worker reuse can't leak one request's ID into the next.
* **Logging filter included** — one line in `LOGGING` puts the ID on every
  record.
* **Response echo** — clients and support tickets get the same ID back.

## Install

```bash
pip install drf-request-id   # (PyPI soon; until then: pip install git+https://github.com/hossam1244/drf-request-id.git)
```

```python
MIDDLEWARE = [
    "drf_request_id.middleware.RequestIDMiddleware",  # as high as possible
    ...
]
```

Logs:

```python
LOGGING = {
    "version": 1,
    "filters": {
        "request_id": {"()": "drf_request_id.logging.RequestIDLogFilter"},
    },
    "formatters": {
        "request": {
            "format": "%(asctime)s [%(request_id)s] %(name)s %(levelname)s %(message)s"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "filters": ["request_id"],
            "formatter": "request",
        },
    },
    "root": {"handlers": ["console"], "level": "INFO"},
}
```

Anywhere in request scope:

```python
from drf_request_id.middleware import get_request_id

logger.info("payment settled", extra={"request": get_request_id()})
```

## Testing

8 tests: UUID generation and header echo, upstream-ID acceptance, ContextVar
visibility inside views, injection-attempt sanitization, request-object
attribute, ContextVar reset after the request, logging-filter attachment
inside a request, and the outside-request `-` fallback.

```bash
pip install -e . && pytest
```

## License

[MIT](LICENSE)

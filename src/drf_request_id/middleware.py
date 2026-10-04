"""Request-ID middleware: generate or accept, propagate via contextvar,
and echo on the response."""

import contextvars
import uuid
from typing import Final

from django.http import HttpRequest, HttpResponse

#: The contextvar everything else reads. Django processes a request on a
#: single thread/async task, so a ContextVar carries the ID through views,
#: services, and Celery tasks spawned with the request's context — without
#: passing it as a parameter everywhere.
request_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "request_id", default=None
)

DEFAULT_HEADER: Final = "X-Request-ID"
RESPONSE_HEADER: Final = "X-Request-ID"


def get_request_id() -> str | None:
    """The current request's ID (None outside a request)."""
    return request_id_var.get()


def _sanitize(value: str) -> str | None:
    """Accept only safe characters — the ID is echoed into headers and logs."""
    cleaned = value.strip()
    if not cleaned or len(cleaned) > 200:
        return None
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.")
    if not set(cleaned) <= allowed:
        return None
    return cleaned


class RequestIDMiddleware:
    """Assigns every request an ID and echoes it on the response.

    * Incoming ``X-Request-ID`` (configurable) is honored when it looks safe —
      load balancers and API gateways often generate one upstream.
    * Otherwise a UUID is generated.
    * The ID is stored in a ContextVar for the request's duration and copied
      into the response header so clients and support tickets can correlate.

    Order matters: place it as high in ``MIDDLEWARE`` as possible so
    everything downstream (including exception logging) sees the ID.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        raw = request.headers.get(DEFAULT_HEADER, "")
        request_id = _sanitize(raw) or str(uuid.uuid4())

        request.request_id = request_id  # type: ignore[attr-defined]
        token = request_id_var.set(request_id)
        try:
            response = self.get_response(request)
        finally:
            request_id_var.reset(token)
        response[RESPONSE_HEADER] = request_id
        return response

    async def __acall__(self, request: HttpRequest) -> HttpResponse:
        raw = request.headers.get(DEFAULT_HEADER, "")
        request_id = _sanitize(raw) or str(uuid.uuid4())

        request.request_id = request_id  # type: ignore[attr-defined]
        token = request_id_var.set(request_id)
        try:
            response = await self.get_response(request)
        finally:
            request_id_var.reset(token)
        response[RESPONSE_HEADER] = request_id
        return response

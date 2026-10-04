import logging
import re

import pytest
from django.http import JsonResponse
from django.test import RequestFactory

from drf_request_id.logging import RequestIDLogFilter
from drf_request_id.middleware import RequestIDMiddleware, get_request_id

pytestmark = pytest.mark.django_db


def test_response_carries_generated_request_id(client):
    response = client.get("/echo")

    assert response.status_code == 200
    assert re.match(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        response["X-Request-ID"],
    )


def test_incoming_request_id_is_honored(client):
    response = client.get("/echo", headers={"X-Request-ID": "abc-123"})

    assert response["X-Request-ID"] == "abc-123"
    assert response.json()["request_id"] == "abc-123"


def test_contextvar_visible_inside_the_view(client):
    response = client.get("/echo", headers={"X-Request-ID": "ctx-42"})

    assert response.json()["request_id"] == "ctx-42"


def test_unsafe_incoming_ids_are_replaced(client):
    response = client.get(
        "/echo",
        headers={"X-Request-ID": "bad\r\ninjected: header"},
    )

    assert response["X-Request-ID"] != "bad\r\ninjected: header"
    assert re.match(r"^[0-9a-f-]{36}$", response["X-Request-ID"])


def test_request_object_and_response_expose_the_id():
    request = RequestFactory(HTTP_X_REQUEST_ID="req-obj-7").get("/echo")
    response = RequestIDMiddleware(lambda r: JsonResponse({}))(request)

    assert request.request_id == "req-obj-7"
    assert response["X-Request-ID"] == "req-obj-7"


def test_contextvar_is_reset_after_the_request():
    request = RequestFactory(HTTP_X_REQUEST_ID="reset-me").get("/echo")
    RequestIDMiddleware(lambda r: JsonResponse({}))(request)

    assert get_request_id() is None


def test_logging_filter_attaches_request_id_inside_a_request():
    records: list[logging.LogRecord] = []

    class Capture(logging.Handler):
        def emit(self, record):
            records.append(record)

    logger = logging.getLogger("test.request.id")
    handler = Capture()
    handler.addFilter(RequestIDLogFilter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    def view(request):
        logger.info("hello from inside")
        return JsonResponse({})

    RequestIDMiddleware(view)(
        RequestFactory(HTTP_X_REQUEST_ID="log-9").get("/echo"),
    )

    assert records, "log record emitted inside the request"
    assert records[0].request_id == "log-9"


def test_filter_outside_request_emits_dash():
    record = logging.LogRecord("x", logging.INFO, __file__, 1, "msg", (), None)
    RequestIDLogFilter().filter(record)
    assert record.request_id == "-"
